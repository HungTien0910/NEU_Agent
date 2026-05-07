from __future__ import annotations

import base64
import hashlib
import json
import logging
import re
import tempfile
import textwrap
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pypdfium2 as pdfium
from app.core.config import settings
from app.db.neo4j import get_neo4j_driver
from app.services.import_progress import set_progress

logger = logging.getLogger(__name__)


@dataclass
class ChunkItem:
    chunk_id: str
    index: int
    page_start: int
    page_end: int
    content: str


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _openai_ocr_image(image_path: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("Thiếu OPENAI_API_KEY cho OCR.")
    model = settings.openai_ocr_model or settings.openai_model
    with open(image_path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("utf-8")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Bạn là OCR engine. Trả về nguyên văn toàn bộ chữ nhìn thấy trong ảnh, không giải thích.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Trích xuất toàn bộ nội dung chữ trong ảnh này."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                ],
            },
        ],
        "temperature": 0,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.openai_api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = response.read().decode("utf-8")
        data = json.loads(raw)
    text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
    return _normalize_space(text)


def _ocr_pages_text_with_llm(pdf_path: str) -> List[str]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf = pdfium.PdfDocument(pdf_path)
        if len(pdf) == 0:
            return []

        page_texts: List[str] = []
        empty_pages: List[int] = []
        for page_idx in range(len(pdf)):
            page = pdf[page_idx]
            bitmap = page.render(scale=2.0)
            pil_img = bitmap.to_pil()
            image = Path(tmp_dir) / f"page-{page_idx + 1}.png"
            pil_img.save(image, format="PNG")

            text = _openai_ocr_image(str(image))
            if not text:
                empty_pages.append(page_idx + 1)
            page_texts.append(text)

        non_empty = [t for t in page_texts if t]
        if not non_empty:
            raise RuntimeError(
                "OCR thất bại: toàn bộ trang không trích xuất được text. "
                "Kiểm tra OPENAI_API_KEY / OPENAI_OCR_MODEL (vision) hoặc chất lượng PDF."
            )

        # Cho phép vài trang rỗng, nhưng nếu rỗng quá nhiều thì báo lỗi để tránh ingest sai.
        if len(empty_pages) > len(page_texts) * 0.6:
            raise RuntimeError(
                f"OCR thất bại phần lớn trang (rỗng {len(empty_pages)}/{len(page_texts)})."
            )

        logger.info(
            "admission_ocr_done pages=%s non_empty=%s empty_pages=%s",
            len(page_texts),
            len(non_empty),
            empty_pages[:20],
        )
        return page_texts


def _extract_pages_text(pdf_bytes: bytes) -> Tuple[List[str], int]:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()
        texts = _ocr_pages_text_with_llm(tmp.name)
        return texts, len(texts)


