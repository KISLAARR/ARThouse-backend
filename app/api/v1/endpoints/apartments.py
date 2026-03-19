"""
Эндпоинты для работы с квартирами.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.apartment import ApartmentCreate, ApartmentUpdate, ApartmentResponse
from app.services.apartment_service import ApartmentService

router = APIRouter(prefix="/apartments", tags=["Квартиры"])


@router.get("/my", response_model=List[ApartmentResponse])
async def get_my_apartments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить все квартиры текущего пользователя.
    """
    user_id = current_user.get("id")
    service = ApartmentService(db)
    return service.get_user_apartments(user_id)


@router.post("/my", response_model=ApartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_apartment(
    apartment_data: ApartmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать новую квартиру для текущего пользователя.
    """
    user_id = current_user.get("id")
    service = ApartmentService(db)
    return service.create_apartment(user_id, apartment_data)


@router.get("/my/{apartment_id}", response_model=ApartmentResponse)
async def get_apartment(
    apartment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить конкретную квартиру по ID.
    """
    user_id = current_user.get("id")
    service = ApartmentService(db)
    apartment = service.get_apartment(user_id, apartment_id)
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Квартира не найдена"
        )
    return apartment


@router.put("/my/{apartment_id}", response_model=ApartmentResponse)
async def update_apartment(
    apartment_id: int,
    apartment_data: ApartmentUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить квартиру.
    """
    user_id = current_user.get("id")
    service = ApartmentService(db)
    apartment = service.update_apartment(user_id, apartment_id, apartment_data)
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Квартира не найдена"
        )
    return apartment


@router.delete("/my/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_apartment(
    apartment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удалить квартиру.
    """
    user_id = current_user.get("id")
    service = ApartmentService(db)
    success = service.delete_apartment(user_id, apartment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Квартира не найдена"
        )
    return None