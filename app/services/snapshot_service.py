"""
Сервис для работы со снимками карты.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List

from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.apartment_repository import ApartmentRepository
from app.schemas.apartment_snapshot import MapSnapshot


class SnapshotService:
    
    def __init__(self, db: Session):
        self.db = db
        self.snapshot_repo = SnapshotRepository(db)
        self.apartment_repo = ApartmentRepository(db)

    def _check_access(self, user_id: int, apartment_id: int):
        apartment = self.apartment_repo.get_user_apartment(user_id, apartment_id)
        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Квартира не найдена или нет доступа"
            )
        return apartment

    def _validate_snapshot(self, snapshot_data: Dict[str, Any]):
        try:
            MapSnapshot(**snapshot_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Невалидный snapshot_json: {str(e)}"
            )

    def get_latest_snapshot(self, user_id: int, apartment_id: int) -> Dict[str, Any]:
        self._check_access(user_id, apartment_id)

        snapshot = self.snapshot_repo.get_latest_by_apartment(apartment_id)

        if not snapshot:
            return {
                "version": 1,
                "format": "unity_2023",
                "rooms": [],
                "walls": [],
                "doors": [],
                "windows": []
            }

        return snapshot.snapshot_json

    def save_snapshot(
        self,
        user_id: int,
        apartment_id: int,
        snapshot_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        self._check_access(user_id, apartment_id)
        self._validate_snapshot(snapshot_data)

        latest = self.snapshot_repo.get_latest_by_apartment(apartment_id)

        new_version = 1
        if latest:
            new_version = latest.version + 1

        snapshot = self.snapshot_repo.create_snapshot(
            apartment_id=apartment_id,
            snapshot_json=snapshot_data,
            version=new_version
        )

        self.snapshot_repo.delete_old_versions(apartment_id)

        return snapshot.snapshot_json

    def get_snapshot_by_version(
        self,
        user_id: int,
        apartment_id: int,
        version: int
    ) -> Dict[str, Any]:
        self._check_access(user_id, apartment_id)

        snapshot = self.snapshot_repo.get_by_version(apartment_id, version)

        if not snapshot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Версия не найдена"
            )

        return snapshot.snapshot_json

    def restore_snapshot(
        self,
        user_id: int,
        apartment_id: int,
        version: int
    ) -> Dict[str, Any]:
        self._check_access(user_id, apartment_id)

        old_snapshot = self.snapshot_repo.get_by_version(apartment_id, version)

        if not old_snapshot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Версия не найдена"
            )

        latest = self.snapshot_repo.get_latest_by_apartment(apartment_id)
        new_version = 1 if not latest else latest.version + 1

        snapshot = self.snapshot_repo.create_snapshot(
            apartment_id=apartment_id,
            snapshot_json=old_snapshot.snapshot_json,
            version=new_version
        )

        return snapshot.snapshot_json

    def delete_snapshot(
        self,
        user_id: int,
        apartment_id: int,
        version: int
    ) -> bool:
        self._check_access(user_id, apartment_id)

        snapshot = self.snapshot_repo.get_by_version(apartment_id, version)

        if not snapshot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Версия не найдена"
            )

        self.snapshot_repo.delete(snapshot)
        return True

    def update_furniture(
        self,
        apartment_id: int,
        user_id: int,
        room_id: int,
        furniture_id: str,
        new_position: List[float]
    ) -> Dict[str, Any]:
        """Обновить позицию мебели в последнем снимке"""
        self._check_access(user_id, apartment_id)

        snapshot = self.snapshot_repo.get_latest_by_apartment(apartment_id)
        if not snapshot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Снимок карты не найден"
            )

        updated = self.snapshot_repo.update_furniture_position(
            snapshot.id, room_id, furniture_id, new_position
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Мебель или комната не найдены"
            )

        return updated.snapshot_json

    def get_snapshot_history(
        self,
        apartment_id: int,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """История версий"""
        self._check_access(user_id, apartment_id)

        snapshots = self.snapshot_repo.get_all_versions(apartment_id)

        return [
            {
                "version": s.version,
                "created_at": s.created_at
            }
            for s in snapshots[:limit]
        ]
