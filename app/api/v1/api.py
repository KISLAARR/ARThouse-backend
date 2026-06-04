from fastapi import APIRouter
from app.api.v1.endpoints import uploads
from app.api.v1.endpoints import masters
from app.api.v1.endpoints import marketplace_projects
from app.api.v1.endpoints import master_bids
from app.api.v1.endpoints import direct_chats
from app.api.v1.endpoints import catalog
from app.api.v1.endpoints import ai_foreman
from app.api.v1.endpoints import snapshots
from app.api.v1.endpoints import maps

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
    auth.router
)

api_router.include_router(
    users.router
)

api_router.include_router(
    apartments.router
)

api_router.include_router(
    surveys.router
)

api_router.include_router(
    tasks.router
)

api_router.include_router(
    rooms.router
)

api_router.include_router(
    uploads.router,
    tags=["Uploads"]
)

api_router.include_router(
    masters.router,
    tags=["Masters"]
)

api_router.include_router(
    marketplace_projects.router,
    tags=["Projects"]
)

api_router.include_router(
    master_bids.router,
    tags=["Bids"]
)

api_router.include_router(
    direct_chats.router,
    tags=["Chats"]
)

api_router.include_router(
    catalog.router,
    tags=["Catalog"]
)

api_router.include_router(
    ai_foreman.router,
    tags=["AI Foreman"]
)

api_router.include_router(
    snapshots.router
)

api_router.include_router(
    maps.router
)