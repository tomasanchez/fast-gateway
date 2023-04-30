"""
This module contains the schemas used for request/response validation in the allocation service.
"""
import datetime
import uuid
from enum import Enum
from re import sub
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseConfig, BaseModel, Field, EmailStr
from pydantic.generics import GenericModel


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


class ServiceReadinessStatus(str, Enum):
    """
    The service readiness check status.

    Attributes:
        OK: The service is healthy.
        ERROR: The service is unhealthy.
        OFFLINE: The service is offline.
    """
    OK = "healthy"
    ERROR = "unhealthy"
    OFFLINE = "offline"


class ServiceReadiness(CamelCaseModel):
    """
    A response wrapper for a service readiness check.
    """
    name: str = Field(description="The service name.", example="auth service")
    status: ServiceReadinessStatus = Field(description="The health check status.", example="ok",
                                           default=ServiceReadinessStatus.OK)


class ReadinessChecked(CamelCaseModel):
    """
    A response wrapper for a readiness check.
    """
    status: ServiceReadinessStatus = Field(description="The health check status.",
                                           example="ok",
                                           default=ServiceReadinessStatus.OFFLINE)
    services: list[ServiceReadiness] = Field(description="The services health check status.",
                                             example=[
                                                 ServiceReadiness(name="redis",
                                                                  status=ServiceReadinessStatus.OK)],
                                             default=list())


class User(CamelCaseModel):
    """
    A user.
    """
    id: UUID = Field(description="The user id.", example="1")
    username: str = Field(description="The username.", example="john")
    email: EmailStr | None = Field(description="The email.", example="jd@e.mail")
    name: str | None = Field(description="The name.", example="John")
    last_name: str | None = Field(description="The last name.", example="Doe")


class Passenger(CamelCaseModel):
    """
    A passenger.
    """
    full_name: str = Field(description="The passenger name.", example="John Doe")
    birth_date: datetime.date = Field(description="The passenger birth date.", example="1990-01-01")
    passport_number: str = Field(description="The passenger passport number.", example="123456789")


class FlightReserved(CamelCaseModel):
    """
    A flight reservation.
    """

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
