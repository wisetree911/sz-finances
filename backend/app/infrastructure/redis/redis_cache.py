from __future__ import annotations

import json
from typing import Any, Optional
from redis.asyncio import Redis


class RedisCache:
    def __init__(self, redis: Redis, *, prefix: str = 'sz'):
        self._r = redis
        self._p = prefix

    def _k(self, key: str) -> str:
        return f'{self._p}:cache:{key}'

    async def get_json(self, key: str) -> Optional[Any]:
        val = await self._r.get(self._k(key))
        return None if val is None else json.loads(val)

    async def set_json(self, key: str, payload: Any, *, ttl: int) -> None:
        await self._r.set(
            self._k(key),
            json.dumps(payload, ensure_ascii=False, default=str),
            ex=ttl,
        )

    async def delete(self, key: str) -> None:
        await self._r.delete(self._k(key))
