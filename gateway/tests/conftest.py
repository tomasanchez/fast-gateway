"""
This module contains pytest fixtures.
"""
import pytest_asyncio

from app.adapters.aiohttp_client import AsyncHttpClient, AiohttpClient


@pytest_asyncio.fixture(name="aio_http_client")
async def fixture_aio_http_client() -> AsyncHttpClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: A test client for the app.
    """
    client = AiohttpClient()
    client.get_aiohttp_client()
    yield client
    await client.close_aiohttp_client()
