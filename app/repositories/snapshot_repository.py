"""
Репозиторий для работы со снимками карты.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.apartment_snapshot import ApartmentSnapshot
from app.repositories.base import BaseRepository


class SnapshotRepository(BaseRepository[ApartmentSnapshot]):
    """Специфичные методы для снимков карты"""
    
    def __init__(self, db: Session):
        super().__init__(ApartmentSnapshot, db)
    
    def get_latest_by_apartment(self, apartment_id: int) -> Optional[ApartmentSnapshot]:
        """Получить последний снимок по квартире"""
        return self.db.query(ApartmentSnapshot).filter(
            ApartmentSnapshot.apartment_id == apartment_id
        ).order_by(desc(ApartmentSnapshot.created_at)).first()
    
    def get_all_by_apartment(self, apartment_id: int, skip: int = 0, limit: int = 50) -> List[ApartmentSnapshot]:
        """Получить все снимки квартиры"""
        return self.db.query(ApartmentSnapshot).filter(
            ApartmentSnapshot.apartment_id == apartment_id
        ).order_by(desc(ApartmentSnapshot.created_at)).offset(skip).limit(limit).all()
    
    def find_by_room_name(self, apartment_id: int, room_name: str) -> List[ApartmentSnapshot]:
        """Поиск снимков по названию комнаты внутри JSONB"""
        return self.db.query(ApartmentSnapshot).filter(
            ApartmentSnapshot.apartment_id == apartment_id,
            ApartmentSnapshot.snapshot_json['rooms'].contains([{"name": room_name}])
        ).all()
    
    def update_furniture_position(
        self, 
        snapshot_id: int, 
        room_id: int, 
        furniture_id: str, 
        new_position: List[float]
    ) -> Optional[ApartmentSnapshot]:
        """Обновить позицию мебели в комнате"""
        snapshot = self.get(snapshot_id)
        if not snapshot:
            return None
        
        # Ищем комнату и мебель
        for room in snapshot.snapshot_json.get('rooms', []):
            if room.get('id') == room_id:
                for furniture in room.get('furniture', []):
                    if furniture.get('id') == furniture_id:
                        furniture['position'] = new_position
                        break
        
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot