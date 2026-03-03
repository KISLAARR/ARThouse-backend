"""
Роуты помещений
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.apartment import Apartment, Room
from app.schemas.apartment import (
    ApartmentCreate, ApartmentUpdate, ApartmentResponse, 
    ApartmentListResponse, RoomCreate, RoomResponse
)

router = APIRouter(prefix="/apartments", tags=["Помещения"])


@router.get("/my", response_model=List[ApartmentListResponse])
async def get_my_apartments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список моих помещений"""
    apartments = db.query(Apartment).filter(
        Apartment.owner_id == current_user.id
    ).all()
    return apartments


@router.post("/", response_model=ApartmentResponse)
async def create_apartment(
    apartment_data: ApartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новое помещение"""
    
    db_apartment = Apartment(
        owner_id=current_user.id,
        **apartment_data.model_dump()
    )
    
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)
    
    return db_apartment


@router.get("/{apartment_id}", response_model=ApartmentResponse)
async def get_apartment(
    apartment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить помещение по ID"""
    
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.owner_id == current_user.id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Помещение не найдено"
        )
    
    return apartment


@router.put("/{apartment_id}", response_model=ApartmentResponse)
async def update_apartment(
    apartment_id: int,
    apartment_data: ApartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить помещение"""
    
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.owner_id == current_user.id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Помещение не найдено"
        )
    
    update_data = apartment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(apartment, field, value)
    
    db.commit()
    db.refresh(apartment)
    
    return apartment


@router.delete("/{apartment_id}")
async def delete_apartment(
    apartment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить помещение"""
    
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.owner_id == current_user.id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Помещение не найдено"
        )
    
    db.delete(apartment)
    db.commit()
    
    return {"message": "Помещение удалено"}


# === Комнаты ===

@router.get("/{apartment_id}/rooms", response_model=List[RoomResponse])
async def get_rooms(
    apartment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить комнаты помещения"""
    
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.owner_id == current_user.id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Помещение не найдено"
        )
    
    return apartment.rooms


@router.post("/{apartment_id}/rooms", response_model=RoomResponse)
async def create_room(
    apartment_id: int,
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Добавить комнату"""
    
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.owner_id == current_user.id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Помещение не найдено"
        )
    
    room = Room(
        apartment_id=apartment_id,
        **room_data.model_dump()
    )
    
    db.add(room)
    db.commit()
    db.refresh(room)
    
    return room
