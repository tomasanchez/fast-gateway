"""
Actuator entrypoint

In essence, Actuator brings production-ready features to our application.

Monitoring our app, gathering metrics, understanding traffic, or the state of our database become trivial with this
dependency.
"""
import asyncio

from fastapi import APIRouter
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK, HTTP_301_MOVED_PERMANENTLY

from app.adapters.network import make_request
from app.dependencies import AsyncHttpClientDependency
from app.domain.schemas import ResponseModel, HealthChecked, ServiceHealth, ServiceHealthStatus
from app.settings.gateway_settings import GatewaySettings

router = APIRouter(tags=["Actuator"])


@router.get("/health",
            status_code=HTTP_200_OK,
            summary="Checks healthy upstream.", )
async def health(http_client: AsyncHttpClientDependency) -> ResponseModel[HealthChecked]:
    """
    Health check endpoint.
    """
    settings = GatewaySettings()

    try:
        _, code = await make_request(url=settings.AUTH_SERVICE_URL + "/health", method="GET", client=http_client)
        auth_service_status = ServiceHealthStatus.OK if code == HTTP_200_OK else ServiceHealthStatus.ERROR
    except asyncio.TimeoutError:
        auth_service_status = ServiceHealthStatus.OFFLINE

    return ResponseModel(data=HealthChecked(
        status=ServiceHealthStatus.OK,
        services=[ServiceHealth(name="auth service", status=auth_service_status)]
    ))


@router.get("/",
            status_code=HTTP_301_MOVED_PERMANENTLY,
            include_in_schema=False,
            summary="Redirects to health check endpoint.")
async def root_redirect():
    """
    Redirects to health check endpoint.
    """
    return RedirectResponse(url="/docs")
