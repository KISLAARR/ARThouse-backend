"""
Сервис для работы со снимками карты.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List

from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.apartment_repository import ApartmentRepository
from app.schemas.apartment_snapshot import MapSnapshot, ApartmentSnapshotCreate


class SnapshotService:
    """Бизнес-логика для снимков карты"""
    
    def __init__(self, db: Session):
        self.db = db
        self.snapshot_repo = SnapshotRepository(db)
        self.apartment_repo = ApartmentRepository(db)
    
    def get_latest_snapshot(self, apartment_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить последний снимок с проверкой прав"""
        # Проверяем, что квартира принадлежит пользователю
        apartment = self.apartment_repo.get_user_apartment(user_id, apartment_id)
        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Квартира не найдена или нет доступа"
            )
        
        snapshot = self.snapshot_repo.get_latest_by_apartment(apartment_id)
        if not snapshot:
            # Возвращаем пустую карту, если снимков нет
            return {
                "version": 1,
                "format": "unity_2023",
                "rooms": [],
                "walls": [],
                "doors": [],
                "windows": []
            }
        
        return snapshot.snapshot_json
    
    def save_snapshot(self, apartment_id: int, user_id: int, snapshot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Сохранить новый снимок карты"""
        # Проверяем права
        apartment = self.apartment_repo.get_user_apartment(user_id, apartment_id)
        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Квартира не найдена или нет доступа"
            )
        
        # Создаём новый снимок
        snapshot = self.snapshot_repo.create(
            apartment_id=apartment_id,
            snapshot_json=snapshot_data,
            version=snapshot_data.get('version', 1)
        )
        
        return snapshot.snapshot_json
    
    def update_furniture(
        self, 
        apartment_id: int, 
        user_id: int, 
        room_id: int, 
        furniture_id: str, 
        new_position: List[float]
    ) -> Dict[str, Any]:
        """Обновить позицию мебели в последнем снимке"""
        # Проверяем права
        apartment = self.apartment_repo.get_user_apartment(user_id, apartment_id)
        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Квартира не найдена или нет доступа"
            )
        
        # Получаем последний снимок
        snapshot = self.snapshot_repo.get_latest_by_apartment(apartment_id)
        if not snapshot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Снимок карты не найден"
            )
        
        # Обновляем позицию мебели
        updated = self.snapshot_repo.update_furniture_position(
            snapshot.id, room_id, furniture_id, new_position
        )
        
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Мебель или комната не найдены"
            )
        
        return updated.snapshot_json
    
    def get_snapshot_history(self, apartment_id: int, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить историю снимков"""
        apartment = self.apartment_repo.get_user_apartment(user_id, apartment_id)
        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Квартира не найдена или нет доступа"
            )
        
        snapshots = self.snapshot_repo.get_all_by_apartment(apartment_id, limit=limit)
        return [
            {
                "id": s.id,
                "version": s.version,
                "created_at": s.created_at,
                "preview": s.snapshot_json.get('rooms', [])[:1]  # мини-превью
            }
            for s in snapshots
        ]