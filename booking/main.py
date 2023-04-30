import datetime
import uuid
from enum import Enum
from re import sub
from typing import Generic, TypeVar
from uuid import UUID

from fastapi import FastAPI, HTTPException, Response, Request
from pydantic import Field, BaseModel, BaseConfig
from pydantic.generics import GenericModel
from starlette.responses import RedirectResponse
from starlette.status import HTTP_301_MOVED_PERMANENTLY, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED

app = FastAPI(title="Booking Service",
              description="A demo for a service dependant on an API Gateway for flight reservations",
              version="0.1.0",
              )


#######################################################################
# Schemas
#######################################################################


def to_camel(s: str) -> str:
    """
    Translates a string to camel case.

    Args:
        s (str): The string to translate.
    """
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return "".join([s[0].lower(), s[1:]])


class CamelCaseModel(BaseModel):
    """
    A base which attributes can be translated to camel case.
    """

    def dict(self, *args, **kwargs):
        kwargs["exclude_none"] = True
        return super().dict(*args, **kwargs)

    class Config(BaseConfig):
        alias_generator = to_camel
        allow_population_by_field_name = True
        allow_arbitrary_types = True
        anystr_strip_whitespace = True


T = TypeVar("T", bound=CamelCaseModel)


class ResponseModel(GenericModel, Generic[T], CamelCaseModel):
    """
    A response wrapper for a single resource.
    """
    data: T = Field(description="The response data.")


class ResponseModels(GenericModel, Generic[T], CamelCaseModel):
    """
    A response wrapper for a collection of resources.
    """
    data: list[T] = Field(description="The response data list.")


class ServiceStatus(str, Enum):
    """
    The service status.

    Attributes:
        OK: The service is healthy.
        ERROR: The service is unhealthy.
    """
    OK = "OK"
    ERROR = "ERROR"


class ReadinessChecked(CamelCaseModel):
    status: ServiceStatus = Field(description="The service status.")


class Passenger(CamelCaseModel):
    full_name: str = Field(description="The passenger name.", example="John Doe")
    birth_date: datetime.date = Field(description="The passenger birth date.", example="1990-01-01")
    passport_number: str = Field(description="The passenger passport number.", example="123456789")


class FlightReserved(CamelCaseModel):
    id: UUID = Field(description="The flight reservation id.", default_factory=uuid.uuid4)
    user: str = Field(description="Username of the user who made the reservation.", example="johndoe")
    flight_number: str = Field(description="The flight number.", example="TP1234")
    origin: str = Field(description="The flight origin.", example="LIS")
    destination: str = Field(description="The flight destination.", example="OPO")
    departure_time: datetime.datetime = Field(description="The flight departure date.", example="2021-01-01T12:00:00",
                                              default_factory=datetime.datetime.now)
    arrival_time: datetime.datetime = Field(description="The flight arrival date.", example="2021-01-01T15:00:00",
                                            default_factory=datetime.datetime.now)
    passengers: list[Passenger] = Field(description="The passengers list.")


class BookFlight(CamelCaseModel):
    user: str = Field(description="Username of the user who made the reservation.", example="johndoe")
    flight_number: str = Field(description="The flight number.", example="TP1234")
    origin: str = Field(description="The flight origin.", example="LIS")
    destination: str = Field(description="The flight destination.", example="OPO")
    passengers: list[Passenger] = Field(description="The passengers list.")


#######################################################################
# Entry points - Actuator
#######################################################################

@app.get("/",
         status_code=HTTP_301_MOVED_PERMANENTLY,
         include_in_schema=False,
         summary="Redirects to health check endpoint.")
async def root_redirect():
    """
    Redirects to health check endpoint.
    """
    return RedirectResponse(url="/docs", status_code=HTTP_301_MOVED_PERMANENTLY)


@app.get("/health",
         status_code=HTTP_200_OK,
         summary="Checks if application is alive.",
         tags=["Actuator"])
async def check_liveliness() -> ResponseModel[ReadinessChecked]:
    """
    Checks if the application is running, it doesn't take into account required services. See readiness.
    """
    return ResponseModel(data=ReadinessChecked(status=ServiceStatus.OK))


@app.get("/readiness",
         status_code=HTTP_200_OK,
         summary="Checks if application is ready.",
         tags=["Actuator"])
async def check_readiness() -> ResponseModel[ReadinessChecked]:
    """
    Checks if the application is ready, it takes into account required services.
    """
    return ResponseModel(data=ReadinessChecked(status=ServiceStatus.OK))


#######################################################################
# Entry points -  API
#######################################################################

db: dict[UUID, FlightReserved] = dict()


@app.get("/api/v1/bookings",
         status_code=HTTP_200_OK,
         summary="Get all flight reservations.",
         tags=["Bookings", "Queries"])
async def get_bookings() -> ResponseModels[FlightReserved]:
    """
    Get all flight reservations.
    """
    return ResponseModels(data=list(db.values()))


@app.get("/api/v1/bookings/{booking_id}",
         status_code=HTTP_200_OK,
         summary="Get a flight reservation.",
         tags=["Bookings", "Queries"])
async def get_booking(booking_id: UUID) -> ResponseModel[FlightReserved]:
    """
    Get a flight reservation.
    """
    booking = db.get(booking_id, None)
    if booking is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Booking not found")
    return ResponseModel(data=db[booking_id])


@app.post("/api/v1/bookings",
          status_code=HTTP_201_CREATED,
          summary="Reserve a flight.",
          tags=["Bookings", "Commands"])
async def book_flight(command: BookFlight, request: Request, response: Response) -> ResponseModel[FlightReserved]:
    """
    Reserve a flight.
    """

    flight_reserved = FlightReserved(**command.dict())

    db[flight_reserved.id] = flight_reserved

    response.headers["Location"] = f"{request.base_url}api/v1/bookings/{flight_reserved.id}"

    return ResponseModel(data=flight_reserved)
