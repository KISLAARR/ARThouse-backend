"""
API роутеры приложения.
"""
from fastapi import APIRouter

from app.api.endpoints import users, apartments, tasks, rooms

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(apartments.router, prefix="/apartments", tags=["apartments"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])