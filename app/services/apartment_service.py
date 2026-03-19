"""
Сервис для работы с квартирами.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.repositories.apartment_repository import ApartmentRepository
from app.schemas.apartment import ApartmentCreate, ApartmentUpdate


class ApartmentService:
    """Бизнес-логика для квартир"""
    
    def __init__(self, db: Session):
        self.db = db
        self.apartment_repo = ApartmentRepository(db)
    
    def get_user_apartments(self, user_id: int) -> List:
        """Получить все квартиры пользователя"""
        return self.apartment_repo.get_by_user(user_id)
    
    def get_apartment(self, user_id: int, apartment_id: int) -> Optional:
        """Получить конкретную квартиру"""
        return self.apartment_repo.get_user_apartment(user_id, apartment_id)
    
    def create_apartment(self, user_id: int, apartment_data: ApartmentCreate):
        """Создать новую квартиру"""
        return self.apartment_repo.create(
            user_id=user_id,
            **apartment_data.dict(exclude_unset=True)
        )
    
    def update_apartment(self, user_id: int, apartment_id: int, apartment_data: ApartmentUpdate):
        """Обновить квартиру"""
        apartment = self.apartment_repo.get_user_apartment(user_id, apartment_id)
        if not apartment:
            return None
        
        # Обновляем только переданные поля
        update_data = apartment_data.dict(exclude_unset=True)
        return self.apartment_repo.update(apartment, **update_data)
    
    def delete_apartment(self, user_id: int, apartment_id: int) -> bool:
        """Удалить квартиру"""
        apartment = self.apartment_repo.get_user_apartment(user_id, apartment_id)
        if not apartment:
            return False
        
        self.apartment_repo.delete(apartment)
        return True