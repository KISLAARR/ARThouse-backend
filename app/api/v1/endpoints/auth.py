"""
Эндпоинты для аутентификации.
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    
    - **email**: должен быть уникальным
    - **username**: должно быть уникальным
    - **password**: минимум 6 символов
    """
    try:
        service = AuthService(db)
        result = service.register(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при регистрации: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Вход в систему.
    
    - **email**: email пользователя
    - **password**: пароль
    """
    try:
        service = AuthService(db)
        result = service.login(login_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при входе: {str(e)}"
        )