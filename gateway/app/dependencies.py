"""
FastAPI dependencies injection.
"""
from typing import Annotated

from fastapi import Depends

from app.adapters.aiohttp_client import AsyncHttpClient, aio_http_client


def get_async_http_client() -> AsyncHttpClient:
    """Get async http client."""
    return aio_http_client


AsyncHttpClientDependency = Annotated[AsyncHttpClient, Depends(get_async_http_client)]
