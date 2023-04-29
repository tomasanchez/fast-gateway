"""
FastAPI dependencies injection.
"""
from typing import Annotated

from fastapi import Depends

from app.adapters.aiohttp_client import AsyncHttpClient, aio_http_client
from app.adapters.redis_connector import RedisConnector, RedisClusterConnection, RedisClient
from app.settings.redis_settings import RedisSettings

redis_connector: RedisConnector | None = None


def get_async_http_client() -> AsyncHttpClient:
    """Get async http client."""
    return aio_http_client


AsyncHttpClientDependency = Annotated[AsyncHttpClient, Depends(get_async_http_client)]


def get_redis() -> RedisConnector:
    """Get redis connector."""

    global redis_connector

    settings = RedisSettings()

    host = settings.HOST
    port = settings.PORT

    if redis_connector is None:
        redis_connector = RedisClusterConnection(url=host, port=port) if settings.CLUSTER else RedisClient(url=host,
                                                                                                           port=port)

    return redis_connector


RedisDependency = Annotated[RedisConnector, Depends(get_redis)]
