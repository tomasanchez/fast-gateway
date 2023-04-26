from fastapi import FastAPI, Form
from starlette.status import HTTP_200_OK

from app.domain.schemas import HealthChecked, ResponseModel

app = FastAPI(title="API Gateway", description="A generic API Gateway", version="0.1.0", )


@app.get("/health",
         status_code=HTTP_200_OK,
         summary="Checks healthy upstream.",
         tags=["actuator"], )
async def health() -> ResponseModel[HealthChecked]:
    """
    Health check endpoint.
    """
    return ResponseModel(data=HealthChecked())


@app.post("/register", )
async def register(username: str = Form(), password: str = Form()):
    """
    Register all routes.
    """
    print(f"register {username} {password}")
    return {"data": {"username": username, "password": password}, "status": "201 - Created"}
