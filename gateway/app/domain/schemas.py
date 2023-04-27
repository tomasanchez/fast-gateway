"""
This module contains the schemas used for request/response validation in the allocation service.
"""
from enum import Enum
from re import sub
from typing import Generic, TypeVar

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


class ServiceHealthStatus(str, Enum):
    """
    The service health check status.

    Attributes:
        OK: The service is healthy.
        ERROR: The service is unhealthy.
        OFFLINE: The service is offline.
    """
    OK = "healthy"
    ERROR = "unhealthy"
    OFFLINE = "offline"


class ServiceHealth(CamelCaseModel):
    """
    A response wrapper for a service health check.
    """
    name: str = Field(description="The service name.", example="auth service")
    status: ServiceHealthStatus = Field(description="The health check status.", example="ok",
                                        default=ServiceHealthStatus.OK)


class HealthChecked(CamelCaseModel):
    """
    A response wrapper for a health check.
    """
    status: ServiceHealthStatus = Field(description="The health check status.",
                                        example="ok",
                                        default=ServiceHealthStatus.OFFLINE)
    redis: str = Field(description="The redis health check status.", example="offline", default="offline")
    services: list[ServiceHealth] = Field(description="The services health check status.",
                                          example=[ServiceHealth(name="auth service", status=ServiceHealthStatus.OK)],
                                          default=list())


class User(CamelCaseModel):
    """
    A user.
    """
    id: str = Field(description="The user id.", example="1")
    username: str = Field(description="The username.", example="john")
    email: EmailStr = Field(description="The email.", example="jd@e.mail")
