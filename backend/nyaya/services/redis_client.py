from __future__ import annotations

from typing import Optional

import redis.asyncio as redis_async
from redis import Redis as SyncRedis

from nyaya.config.settings import get_settings

settings = get_settings()

_sync: Optional[SyncRedis] = None
_async_client: Optional[redis_async.Redis] = None


def get_redis_sync() -> SyncRedis:
    global _sync
    if _sync is None:
        _sync = SyncRedis.from_url(settings.redis_url, decode_responses=True)
    return _sync


def get_redis_async() -> redis_async.Redis:
    global _async_client
    if _async_client is None:
        _async_client = redis_async.Redis.from_url(settings.redis_url, decode_responses=True)
    return _async_client


def ping_sync() -> bool:
    try:
        return bool(get_redis_sync().ping())
    except Exception:
        return False


async def ping_async() -> bool:
    try:
        return bool(await get_redis_async().ping())
    except Exception:
        return False
