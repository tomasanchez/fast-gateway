"""Application implementation - ASGI."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from app.adapters.aiohttp_client import aio_http_client
from app.middleware import rate_limiter_middleware
from app.router import root_router, root_v1_router
from app.settings.app_settings import ApplicationSettings
from app.settings.gateway_settings import GatewaySettings

log = logging.getLogger(__name__)


async def on_startup():
    """
    Define FastAPI startup event handler.

    Resources:
        1. https://fastapi.tiangolo.com/advanced/events/#startup-event
    """
    log.debug("Execute FastAPI startup event handler.")

    aio_http_client.get_aiohttp_client()


async def on_shutdown():
    """
    Define FastAPI shutdown event handler.

    Resources:
        1. https://fastapi.tiangolo.com/advanced/events/#shutdown-event
    """
    log.debug("Execute FastAPI shutdown event handler.")

    await aio_http_client.close_aiohttp_client()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Define FastAPI lifespan event handler.

    Args:
        app (FastAPI): Application object instance.

    Resources:
        1. https://fastapi.tiangolo.com/advanced/events/#lifespan-event
    """
    log.debug("Execute FastAPI lifespan event handler.")

    await on_startup()
    yield
    await on_shutdown()


def get_application() -> FastAPI:
    """
    Initialize FastAPI application.

    Returns:
       FastAPI: Application object instance.
    """

    log.debug("Initialize FastAPI application node.")

    settings = ApplicationSettings()
    gateway = GatewaySettings()

    contact = {
        "name": "Tomas Sanchez",
        "url": "https://tomasanchez.github.io/",
        "email": "tosanchez@frba.utn.edu.ar"
    }

    license_info = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }

    tags_metadata = [
        {
            "name": "Auth Service",
            "description": "Manage registered user operations.",
            "externalDocs": {
                "description": "Auth Service docs",
                "url": f"{gateway.AUTH_SERVICE_URL}/docs",
            }
        },
        {
            "name": "Booking Service",
            "description": "Manage Flight reservations.",
            "externalDocs": {
                "description": "Booking Service docs",
                "url": f"{gateway.BOOKING_SERVICE_URL}/docs",
            },
        },
    ]

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        debug=settings.DEBUG,
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
        lifespan=lifespan,
        dependencies=[Depends(rate_limiter_middleware)],
        contact=contact,
        license_info=license_info,
        openapi_tags=tags_metadata
    )

    log.debug("Add application routes.")

    app.include_router(root_router)
    app.include_router(root_v1_router)

    return app
