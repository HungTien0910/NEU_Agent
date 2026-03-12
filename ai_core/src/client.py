from __future__ import annotations

import json
import logging
import time
import urllib.request
from urllib.error import HTTPError, URLError
from typing import Any, Dict, List, Optional

from .config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key: str, model: str, timeout: int = 60) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def call(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, Any]] = None,
        temperature: float = 0.2,
    ) -> Any:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = response_format

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        started = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)
        except HTTPError as exc:
            err_body = ""
            try:
                err_body = exc.read().decode("utf-8")
            except Exception:
                err_body = ""
            logger.error("openai_http_error status=%s body=%s", exc.code, err_body[:1000])
            raise RuntimeError(f"OpenAI HTTP {exc.code}: {err_body}") from exc
        except URLError as exc:
            logger.error("openai_url_error err=%s", str(exc))
            raise RuntimeError(f"OpenAI URL error: {exc}") from exc

        elapsed = (time.perf_counter() - started) * 1000
        usage = data.get("usage", {}) if isinstance(data, dict) else {}
        logger.info(
            "openai_call model=%s ms=%.1f prompt=%s completion=%s total=%s",
            self.model,
            elapsed,
            usage.get("prompt_tokens"),
            usage.get("completion_tokens"),
            usage.get("total_tokens"),
        )

        if "error" in data:
            raise RuntimeError(data["error"].get("message", "OpenAI API error"))

        choice = data["choices"][0]["message"]
        if response_format:
            content = choice.get("content") or "{}"
            return json.loads(content)

        return choice.get("content", "")


default_client = OpenAIClient(OPENAI_API_KEY, OPENAI_MODEL)


def call_model(
    messages: List[Dict[str, str]],
    response_format: Optional[Dict[str, Any]] = None,
    temperature: float = 0.2,
) -> Any:
    return default_client.call(messages, response_format=response_format, temperature=temperature)
