from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, apartments, surveys, snapshots, tasks

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(apartments.router)
api_router.include_router(surveys.router)
api_router.include_router(snapshots.router)
api_router.include_router(tasks.router) 
