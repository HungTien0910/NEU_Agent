from __future__ import annotations

import re
from typing import Dict, List, Tuple

_SYNONYM_RULES: List[Tuple[str, str]] = [
    # Negative outcomes first to avoid overwriting "khong dat" -> "dat"
    (r"\b(không\s+đạt|không\s+qua(\s+môn|\s+học\s+phần)?|trượt|rớt|fail)\b", "không đạt"),
    (r"\b(đạt|đậu|đỗ|qua(\s+môn|\s+học\s+phần)?|pass)\b", "đạt"),
    (r"\b(nữ|female)\b", "nữ"),
    (r"\b(nam|male)\b", "nam"),
]


def normalize(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    for pattern, replacement in _SYNONYM_RULES:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE | re.UNICODE)
    return cleaned


def compact_history(
    history: List[Dict[str, str]],
    limit: int = 6,
) -> List[Dict[str, str]]:
    if not history:
        return []
    return history[-limit:]
