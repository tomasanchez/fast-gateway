"""
Booking Service endpoints
"""

from fastapi import APIRouter, HTTPException, Request, Response
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED

from app.adapters.network import gateway
from app.dependencies import AsyncHttpClientDependency
from app.domain.commands import BookFlight
from app.domain.schemas import ResponseModels, FlightReserved, ResponseModel
from app.settings.gateway_settings import GatewaySettings

router = APIRouter(prefix="/booking-service", tags=["Booking Service"])

booking_base_url = "/bookings"
booking_request_base_url = "/api/v1/bookings"


@router.get("/docs", include_in_schema=False)
async def docs():
    """
    Redirects to Auth Service docs.
    """
    settings = GatewaySettings()
    return RedirectResponse(url=f"{settings.BOOKING_SERVICE_URL}/docs")


@router.get(f"{booking_base_url}", tags=["Queries"])
async def bookings(http_client: AsyncHttpClientDependency) -> ResponseModels[FlightReserved]:
    """
    Queries bookings from Booking Service.
    """
    settings = GatewaySettings()
    response, code = await gateway(client=http_client,
                                   service_url=settings.BOOKING_SERVICE_URL,
                                   path=booking_request_base_url,
                                   method="GET")

    return ResponseModels[FlightReserved](**response)


@router.get(f"{booking_base_url}/{{booking_id}}", tags=["Queries"])
async def booking_by_id(booking_id: str,
                        http_client: AsyncHttpClientDependency) -> ResponseModel[FlightReserved]:
    """
    Queries booking by id from Booking Service.
    """
    settings = GatewaySettings()
    response, code = await gateway(client=http_client,
                                   service_url=settings.BOOKING_SERVICE_URL,
                                   path=f"{booking_request_base_url}/{booking_id}",
                                   method="GET")

    if code != HTTP_200_OK:
        raise HTTPException(status_code=code, detail=response.get("detail", "Unknown error"))

    return ResponseModel[FlightReserved](**response)


@router.post(f"{booking_base_url}",
             status_code=HTTP_201_CREATED,
             tags=["Commands"])
async def create_booking(command: BookFlight,
                         http_client: AsyncHttpClientDependency,
                         request: Request,
                         response: Response
                         ) -> ResponseModel[FlightReserved]:
    """
    Books a flight in Booking Service.
    """
    settings = GatewaySettings()

    auth_response, auth_code = await gateway(
        service_url=settings.AUTH_SERVICE_URL,
        client=http_client,
        path=f"/api/v1/users/{command.user}",
        method="GET",
    )

    if auth_code != HTTP_200_OK:
        raise HTTPException(status_code=auth_code, detail=auth_response.get("detail", "unknown error"))

    service_response, code = await gateway(
        service_url=settings.BOOKING_SERVICE_URL,
        client=http_client,
        path=booking_request_base_url,
        method="POST",
        request_body=command.json(by_alias=True))

    if code in (HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED):
        response_body = ResponseModel[FlightReserved](**service_response)

        response.headers["Location"] = f"{request.base_url}api/v1/users/{response_body.data.id}"

        return response_body

    raise HTTPException(status_code=code, detail=service_response.get("detail", "unknown error"))
