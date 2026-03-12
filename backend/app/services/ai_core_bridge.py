from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

from app.core.config import settings


def _ensure_ai_env() -> None:
    if settings.openai_api_key and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    if settings.openai_model and not os.getenv("OPENAI_MODEL"):
        os.environ["OPENAI_MODEL"] = settings.openai_model


class AICoreBridge:
    def __init__(self) -> None:
        self._import_error: Optional[Exception] = None
        self._core_ai = None
        self._validator = None
        self._init_core()

    def _init_core(self) -> None:
        ai_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../ai_core")
        )
        if ai_root not in sys.path:
            sys.path.append(ai_root)

        try:
            _ensure_ai_env()
            from src.core import core_ai
            from src.validator import validate_cypher

            self._core_ai = core_ai
            self._validator = validate_cypher
        except Exception as exc:  # pragma: no cover
            self._import_error = exc
            self._core_ai = None
            self._validator = None

    def is_data_question(self, question: str) -> bool:
        if not self._core_ai:
            return False
        try:
            return self._core_ai.is_data_question(question)
        except Exception:
            return False

    def classify_mode(self, question: str, lang: str) -> str:
        if not self._core_ai:
            return "data"
        try:
            return self._core_ai.classify_mode(question, lang)
        except Exception:
            return "data"

    def generate_cypher(
        self,
        question: str,
        lang: str,
        history: Optional[List[Dict[str, str]]] = None,
        error: str | None = None,
    ) -> Dict[str, Any]:
        if not self._core_ai:
            raise RuntimeError(f"AI Core import error: {self._import_error}")
        return self._core_ai.generate_cypher(
            question,
            lang,
            history=history,
            error=error,
        )

    def chat_answer(
        self,
        question: str,
        lang: str,
        history: Optional[List[Dict[str, str]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not self._core_ai:
            return "Xin lỗi, hệ thống AI chưa sẵn sàng."
        try:
            return self._core_ai.chat_answer(
                question,
                lang,
                history=history,
                user_profile=user_profile,
            )
        except Exception:
            return "Xin lỗi, hệ thống AI chưa sẵn sàng."

    def summarize_answer(
        self,
        question: str,
        columns: List[str],
        rows: List[List[Any]],
        lang: str,
        history: Optional[List[Dict[str, str]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not self._core_ai:
            return "Đã có kết quả dữ liệu."
        try:
            return self._core_ai.summarize_answer(
                question,
                columns,
                rows,
                lang,
                history=history,
                user_profile=user_profile,
            )
        except Exception:
            return "Đã có kết quả dữ liệu."

    def validate_cypher(self, cypher: str) -> None:
        if not self._validator:
            return
        self._validator(cypher)


ai_core_bridge = AICoreBridge()


def is_data_question(question: str) -> bool:
    return ai_core_bridge.is_data_question(question)


def classify_mode(question: str, lang: str) -> str:
    return ai_core_bridge.classify_mode(question, lang)


def generate_cypher(question: str, lang: str) -> Dict[str, Any]:
    return ai_core_bridge.generate_cypher(question, lang)


def generate_cypher_with_context(
    question: str,
    lang: str,
    history: List[Dict[str, str]] | None = None,
    error: str | None = None,
) -> Dict[str, Any]:
    return ai_core_bridge.generate_cypher(question, lang, history=history, error=error)


def chat_answer(
    question: str,
    lang: str,
    history: List[Dict[str, str]] | None = None,
    user_profile: Optional[Dict[str, Any]] = None,
) -> str:
    return ai_core_bridge.chat_answer(
        question, lang, history=history, user_profile=user_profile
    )


def summarize_answer(
    question: str,
    columns: List[str],
    rows: List[List[Any]],
    lang: str,
    history: List[Dict[str, str]] | None = None,
    user_profile: Optional[Dict[str, Any]] = None,
) -> str:
    return ai_core_bridge.summarize_answer(
        question,
        columns,
        rows,
        lang,
        history=history,
        user_profile=user_profile,
    )


def validate_cypher(cypher: str) -> None:
    ai_core_bridge.validate_cypher(cypher)
