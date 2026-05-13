from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    apartments,
    surveys,
    snapshots,
    tasks,
    rooms
)

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    apartments.router,
    prefix="/apartments",
    tags=["Apartments"]
)

api_router.include_router(
    surveys.router,
    prefix="/surveys",
    tags=["Surveys"]
)

api_router.include_router(
    snapshots.router,
    prefix="/snapshots",
    tags=["Snapshots"]
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)

api_router.include_router(
    rooms.router,
    tags=["Rooms"]
)
