"""
Эндпоинты для работы со снимками карты.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.snapshot_service import SnapshotService
from app.models.user import User
from app.schemas.apartment_snapshot import ApartmentSnapshotResponse

router = APIRouter(prefix="/snapshots", tags=["Снимки карты"])


@router.get("/apartments/{apartment_id}/latest")
async def get_latest_snapshot(
    apartment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить последний снимок карты для квартиры.
    """
    service = SnapshotService(db)
    return service.get_latest_snapshot(apartment_id, current_user.id)


@router.post("/apartments/{apartment_id}/save")
async def save_snapshot(
    apartment_id: int,
    snapshot_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Сохранить новый снимок карты.
    """
    service = SnapshotService(db)
    return service.save_snapshot(apartment_id, current_user.id, snapshot_data)


@router.patch("/apartments/{apartment_id}/furniture")
async def update_furniture_position(
    apartment_id: int,
    room_id: int,
    furniture_id: str,
    new_position: List[float],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить позицию мебели.
    """
    service = SnapshotService(db)
    return service.update_furniture(apartment_id, current_user.id, room_id, furniture_id, new_position)


@router.get("/apartments/{apartment_id}/history")
async def get_snapshot_history(
    apartment_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить историю снимков карты.
    """
    service = SnapshotService(db)
    return service.get_snapshot_history(apartment_id, current_user.id, limit)