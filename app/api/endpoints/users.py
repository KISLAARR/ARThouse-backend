from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.user import UserResponse as User, UserCreate, UserUpdate
from app.services import user_service

router = APIRouter()

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Получить всех пользователей"""
    users = user_service.get_all(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int, 
    db: Session = Depends(get_db)
):
    """Получить пользователя по ID"""
    user = user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=User, status_code=201)
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    """Создать нового пользователя"""
    # Проверка, существует ли пользователь с таким email
    existing_user = user_service.get_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return user_service.create(db, user)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Обновить пользователя"""
    user = user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_service.update(db, user, user_update)

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Удалить пользователя"""
    user = user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_service.delete(db, user)
    return None