from __future__ import annotations

import json
import hashlib
from typing import Any, Dict, List, Optional
from app.db.redis import get_redis


def make_cache_key(username: str, question: str) -> str:
    key = f"{username}:{question}".encode("utf-8")
    return "query:" + hashlib.sha256(key).hexdigest()


def get_cached_result(username: str, question: str) -> Optional[Dict[str, Any]]:
    client = get_redis()
    if not client:
        return None
    key = make_cache_key(username, question)
    raw = client.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def set_cached_result(
    username: str, question: str, payload: Dict[str, Any], ttl: int = 300
) -> None:
    client = get_redis()
    if not client:
        return
    key = make_cache_key(username, question)
    client.setex(key, ttl, json.dumps(payload, ensure_ascii=False))


def append_chat_history(username: str, role: str, content: str, max_items: int = 12):
    client = get_redis()
    if not client:
        return
    key = f"chat:{username}"
    payload = json.dumps({"role": role, "content": content}, ensure_ascii=False)
    client.rpush(key, payload)
    client.ltrim(key, -max_items, -1)
    client.expire(key, 60 * 60 * 6)


def get_chat_history(username: str, limit: int = 12) -> List[Dict[str, str]]:
    client = get_redis()
    if not client:
        return []
    key = f"chat:{username}"
    raw_items = client.lrange(key, -limit, -1)
    history = []
    for raw in raw_items:
        try:
            item = json.loads(raw)
            if "role" in item and "content" in item:
                history.append({"role": item["role"], "content": item["content"]})
        except Exception:
            continue
    return history
