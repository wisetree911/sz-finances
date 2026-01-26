from __future__ import annotations

from typing import cast
from fastapi import Request
from redis.asyncio import Redis

from .redis_cache import RedisCache


def get_redis(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis)


def get_cache(request: Request) -> RedisCache:
    return RedisCache(get_redis(request))
