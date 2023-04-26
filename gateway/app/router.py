"""Application configuration - root APIRouter.
Defines all FastAPI application endpoints.

Resources:
    1. https://fastapi.tiangolo.com/tutorial/bigger-applications
"""

from fastapi import APIRouter

from app.entrypoints import actuator

root_router = APIRouter()
root_v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Base Routers
root_router.include_router(actuator.router)

# API Routers
