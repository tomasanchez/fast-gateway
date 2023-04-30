"""
FastAPI middlewares
"""
import aioredis
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS, HTTP_503_SERVICE_UNAVAILABLE

from app.adapters.redis_connector import RedisConnectionError
from app.dependencies import RedisDependency
from app.settings.app_settings import ApplicationSettings


async def rate_limiter_middleware(request: Request, redis: RedisDependency):
    """
    Rate limiter middleware.

    Uses Redis to store the number of requests per client host. If the number of requests exceeds the limit, it raises
    an HTTPException with status code 429: TOO_MANY_REQUESTS.

    Args:
        request: the request object
        redis: a redis connector
    """

    settings = ApplicationSettings()

    if not settings.USE_LIMITER:
        return

    if request.url.path == "/readiness":
        return

    identifier = request.client.host
    key = f"rate-limiter:{identifier}"

    try:
        counter = await redis.incr(key)

        if counter > settings.MAX_REQUESTS:
            await redis.expire(key, settings.REQUEST_TIME_LIMIT)
            raise HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS,
                                detail=f"Limit of: {settings.MAX_REQUESTS} exceeded")

    except (RedisConnectionError, ConnectionError, aioredis.exceptions.ConnectionError, OSError) as e:

        if request.url.path == "/health":
            return

        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
