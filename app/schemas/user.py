"""
Pydantic схемы для пользователя.
Валидация входящих и исходящих данных.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# --- Базовые схемы ---
class UserBase(BaseModel):
    """Общая схема пользователя"""
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)


# --- Схемы для запросов (Request) ---
class UserCreate(UserBase):
    """Схема для регистрации нового пользователя"""
    password: str = Field(..., min_length=6)
    role: Optional[UserRole] = UserRole.CUSTOMER


class UserLogin(BaseModel):
    """Схема для входа в систему"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления профиля"""
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    role: Optional[UserRole] = None


# --- Схемы для ответов (Response) ---
class UserResponse(UserBase):
    """Схема для ответа с данными пользователя"""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy


class Token(BaseModel):
    """Схема для JWT токена"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные, хранящиеся в токене"""
    user_id: Optional[int] = None
