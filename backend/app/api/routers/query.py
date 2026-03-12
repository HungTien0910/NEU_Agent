import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.history_repo import create_history
from app.repositories.user_repo import get_by_username
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import query_service

router = APIRouter(prefix="/query", tags=["query"])


def _chunk_text(text: str, size: int = 24) -> list[str]:
    if not text:
        return []
    words = text.split()
    chunks = []
    current: list[str] = []
    for word in words:
        current.append(word)
        if len(current) >= size:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


@router.post("", response_model=QueryResponse)
def query_data(payload: QueryRequest, db: Session = Depends(get_db)):
    if not payload.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiếu thông tin người dùng.",
        )

    user = get_by_username(db, payload.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng.",
        )
    permissions = [p for p in (user.permissions or "").split(",") if p]
    user_context = {
        "username": user.username,
        "full_name": user.full_name,
        "gender": user.gender,
        "title": user.title,
        "department": user.department,
        "phone": user.phone,
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "role": user.role,
    }
    result, cypher = query_service.run_query(
        payload.question,
        payload.language or "vi",
        payload.username,
        role=user.role,
        permissions=permissions,
        user_profile=user_context,
    )
    history = create_history(
        db=db,
        username=payload.username,
        question=payload.question,
        cypher=cypher,
        columns=result.get("columns", []),
        rows=result.get("rows", []),
        chart=result.get("chart"),
        summary=result.get("summary", ""),
        chart_type=(result.get("chart") or {}).get("type"),
    )

    return QueryResponse(
        id=history.id,
        columns=result.get("columns", []),
        rows=result.get("rows", []),
        chart=result.get("chart"),
        summary=result.get("summary", ""),
        cypher=cypher or None,
        is_stat=result.get("is_stat", False),
    )


@router.post("/stream")
def query_stream(payload: QueryRequest, db: Session = Depends(get_db)):
    if not payload.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiếu thông tin người dùng.",
        )

    user = get_by_username(db, payload.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng.",
        )
    permissions = [p for p in (user.permissions or "").split(",") if p]
    user_context = {
        "username": user.username,
        "full_name": user.full_name,
        "gender": user.gender,
        "title": user.title,
        "department": user.department,
        "phone": user.phone,
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "role": user.role,
    }

    def event_stream():
        try:
            result, cypher = query_service.run_query(
                payload.question,
                payload.language or "vi",
                payload.username,
                role=user.role,
                permissions=permissions,
                user_profile=user_context,
            )
            summary = result.get("summary", "")
            for chunk in _chunk_text(summary):
                yield "event: summary\n"
                yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"

            history = create_history(
                db=db,
                username=payload.username,
                question=payload.question,
                cypher=cypher,
                columns=result.get("columns", []),
                rows=result.get("rows", []),
                chart=result.get("chart"),
                summary=summary,
                chart_type=(result.get("chart") or {}).get("type"),
            )

            payload_data = {
                "id": history.id,
                "columns": result.get("columns", []),
                "rows": result.get("rows", []),
                "chart": result.get("chart"),
                "summary": summary,
                "cypher": cypher or None,
                "is_stat": result.get("is_stat", False),
            }
            yield "event: result\n"
            yield f"data: {json.dumps(payload_data, ensure_ascii=False)}\n\n"
        except Exception as exc:
            yield "event: error\n"
            yield f"data: {json.dumps({'detail': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
