"""
Actuator entrypoint

In essence, Actuator brings production-ready features to our application.

Monitoring our app, gathering metrics, understanding traffic, or the state of our database become trivial with this
dependency.
"""
import asyncio
import logging

import aiohttp
from fastapi import APIRouter, HTTPException
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK, HTTP_301_MOVED_PERMANENTLY, HTTP_503_SERVICE_UNAVAILABLE

from app.adapters.network import make_request
from app.dependencies import AsyncHttpClientDependency, RedisDependency
from app.domain.schemas import ResponseModel, ReadinessChecked, ServiceReadiness, ServiceReadinessStatus
from app.settings.app_settings import ApplicationSettings
from app.settings.gateway_settings import GatewaySettings

router = APIRouter(tags=["Actuator"])
log = logging.getLogger("uvicorn")


async def check_services(client: AsyncHttpClientDependency,
                         services: dict[str, str] | None = None) -> list[ServiceReadiness]:
    """
    Checks if upstream services are ready.
    """
    microservices: list[ServiceReadiness] = list()

    for service, url in services.items():
        log.info(f"Checking service {service}(url={url})")

        try:
            _, code = await make_request(url=url + "/readiness", method="GET", client=client)
            status = ServiceReadinessStatus.OK if code == HTTP_200_OK else ServiceReadinessStatus.ERROR
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            log.error(f"Error while checking service {service}(url={url}): {str(e)}")
            status = ServiceReadinessStatus.OFFLINE

        microservices.append(ServiceReadiness(name=service, status=status))

    return microservices


@router.get("/readiness",
            status_code=HTTP_200_OK,
            summary="Checks healthy upstream.", )
async def ready(http_client: AsyncHttpClientDependency, redis: RedisDependency) -> ResponseModel[ReadinessChecked]:
    """
    Queries to check if application is ready to serve requests.

    It checks if the required services are ready.
    """
    app_settings = ApplicationSettings()
    gateway = GatewaySettings()

    services = []

    if app_settings.USE_LIMITER:
        services.append(ServiceReadiness(name="redis",
                                         status=ServiceReadinessStatus.OK
                                         if await redis.ping() else ServiceReadinessStatus.ERROR))

    using_services: dict[str, str] = {
        "auth-service": gateway.AUTH_SERVICE_URL,
        "booking-service": gateway.BOOKING_SERVICE_URL,
    }

    microservices = await check_services(client=http_client, services=using_services)

    services.extend(microservices)

    readiness = ReadinessChecked(
        status=ServiceReadinessStatus.OK,
        services=services,
    )

    if any(
            [service.status in (ServiceReadinessStatus.OFFLINE, ServiceReadinessStatus.ERROR) for service in
             readiness.services]):
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=readiness.dict())

    return ResponseModel(data=readiness)


@router.get("/health",
            status_code=HTTP_200_OK,
            summary="Checks if application is alive.")
async def check_liveliness() -> ResponseModel[ServiceReadiness]:
    """
    Checks if the application is running, it doesn't take into account required services. See readiness.
    """
    return ResponseModel(data=ServiceReadiness(status=ServiceReadinessStatus.OK, name="api-gateway"))


@router.get("/",
            status_code=HTTP_301_MOVED_PERMANENTLY,
            include_in_schema=False,
            summary="Redirects to health check endpoint.")
async def root_redirect():
    """
    Redirects to health check endpoint.
    """
    return RedirectResponse(url="/docs", status_code=HTTP_301_MOVED_PERMANENTLY)