def _chunk_by_page(page_texts: List[str]) -> List[ChunkItem]:
    chunk_words = max(60, int(settings.admission_chunk_words or 180))
    overlap_words = max(0, int(settings.admission_chunk_overlap_words or 40))
    if overlap_words >= chunk_words:
        overlap_words = max(0, chunk_words // 4)

    chunks: List[ChunkItem] = []
    chunk_index = 0
    for page_idx, text in enumerate(page_texts, start=1):
        normalized = _normalize_space(text)
        if not normalized:
            continue

        words = normalized.split(" ")
        start = 0
        while start < len(words):
            end = min(len(words), start + chunk_words)
            piece = " ".join(words[start:end]).strip()
            if piece:
                chunks.append(
                    ChunkItem(
                        chunk_id=f"chunk-{page_idx}-{chunk_index}",
                        index=chunk_index,
                        page_start=page_idx,
                        page_end=page_idx,
                        content=piece,
                    )
                )
                chunk_index += 1
            if end >= len(words):
                break
            start = max(start + 1, end - overlap_words)

    return chunks


def _openai_embeddings(texts: List[str]) -> List[List[float]]:
    if not settings.openai_api_key:
        raise RuntimeError("Thiếu OPENAI_API_KEY để tạo embedding.")
    if not texts:
        return []

    model = settings.openai_embedding_model
    dims = int(settings.openai_embedding_dimensions or 1536)
    batch_size = max(1, int(settings.admission_embedding_batch_size or 32))

    vectors: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        payload: Dict[str, Any] = {
            "model": model,
            "input": batch,
            "dimensions": dims,
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/embeddings",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.openai_api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        items = data.get("data") or []
        if len(items) != len(batch):
            raise RuntimeError("OpenAI embedding trả về thiếu vector trong batch.")
        vectors.extend([item.get("embedding") or [] for item in items])

    if len(vectors) != len(texts):
        raise RuntimeError("Số lượng embedding không khớp số lượng chunk.")
    return vectors


def import_admission_pdf(file_name: str, pdf_bytes: bytes) -> Dict[str, Any]:
    page_texts, pages = _extract_pages_text(pdf_bytes)
    chunks = _chunk_by_page(page_texts)
    if not chunks:
        raise RuntimeError("OCR có dữ liệu nhưng không tạo được chunk hợp lệ.")

    digest = hashlib.sha1(pdf_bytes).hexdigest()[:16]
    doc_id = f"admission-{digest}"
    title = _normalize_space(file_name.rsplit(".", 1)[0] if file_name else "Admission Document")

    vectors = _openai_embeddings([chunk.content for chunk in chunks])

    driver = get_neo4j_driver()
    with driver.session() as session:
        session.run(
            "CREATE CONSTRAINT document_doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.docId IS UNIQUE"
        )
        session.run(
            "CREATE CONSTRAINT chunk_chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.chunkId IS UNIQUE"
        )
        session.run(
            "CREATE FULLTEXT INDEX chunk_content_ft IF NOT EXISTS FOR (c:Chunk) ON EACH [c.content]"
        )
        try:
            session.run(
                """
                CREATE VECTOR INDEX chunk_embedding_idx IF NOT EXISTS
                FOR (c:Chunk) ON (c.embedding)
                OPTIONS {indexConfig: {
                  `vector.dimensions`: $dims,
                  `vector.similarity_function`: 'cosine'
                }}
                """,
                dims=int(settings.openai_embedding_dimensions or 1536),
            )
        except Exception as exc:
            logger.warning("vector_index_create_failed err=%s", str(exc))

        # Chỉ thay thế chunk của đúng file đang import; không đụng các Document khác.
        session.run(
            """
            MATCH (d:Document {docId: $doc_id})
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(old:Chunk)
            DETACH DELETE old
            """,
            doc_id=doc_id,
        )

        session.run(
            """
            MERGE (d:Document {docId: $doc_id})
            SET d.title = $title,
                d.source = 'admission',
                d.fileName = $file_name,
                d.pageCount = $page_count,
                d.chunkCount = $chunk_count,
                d.importedAt = datetime()
            """,
            doc_id=doc_id,
            title=title,
            file_name=file_name,
            page_count=pages,
            chunk_count=len(chunks),
        )

        rows = [
            {
                "chunk_id": chunk.chunk_id,
                "idx": chunk.index,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "content": chunk.content,
                "embedding": vectors[i],
            }
            for i, chunk in enumerate(chunks)
        ]

        session.run(
            """
            UNWIND $rows AS row
            MATCH (d:Document {docId: $doc_id})
            MERGE (c:Chunk {chunkId: row.chunk_id})
            SET c.content = row.content,
                c.pageStart = row.page_start,
                c.pageEnd = row.page_end,
                c.docId = $doc_id,
                c.embedding = row.embedding
            MERGE (d)-[r:HAS_CHUNK]->(c)
            SET r.index = row.idx
            """,
            doc_id=doc_id,
            rows=rows,
        )

        if len(rows) >= 2:
            session.run(
                """
                UNWIND range(0, size($rows)-2) AS idx
                MATCH (d:Document {docId: $doc_id})-[r1:HAS_CHUNK {index: idx}]->(c1:Chunk)
                MATCH (d)-[r2:HAS_CHUNK {index: idx + 1}]->(c2:Chunk)
                MERGE (c1)-[:NEXT]->(c2)
                """,
                doc_id=doc_id,
                rows=rows,
            )
    driver.close()

    logger.info(
        "admission_import_done doc_id=%s pages=%s chunks=%s",
        doc_id,
        pages,
        len(chunks),
    )
    return {"doc_id": doc_id, "title": title, "pages": pages, "chunks": len(chunks)}


def run_import_admission_pdf_job(job_id: str, file_name: str, pdf_bytes: bytes) -> None:
    try:
        set_progress(job_id, "running", 5, "Đang OCR tài liệu PDF")
        result = import_admission_pdf(file_name, pdf_bytes)
        set_progress(
            job_id,
            "done",
            100,
            f"Hoàn tất import PDF: {result.get('title', '')}",
        )
    except Exception as exc:
        set_progress(job_id, "error", 100, "Lỗi import PDF", str(exc))


def _openai_chat(messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
    if not settings.openai_api_key:
        return "Hệ thống AI chưa cấu hình OPENAI_API_KEY."
    payload = {
        "model": settings.openai_model,
        "messages": messages,
        "temperature": temperature,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.openai_api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    return (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()


def _normalize_scores(items: List[Dict[str, Any]], key: str) -> Dict[str, float]:
    values = [float(item.get(key) or 0.0) for item in items]
    max_val = max(values) if values else 0.0
    if max_val <= 0:
        return {item["chunk_id"]: 0.0 for item in items}
    return {item["chunk_id"]: float(item.get(key) or 0.0) / max_val for item in items}


def _hybrid_retrieve(question: str, top_k: int) -> List[Dict[str, Any]]:
    q_embedding = _openai_embeddings([question])[0]
    driver = get_neo4j_driver()
    with driver.session() as session:
        text_hits = session.run(
            """
            CALL db.index.fulltext.queryNodes('chunk_content_ft', $q, {limit: $limit})
            YIELD node, score
            MATCH (d:Document)-[:HAS_CHUNK]->(node)
            WHERE d.source = 'admission'
            RETURN d.docId AS doc_id,
                   d.title AS title,
                   node.chunkId AS chunk_id,
                   node.content AS content,
                   node.pageStart AS page_start,
                   node.pageEnd AS page_end,
                   score AS ft_score
            ORDER BY ft_score DESC
            LIMIT $limit
            """,
            q=question,
            limit=max(top_k * 3, 12),
        ).data()

        try:
            vec_hits = session.run(
                """
                CALL db.index.vector.queryNodes('chunk_embedding_idx', $limit, $embedding)
                YIELD node, score
                MATCH (d:Document)-[:HAS_CHUNK]->(node)
                WHERE d.source = 'admission'
                RETURN d.docId AS doc_id,
                       d.title AS title,
                       node.chunkId AS chunk_id,
                       node.content AS content,
                       node.pageStart AS page_start,
                       node.pageEnd AS page_end,
                       score AS vec_score
                ORDER BY vec_score DESC
                LIMIT $limit
                """,
                embedding=q_embedding,
                limit=max(top_k * 3, 12),
            ).data()
        except Exception as exc:
            logger.warning("vector_query_failed err=%s", str(exc))
            vec_hits = []
    driver.close()

    merged: Dict[str, Dict[str, Any]] = {}
    for item in text_hits:
        chunk_id = item["chunk_id"]
        merged.setdefault(chunk_id, dict(item))
        merged[chunk_id]["ft_score"] = float(item.get("ft_score") or 0.0)
    for item in vec_hits:
        chunk_id = item["chunk_id"]
        merged.setdefault(chunk_id, dict(item))
        merged[chunk_id]["vec_score"] = float(item.get("vec_score") or 0.0)

    rows = list(merged.values())
    ft_norm = _normalize_scores(rows, "ft_score")
    vec_norm = _normalize_scores(rows, "vec_score")
    w_text = float(settings.admission_hybrid_weight_text or 0.5)
    w_vec = float(settings.admission_hybrid_weight_vector or 0.5)
    if w_text < 0:
        w_text = 0.0
    if w_vec < 0:
        w_vec = 0.0
    if w_text == 0 and w_vec == 0:
        w_text = w_vec = 0.5
    total_w = w_text + w_vec
    w_text, w_vec = w_text / total_w, w_vec / total_w

    for row in rows:
        cid = row["chunk_id"]
        row["ft_norm"] = ft_norm.get(cid, 0.0)
        row["vec_norm"] = vec_norm.get(cid, 0.0)
        row["hybrid_score"] = w_text * row["ft_norm"] + w_vec * row["vec_norm"]

    rows.sort(key=lambda x: x.get("hybrid_score", 0.0), reverse=True)
    return rows[:top_k]


def query_admission(question: str, lang: str = "vi", top_k: int = 6) -> Dict[str, Any]:
    q = _normalize_space(question)
    if not q:
        return {"answer": "Vui lòng nhập câu hỏi.", "citations": [], "confidence": "low"}

    records = _hybrid_retrieve(q, top_k)
    if not records:
        return {
            "answer": "Hiện chưa có dữ liệu tuyển sinh phù hợp để trả lời. Vui lòng kiểm tra lại tài liệu đã import.",
            "citations": [],
            "confidence": "low",
        }

    max_score = float(records[0].get("hybrid_score") or 0.0)
    confidence = "high" if max_score >= 0.75 else ("medium" if max_score >= 0.45 else "low")

    context = "\n\n".join(
        [
            f"[Chunk {i + 1}] trang {r.get('page_start')}-{r.get('page_end')}\n{r.get('content')}"
            for i, r in enumerate(records)
        ]
    )

    system = (
        "Bạn là trợ lý tư vấn tuyển sinh NEU. "
        "Chỉ dùng thông tin trong CONTEXT. Nếu không đủ thông tin thì nói rõ không chắc chắn."
    )
    if lang == "en":
        system = (
            "You are an NEU admission assistant. "
            "Use only CONTEXT. If context is insufficient, explicitly say so."
        )

    user_prompt = textwrap.dedent(
        f"""
        Câu hỏi: {q}

        CONTEXT:
        {context}

        Yêu cầu:
        - Trả lời ngắn gọn, đúng nội dung trong CONTEXT.
        - Không tự thêm thông tin ngoài tài liệu.
        """
    ).strip()

    answer = _openai_chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ]
    )

    citations = [
        {
            "doc_id": r["doc_id"],
            "title": r["title"],
            "chunk_id": r["chunk_id"],
            "page_start": int(r["page_start"] or 0),
            "page_end": int(r["page_end"] or 0),
            "score": float(r.get("hybrid_score") or 0.0),
        }
        for r in records
    ]

    return {
        "answer": answer or "Không có câu trả lời phù hợp.",
        "citations": citations,
        "confidence": confidence,
        "debug": {
            "top_score": max_score,
            "hits": len(citations),
            "mode": "hybrid",
        },
    }
