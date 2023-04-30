"""Application configuration - root APIRouter.
Defines all FastAPI application endpoints.

Resources:
    1. https://fastapi.tiangolo.com/tutorial/bigger-applications
"""

from fastapi import APIRouter

from app.entrypoints import actuator
from app.entrypoints.v1 import auth

root_router = APIRouter()
root_v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Base Routers
root_router.include_router(actuator.router)

# API Routers
root_v1_router.include_router(auth.router)
