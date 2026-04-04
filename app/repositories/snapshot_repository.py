"""
Репозиторий для работы со снимками карты.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.apartment_snapshot import ApartmentSnapshot
from app.repositories.base import BaseRepository


class SnapshotRepository(BaseRepository[ApartmentSnapshot]):
    
    def __init__(self, db: Session):
        super().__init__(ApartmentSnapshot, db)
    
    def get_latest_by_apartment(self, apartment_id: int) -> Optional[ApartmentSnapshot]:
        return self.db.query(ApartmentSnapshot).filter(
            ApartmentSnapshot.apartment_id == apartment_id
        ).order_by(desc(ApartmentSnapshot.created_at)).first()
    
    def get_by_version(self, apartment_id: int, version: int) -> Optional[ApartmentSnapshot]:
        return self.db.query(ApartmentSnapshot).filter(
            ApartmentSnapshot.apartment_id == apartment_id,
            ApartmentSnapshot.version == version
        ).first()
    
    def get_all_versions(self, apartment_id: int) -> List[ApartmentSnapshot]:
        return self.db.query(ApartmentSnapshot).filter(
            ApartmentSnapshot.apartment_id == apartment_id
        ).order_by(desc(ApartmentSnapshot.version)).all()
    
    def get_all_by_apartment(self, apartment_id: int, skip: int = 0, limit: int = 50) -> List[ApartmentSnapshot]:
        """Получить все снимки квартиры"""
        return self.db.query(ApartmentSnapshot).filter(
            ApartmentSnapshot.apartment_id == apartment_id
        ).order_by(desc(ApartmentSnapshot.created_at)).offset(skip).limit(limit).all()
    
    def create_snapshot(
        self,
        apartment_id: int,
        snapshot_json: Dict[str, Any],
        version: int
    ) -> ApartmentSnapshot:
        snapshot = ApartmentSnapshot(
            apartment_id=apartment_id,
            snapshot_json=snapshot_json,
            version=version
        )
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot
    
    def delete_old_versions(self, apartment_id: int, keep_last: int = 10) -> int:
        snapshots = self.db.query(ApartmentSnapshot).filter(
            ApartmentSnapshot.apartment_id == apartment_id
        ).order_by(desc(ApartmentSnapshot.version)).all()
        
        to_delete = snapshots[keep_last:]
        deleted_count = len(to_delete)
        
        for snapshot in to_delete:
            self.db.delete(snapshot)
        
        self.db.commit()
        return deleted_count
    
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
