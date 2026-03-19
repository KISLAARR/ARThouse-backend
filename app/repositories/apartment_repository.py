"""
Репозиторий для работы с квартирами.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.apartment import Apartment
from app.repositories.base import BaseRepository


class ApartmentRepository(BaseRepository[Apartment]):
    """Специфичные методы для квартир"""
    
    def __init__(self, db: Session):
        super().__init__(Apartment, db)
    
    def get_by_user(self, user_id: int) -> List[Apartment]:
        """Получить все квартиры пользователя"""
        return self.db.query(Apartment).filter(Apartment.user_id == user_id).all()
    
    def get_user_apartment(self, user_id: int, apartment_id: int) -> Optional[Apartment]:
        """Получить конкретную квартиру пользователя"""
        return self.db.query(Apartment).filter(
            Apartment.id == apartment_id,
            Apartment.user_id == user_id
        ).first()