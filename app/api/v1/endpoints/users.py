"""
Эндпоинты для работы с пользователями.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить информацию о текущем пользователе.
    """
    user_id = current_user.get("id")
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить информацию о текущем пользователе.
    """
    user_id = current_user.get("id")
    service = UserService(db)
    user = service.update_user(user_id, user_update)
    return user