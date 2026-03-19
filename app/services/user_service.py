"""
Сервис для работы с пользователями.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    """Бизнес-логика для пользователей"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def get_user_by_id(self, user_id: int):
        """Получить пользователя по ID"""
        return self.user_repo.get(user_id)
    
    def get_user_by_email(self, email: str):
        """Получить пользователя по email"""
        return self.user_repo.get_by_email(email)
    
    def update_user(self, user_id: int, user_data: dict):
        """Обновить данные пользователя"""
        user = self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Обновляем только переданные поля
        update_data = {k: v for k, v in user_data.items() if v is not None}
        return self.user_repo.update(user, **update_data)