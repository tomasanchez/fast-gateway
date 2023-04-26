"""
Actuator entrypoint

In essence, Actuator brings production-ready features to our application.

Monitoring our app, gathering metrics, understanding traffic, or the state of our database become trivial with this
dependency.
"""

from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from app.domain.schemas import ResponseModel, HealthChecked

router = APIRouter(tags=["Actuator"])


@router.get("/health",
            status_code=HTTP_200_OK,
            summary="Checks healthy upstream.",
            tags=["actuator"], )
async def health() -> ResponseModel[HealthChecked]:
    """
    Health check endpoint.
    """
    return ResponseModel(data=HealthChecked())
