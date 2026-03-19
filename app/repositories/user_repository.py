"""
Репозиторий для работы с пользователями.
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Специфичные методы для пользователей"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str):
        """Найти пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str):
        """Найти пользователя по имени"""
        return self.db.query(User).filter(User.username == username).first()