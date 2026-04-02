"""
Эндпоинты для работы с комнатами.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse
from app.services.room_service import RoomService

router = APIRouter(tags=["Комнаты"])


@router.get("/apartments/{apartment_id}/rooms", response_model=List[RoomResponse])
async def get_rooms(
    apartment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = RoomService(db)
    return service.get_rooms(user_id, apartment_id)


@router.post(
    "/apartments/{apartment_id}/rooms",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_room(
    apartment_id: int,
    room_data: RoomCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = RoomService(db)

    room_data.apartment_id = apartment_id

    return service.create_room(user_id, room_data)


@router.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = RoomService(db)
    return service.get_room(user_id, room_id)


@router.put("/rooms/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = RoomService(db)
    return service.update_room(user_id, room_id, room_data)


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = RoomService(db)

    service.delete_room(user_id, room_id)
    return None
