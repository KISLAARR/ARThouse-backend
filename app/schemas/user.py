"""
<<<<<<< HEAD
Pydantic схемы для пользователя.
Валидация входящих и исходящих данных.
"""
from pydantic import BaseModel, EmailStr, Field
=======
Pydantic схемы для пользователей
"""
from pydantic import BaseModel, EmailStr
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511
from typing import Optional
from datetime import datetime


<<<<<<< HEAD
# --- Базовые схемы ---
class UserBase(BaseModel):
    """Общая схема пользователя"""
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)


# --- Схемы для запросов (Request) ---
class UserCreate(UserBase):
    """Схема для регистрации нового пользователя"""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Схема для входа в систему"""
=======
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
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления профиля"""
<<<<<<< HEAD
    username: Optional[str] = Field(None, min_length=2, max_length=50)


# --- Схемы для ответов (Response) ---
class UserResponse(UserBase):
    """Схема для ответа с данными пользователя"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy


class Token(BaseModel):
    """Схема для JWT токена"""
=======
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
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
<<<<<<< HEAD
    """Данные, хранящиеся в токене"""
    user_id: Optional[int] = None
=======
    """Данные из токена"""
    user_id: Optional[int] = None
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511
