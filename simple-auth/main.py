import uuid
from enum import Enum
from re import sub
from typing import TypeVar, Generic
from uuid import UUID

from fastapi import FastAPI, HTTPException, Response, Request
from pydantic import BaseModel, BaseConfig, Field
from pydantic.generics import GenericModel
from starlette.responses import RedirectResponse
from starlette.status import HTTP_301_MOVED_PERMANENTLY, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, \
    HTTP_409_CONFLICT

app = FastAPI(title="Simple Auth Service",
              description="A demo for a service dependant on an API Gateway for authentication",
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


class UserRegistered(CamelCaseModel):
    id: UUID = Field(description="The user identifier.", default_factory=uuid.uuid4)
    username: str = Field(description="The user email.", example="johndoe")
    password: str = Field(description="The user password.")
    name: str | None = Field(description="The user name.", example="John")
    last_name: str | None = Field(description="The user last name.", example="Doe")


class RegisterUser(CamelCaseModel):
    username: str = Field(description="The user email.", example="johndoe")
    password: str = Field(description="The user password.")
    name: str | None = Field(description="The user name.", example="John")
    last_name: str | None = Field(description="The user last name.", example="Doe")


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

db: dict[UUID, UserRegistered] = {}


@app.get("/api/v1/users",
         status_code=HTTP_200_OK,
         summary="Gets all users.",
         tags=["Users", "Queries", "v1"])
async def get_users() -> ResponseModels[UserRegistered]:
    """
    Gets all users.
    """
    return ResponseModels(data=list(db.values()))


@app.get("/api/v1/users/{user_id}",
         status_code=HTTP_200_OK,
         summary="Gets a user by id.",
         tags=["Users", "Queries", "v1"])
async def get_user(user_id: UUID) -> ResponseModel[UserRegistered]:
    """
    Gets a user by id.
    """
    user = db.get(user_id, None)
    if user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    return ResponseModel(data=user)


@app.post("/api/v1/users",
          status_code=HTTP_201_CREATED,
          summary="Creates a user.",
          tags=["Users", "Commands", "v1"])
async def create_user(command: RegisterUser, request: Request, response: Response) -> ResponseModel[UserRegistered]:
    """
    Creates a user.
    """

    user = UserRegistered(**command.dict())

    if user.username in [u.username for u in db.values()]:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail="User already exists")

    db[user.id] = user

    response.headers["Location"] = f"{request.base_url}api/v1/users/{user.id}"
    return ResponseModel(data=user)
