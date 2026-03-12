from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .client import call_model
from .router import infer_sheet
from .utils.io import read_json, read_text
from .utils.text import compact_history, normalize


BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
TEMPLATES_DIR = BASE_DIR / "templates"
logger = logging.getLogger(__name__)


class CoreAI:
    def __init__(self) -> None:
        self.data_schema = read_text(TEMPLATES_DIR / "schema.md")
        self.system_data = read_text(PROMPTS_DIR / "system_data.txt")
        self.system_chat = read_text(PROMPTS_DIR / "system_chat.txt")
        self.system_intent = read_text(PROMPTS_DIR / "system_intent.txt")
        self.data_examples = read_text(PROMPTS_DIR / "data_examples.txt")
        self.cypher_schema = read_json(TEMPLATES_DIR / "response_format.json")
        self.classify_schema = read_json(TEMPLATES_DIR / "classify_format.json")

    @staticmethod
    def is_data_question(question: str) -> bool:
        q = question.lower()
        keywords = [
            "sinh viên",
            "giảng viên",
            "môn học",
            "học phần",
            "khóa học",
            "điểm",
            "gpa",
            "khoa",
            "học kỳ",
            "nam học",
            "nhập học",
            "tuyển sinh",
            "số lượng",
            "bao nhiêu",
            "thống kê",
            "academic",
            "student",
            "lecturer",
            "course",
        ]
        return any(k in q for k in keywords)

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in response")
        snippet = text[start : end + 1]
        return json.loads(snippet)

    def classify_mode(self, question: str, lang: str = "vi") -> str:
        normalized = normalize(question)
        system = self.system_intent
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": normalized},
        ]
        preview = normalized[:160] + ("..." if len(normalized) > 160 else "")
        logger.info("coreai_intent_start lang=%s q=%s", lang, preview)
        try:
            result = call_model(messages, response_format=self.classify_schema, temperature=0)
            mode = result.get("mode", "chat")
            if mode not in ("data", "chat"):
                mode = "chat"
            logger.info(
                "coreai_intent_result mode=%s reason=%s",
                mode,
                result.get("reason"),
            )
            return mode
        except Exception as exc:
            logger.warning("coreai_intent_error err=%s", str(exc))
            try:
                raw = call_model(messages, response_format=None, temperature=0)
                parsed = self._parse_json(raw)
                mode = parsed.get("mode", "chat")
                if mode not in ("data", "chat"):
                    mode = "chat"
                logger.info("coreai_intent_fallback mode=%s", mode)
                return mode
            except Exception as fallback_exc:
                logger.warning("coreai_intent_fallback_error err=%s", str(fallback_exc))
                return "data" if self.is_data_question(normalized) else "chat"

    def build_data_prompt(
        self,
        question: str,
        lang: str,
        history: Optional[List[Dict[str, str]]] = None,
        error: str | None = None,
    ) -> List[Dict[str, str]]:
        system = self.system_data if lang == "vi" else self.system_data.replace("Bạn", "You")
        sheet = infer_sheet(question)
        user = (
            f"{self.data_schema}\n\n"
            f"Focus sheet: {sheet}\n"
            f"Question: {question}\n\n"
            f"Use these examples as guidance:\n{self.data_examples}\n"
        )
        if error:
            user += f"\nPrevious error: {error}\nPlease fix the Cypher.\n"
        messages = [{"role": "system", "content": system}]
        if history:
            messages.extend(compact_history(history, 6))
        messages.append({"role": "user", "content": user})
        return messages

    @staticmethod
    def _format_user_profile(user_profile: Optional[Dict[str, Any]]) -> str:
        if not user_profile:
            return ""
        fields = []
        for key in (
            "full_name",
            "gender",
            "birth_date",
            "phone",
            "title",
            "department",
            "role",
            "username",
        ):
            value = user_profile.get(key)
            if value:
                fields.append(f"{key}: {value}")
        if not fields:
            return ""
        return "User profile:\n" + "\n".join(f"- {item}" for item in fields)

    def generate_cypher(
        self,
        question: str,
        lang: str = "vi",
        history: Optional[List[Dict[str, str]]] = None,
        error: str | None = None,
    ) -> Dict[str, Any]:
        normalized = normalize(question)
        preview = normalized[:160] + ("..." if len(normalized) > 160 else "")
        logger.info("coreai_cypher_start lang=%s q=%s", lang, preview)
        messages = self.build_data_prompt(normalized, lang, history=history, error=error)
        try:
            result = call_model(messages, response_format=self.cypher_schema, temperature=0.2)
            if "notes" not in result:
                result["notes"] = ""
            cypher = result.get("cypher", "")
            logger.info("coreai_cypher_result len=%s", len(cypher))
            return result
        except Exception as exc:
            logger.warning("coreai_cypher_error err=%s", str(exc))
            raw = call_model(messages, response_format=None, temperature=0.2)
            parsed = self._parse_json(raw)
            if "notes" not in parsed:
                parsed["notes"] = ""
            cypher = parsed.get("cypher", "")
            logger.info("coreai_cypher_fallback len=%s", len(cypher))
            return parsed

    def chat_answer(
        self,
        question: str,
        lang: str = "vi",
        history: Optional[List[Dict[str, str]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> str:
        preview = normalize(question)
        preview = preview[:160] + ("..." if len(preview) > 160 else "")
        logger.info("coreai_chat_start lang=%s q=%s", lang, preview)
        system = self.system_chat if lang == "vi" else self.system_chat.replace("Bạn", "You")
        profile = self._format_user_profile(user_profile)
        messages = [{"role": "system", "content": system}]
        if history:
            messages.extend(compact_history(history, 6))
        user_content = normalize(question)
        if profile:
            user_content = f"{profile}\n\nQuestion: {user_content}"
        messages.append({"role": "user", "content": user_content})
        answer = call_model(messages, temperature=0.4)
        logger.info("coreai_chat_done len=%s", len(answer))
        return answer

    def summarize_answer(
        self,
        question: str,
        columns: List[str],
        rows: List[List[Any]],
        lang: str = "vi",
        history: Optional[List[Dict[str, str]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> str:
        logger.info("coreai_summarize_start cols=%s rows=%s", len(columns), len(rows))
        system = (
            "Summarize the query result for the user. "
            "Format with clear line breaks and bullet points. "
            "If there are many records, list only the first 10 and add a final line "
            "stating only a portion is shown."
        )
        if lang == "vi":
            system = (
                "Hãy tóm tắt kết quả truy vấn cho người dùng. "
                "Trình bày dễ đọc, có xuống dòng rõ ràng và dùng gạch đầu dòng. "
                "Nếu nhiều bản ghi, chỉ liệt kê 10 dòng đầu và thêm 1 dòng cuối "
                "ghi rõ là chỉ hiển thị một phần. "
                "Nếu có thông tin người dùng, hãy xưng hô phù hợp (anh/chị) "
                "nhưng không được lộ dữ liệu nhạy cảm. "
                "Chỉ nêu chi tiết cá nhân khi người dùng hỏi trực tiếp."
            )
        sample_rows = rows[:20]
        profile = self._format_user_profile(user_profile)
        user = f"Question: {question}\nColumns: {columns}\nRows: {sample_rows}\n"
        if profile:
            user = f"{profile}\n\n{user}"
        messages = [{"role": "system", "content": system}]
        if history:
            messages.extend(compact_history(history, 4))
        messages.append({"role": "user", "content": user})
        summary = call_model(messages, temperature=0.4)
        logger.info("coreai_summarize_done len=%s", len(summary))
        return summary


core_ai = CoreAI()
