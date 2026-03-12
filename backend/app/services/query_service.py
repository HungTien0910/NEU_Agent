from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from app.db.neo4j import get_neo4j_driver
from app.services.ai_core_bridge import (
    chat_answer,
    classify_mode,
    generate_cypher_with_context,
    summarize_answer,
    validate_cypher,
)
from app.services.cache_service import (
    append_chat_history,
    get_cached_result,
    get_chat_history,
    set_cached_result,
)


logger = logging.getLogger(__name__)


class QueryService:
    def __init__(self) -> None:
        self.logger = logger

    @staticmethod
    def _lang_text(lang: str, vi: str, en: str) -> str:
        return en if lang == "en" else vi

    @staticmethod
    def required_permission(question: str) -> Optional[str]:
        q = question.lower()
        if "sinh viên" in q or "student" in q:
            return "data:student"
        if "giảng viên" in q or "lecturer" in q:
            return "data:lecturer"
        if "môn học" in q or "học phần" in q or "khóa học" in q or "course" in q:
            return "data:course"
        if "điểm" in q or "học kỳ" in q or "academic" in q:
            return "data:academic"
        return None

    @staticmethod
    def _run_cypher(cypher: str) -> Tuple[List[str], List[List[Any]]]:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run(cypher)
            records = [record.data() for record in result]
        driver.close()
        if not records:
            return [], []
        keys = list(records[0].keys())
        rows = [[row.get(key) for key in keys] for row in records]
        return keys, rows

    @staticmethod
    def _build_chart(columns: List[str], rows: List[List[Any]]) -> Optional[Dict[str, Any]]:
        if not columns or not rows or len(columns) < 2:
            return None
        labels = [row[0] for row in rows]
        values = [row[1] for row in rows]
        has_time = False
        if labels and isinstance(labels[0], int) and 1900 <= labels[0] <= 2100:
            has_time = True
        chart_type = "line" if has_time else "bar"
        return {"type": chart_type, "labels": labels, "values": values}

    @staticmethod
    def _is_stat_query(question: str, cypher: str) -> bool:
        q = question.lower()
        if any(k in q for k in ("bao nhiêu", "thống kê", "tỷ lệ", "trung bình", "tổng")):
            return True
        cy = cypher.lower()
        return any(fn in cy for fn in ("count(", "sum(", "avg(", "min(", "max("))

    def _chat_payload(self, answer: str) -> Tuple[Dict[str, Any], str]:
        return {
            "columns": [],
            "rows": [],
            "chart": None,
            "summary": answer,
        }, ""

    def _record_chat(self, username: Optional[str], question: str, answer: str) -> None:
        if not username:
            return
        append_chat_history(username, "user", question)
        append_chat_history(username, "assistant", answer)

    def _generate_and_run(
        self,
        question: str,
        lang: str,
        history: List[Dict[str, str]],
        error: Optional[str] = None,
    ) -> Tuple[str, List[str], List[List[Any]]]:
        plan = generate_cypher_with_context(question, lang, history=history, error=error)
        cypher = plan.get("cypher", "")
        validate_cypher(cypher)
        columns, rows = self._run_cypher(cypher)
        return cypher, columns, rows

    def run_query(
        self,
        question: str,
        lang: str = "vi",
        username: Optional[str] = None,
        role: str | None = None,
        permissions: Optional[List[str]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], str]:
        started_all = time.perf_counter()
        text = question.strip()
        self.logger.info("query_start user=%s lang=%s", username, lang)
        if not text:
            return self._chat_payload(
                self._lang_text(lang, "Vui lòng nhập câu hỏi.", "Please enter a question.")
            )

        history_ctx = get_chat_history(username) if username else []
        q_preview = (text[:120] + "...") if len(text) > 120 else text

        t_classify = time.perf_counter()
        mode = classify_mode(text, lang)
        self.logger.info(
            "intent_classify mode=%s ms=%.1f user=%s q=%s",
            mode,
            (time.perf_counter() - t_classify) * 1000,
            username,
            q_preview,
        )

        if mode == "chat":
            t_chat = time.perf_counter()
            answer = chat_answer(text, lang, history=None, user_profile=user_profile)
            self.logger.info(
                "chat_answer ms=%.1f user=%s",
                (time.perf_counter() - t_chat) * 1000,
                username,
            )
            self._record_chat(username, text, answer)
            self.logger.info(
                "query_done mode=chat total_ms=%.1f",
                (time.perf_counter() - started_all) * 1000,
            )
            return self._chat_payload(answer)

        if mode == "data":
            required = self.required_permission(text)
            allowed = (
                (role == "admin")
                or not required
                or (permissions and required in permissions)
            )
            self.logger.info(
                "permission_check required=%s allowed=%s user=%s",
                required,
                allowed,
                username,
            )
            if not allowed:
                message = self._lang_text(
                    lang,
                    "Bạn không có quyền truy cập để hỏi các thông tin tại dữ liệu bảng đó.",
                    "You do not have permission to query data from that table.",
                )
                self.logger.info(
                    "query_blocked user=%s required=%s",
                    username,
                    required,
                )
                return {
                    "columns": [],
                    "rows": [],
                    "chart": None,
                    "summary": message,
                }, ""

        cached = get_cached_result(username or "", text) if username else None
        if cached:
            self.logger.info("query_cache_hit user=%s q=%s", username, q_preview)
            return cached, cached.get("cypher", "")

        try:
            t_gen = time.perf_counter()
            cypher, columns, rows = self._generate_and_run(text, lang, history_ctx)
            self.logger.info(
                "cypher_generate ms=%.1f user=%s",
                (time.perf_counter() - t_gen) * 1000,
                username,
            )
        except Exception as exc:
            try:
                t_gen = time.perf_counter()
                cypher, columns, rows = self._generate_and_run(
                    text, lang, history_ctx, error=str(exc)
                )
                self.logger.info(
                    "cypher_retry ms=%.1f user=%s err=%s",
                    (time.perf_counter() - t_gen) * 1000,
                    username,
                    str(exc),
                )
            except Exception:
                t_chat = time.perf_counter()
                answer = chat_answer(text, lang, history=None, user_profile=user_profile)
                self.logger.info(
                    "chat_fallback ms=%.1f user=%s",
                    (time.perf_counter() - t_chat) * 1000,
                    username,
                )
                self._record_chat(username, text, answer)
                self.logger.info(
                    "query_done mode=chat_fallback total_ms=%.1f",
                    (time.perf_counter() - started_all) * 1000,
                )
                return self._chat_payload(answer)

        try:
            show_stats = self._is_stat_query(text, cypher)
            chart = self._build_chart(columns, rows) if show_stats else None
            t_sum = time.perf_counter()
            summary = summarize_answer(
                text,
                columns,
                rows,
                lang,
                history_ctx,
                user_profile=user_profile,
            )
            self.logger.info(
                "summarize ms=%.1f user=%s",
                (time.perf_counter() - t_sum) * 1000,
                username,
            )
            payload = {
                "columns": columns if show_stats else [],
                "rows": rows if show_stats else [],
                "chart": chart,
                "summary": summary,
                "cypher": cypher,
                "is_stat": show_stats,
            }
            if username:
                set_cached_result(username, text, payload, ttl=300)
                self._record_chat(username, text, summary)
            self.logger.info(
                "query_done mode=data total_ms=%.1f rows=%s",
                (time.perf_counter() - started_all) * 1000,
                len(rows),
            )
            return payload, cypher
        except Exception:
            t_chat = time.perf_counter()
            answer = chat_answer(text, lang, history=None, user_profile=user_profile)
            self.logger.info(
                "chat_fallback ms=%.1f user=%s",
                (time.perf_counter() - t_chat) * 1000,
                username,
            )
            self._record_chat(username, text, answer)
            self.logger.info(
                "query_done mode=chat_fallback total_ms=%.1f",
                (time.perf_counter() - started_all) * 1000,
            )
            return self._chat_payload(answer)


query_service = QueryService()
