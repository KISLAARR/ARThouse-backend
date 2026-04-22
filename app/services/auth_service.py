"""
Сервис для работы с аутентификацией - упрощённая версия.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User, UserRole, UserType


class AuthService:
    """Бизнес-логика аутентификации"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register(self, user_data: UserCreate):
        """Регистрация нового пользователя"""
        # Проверяем email
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже используется"
            )
        
        # Проверяем username
        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя пользователя уже занято"
            )
        
        # Хешируем пароль
        hashed_password = get_password_hash(user_data.password)
        
        # Создаём пользователя
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            user_type="b2c",
            role=user_data.role or UserRole.CUSTOMER,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Создаём токен
        access_token = create_access_token(
            data={"sub": str(db_user.id)}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    def login(self, login_data: UserLogin):
        """Вход в систему"""
        # Ищем пользователя
        user = self.user_repo.get_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        # Проверяем пароль
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        # Создаём токен
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
