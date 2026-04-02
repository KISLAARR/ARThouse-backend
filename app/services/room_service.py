"""
Сервис для работы с комнатами.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.repositories.room_repository import RoomRepository
from app.repositories.apartment_repository import ApartmentRepository
from app.schemas.room import RoomCreate, RoomUpdate


class RoomService:

    def __init__(self, db: Session):
        self.db = db
        self.room_repo = RoomRepository(db)
        self.apartment_repo = ApartmentRepository(db)

    def get_rooms(self, user_id: int, apartment_id: int) -> List:
        apartment = self.apartment_repo.get_user_apartment(user_id, apartment_id)
        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Квартира не найдена или нет доступа"
            )

        return self.room_repo.get_by_apartment(apartment_id)

    def get_room(self, user_id: int, room_id: int):
        room = self.room_repo.get(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комната не найдена"
            )

        apartment = self.apartment_repo.get_user_apartment(user_id, room.apartment_id)
        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этой комнате"
            )

        return room

    def create_room(self, user_id: int, room_data: RoomCreate):
        apartment = self.apartment_repo.get_user_apartment(user_id, room_data.apartment_id)
        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Квартира не найдена или нет доступа"
            )

        existing = self.room_repo.get_by_apartment_and_name(
            room_data.apartment_id,
            room_data.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Комната с таким именем уже существует"
            )

        return self.room_repo.create(
            **room_data.dict(exclude_unset=True)
        )

    def update_room(self, user_id: int, room_id: int, room_data: RoomUpdate):
        room = self.get_room(user_id, room_id) 

        update_data = room_data.dict(exclude_unset=True)

        if "name" in update_data:
            existing = self.room_repo.get_by_apartment_and_name(
                room.apartment_id,
                update_data["name"]
            )
            if existing and existing.id != room_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Комната с таким именем уже существует"
                )

        return self.room_repo.update(room, **update_data)

    def delete_room(self, user_id: int, room_id: int) -> bool:
        room = self.get_room(user_id, room_id)  # проверка доступа

        self.room_repo.delete(room)
        return True
