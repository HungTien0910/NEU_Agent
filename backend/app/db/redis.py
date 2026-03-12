from __future__ import annotations

from typing import Optional
import redis
from app.core.config import settings


_client: Optional[redis.Redis] = None


def get_redis() -> Optional[redis.Redis]:
    global _client
    if _client is None:
        try:
            _client = redis.Redis.from_url(
                settings.redis_url, decode_responses=True
            )
            _client.ping()
        except Exception:
            _client = None
    return _client
