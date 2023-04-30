"""
Auth Service endpoints
"""
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response
from starlette.responses import RedirectResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED

from app.adapters.network import gateway
from app.dependencies import AsyncHttpClientDependency
from app.domain.commands import RegisterUser
from app.domain.schemas import User, ResponseModels, ResponseModel
from app.settings.gateway_settings import GatewaySettings

router = APIRouter(prefix="/auth-service", tags=["Auth Service"])

settings = GatewaySettings()

users_base_url = "/api/v1/users"

auth_base_url = "/api/v1/auth"


@router.get("/docs", include_in_schema=False)
async def docs():
    """
    Redirects to Auth Service docs.
    """
    return RedirectResponse(url=f"{settings.AUTH_SERVICE_URL}/docs")


@router.get("/users",
            status_code=HTTP_200_OK,
            tags=["Queries"])
async def users(http_client: AsyncHttpClientDependency) -> ResponseModels[User]:
    """
    Queries users from Auth Service.
    """

    response, code = await gateway(client=http_client,
                                   service_url=settings.AUTH_SERVICE_URL,
                                   path=users_base_url,
                                   method="GET")

    return ResponseModels[User](**response)


@router.get("/users/{user_id}",
            status_code=HTTP_200_OK,
            tags=["Queries"])
async def user_by_id(user_id: UUID,
                     http_client: AsyncHttpClientDependency) -> ResponseModel[User]:
    """
    Queries user by id from Auth Service.
    """

    response, code = await gateway(client=http_client,
                                   service_url=settings.AUTH_SERVICE_URL,
                                   path=f"{users_base_url}/{user_id}",
                                   method="GET")
    if code == HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=code, detail="User not found")

    return ResponseModel[User](**response)


@router.post("/users",
             status_code=HTTP_201_CREATED,
             tags=["Commands"])
async def create_user(command: RegisterUser,
                      http_client: AsyncHttpClientDependency,
                      request: Request,
                      response: Response
                      ) -> ResponseModel[User]:
    """
    Creates user in Auth Service.
    """

    service_response, code = await gateway(client=http_client,
                                           service_url=settings.AUTH_SERVICE_URL,
                                           path=users_base_url,
                                           method="POST",
                                           request_body=command.dict(by_alias=True))

    if code not in (HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED):
        raise HTTPException(status_code=code, detail=service_response.get("detail", "unknown error"))

    response_body = ResponseModel[User](**service_response)

    response.headers["Location"] = f"{request.base_url}{auth_base_url}/users/{response_body.data.id}"
    return response_body
