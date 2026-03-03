"""
Pydantic схемы для пользователей
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Базовые поля пользователя"""
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    user_type: str = "b2c"


class UserCreate(BaseModel):
    """Схема для регистрации"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    user_type: str = "b2c"


class UserLogin(BaseModel):
    """Схема для входа"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления профиля"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    rooms_count: Optional[int] = None
    floors_count: Optional[int] = None
    wall_height: Optional[int] = None
    total_area: Optional[int] = None
    survey_completed: Optional[bool] = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    is_active: bool
    is_verified: bool
    survey_completed: bool
    rooms_count: Optional[int] = None
    floors_count: Optional[int] = None
    wall_height: Optional[int] = None
    total_area: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Схема токена"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные из токена"""
    user_id: Optional[int] = None
