from functools import wraps
import time
from redis import asyncio as aioredis
from fastapi import HTTPException, Request, status
from config import settings

class RateLimiter:
    async def init_redis(self):
        self.redis = await aioredis.from_url(settings.REDIS_HOST)

    async def is_rate_limited(self, key: str, max_requests: int, window: int) -> bool:
        if not hasattr(self, "redis"):
            await self.init_redis()

        current = int(time.time())
        window_start = current - window
        async with self.redis.pipeline(transaction=True) as pipe:
            try:
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zadd(key, {current: current})
                pipe.zcard(key)
                pipe.expire(key, window)
                results = await pipe.execute()
            except self.redis.RedisError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Redis error: {str(e)}"
                ) from e
        return results[2] > max_requests


rate_limiter = RateLimiter()


def rate_limit(max_requests: int, window: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            key = f"rate_limit:{request.client.host}:{request.url.path}"
            if await rate_limiter.is_rate_limited(key, max_requests, window):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator