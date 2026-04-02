"""
Репозиторий для работы с комнатами.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.room import Room
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[Room]):

    def __init__(self, db: Session):
        super().__init__(Room, db)

    def get_by_apartment(self, apartment_id: int) -> List[Room]:
        return self.db.query(Room).filter(
            Room.apartment_id == apartment_id
        ).all()

    def get_by_apartment_and_name(self, apartment_id: int, name: str) -> Optional[Room]:
        return self.db.query(Room).filter(
            Room.apartment_id == apartment_id,
            Room.name == name
        ).first()
