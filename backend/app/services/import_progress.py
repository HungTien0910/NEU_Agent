from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

from app.db.redis import get_redis

_memory_store: Dict[str, Dict[str, Any]] = {}
_TTL_SECONDS = 3600


def _make_payload(
    job_id: str,
    status: str,
    percent: int,
    step: str,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "job_id": job_id,
        "status": status,
        "percent": int(percent),
        "step": step,
        "error": error,
        "updated_at": int(time.time()),
    }


def set_progress(
    job_id: str, status: str, percent: int, step: str, error: Optional[str] = None
) -> Dict[str, Any]:
    payload = _make_payload(job_id, status, percent, step, error)
    client = get_redis()
    if client:
        client.setex(f"import_progress:{job_id}", _TTL_SECONDS, json.dumps(payload))
    else:
        _memory_store[job_id] = payload
    return payload


def get_progress(job_id: str) -> Optional[Dict[str, Any]]:
    client = get_redis()
    if client:
        raw = client.get(f"import_progress:{job_id}")
        if not raw:
            return None
        return json.loads(raw)
    return _memory_store.get(job_id)


def clear_progress(job_id: str) -> None:
    client = get_redis()
    if client:
        client.delete(f"import_progress:{job_id}")
    else:
        _memory_store.pop(job_id, None)
