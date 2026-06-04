"""
Сервис карты пользователя.
"""
from typing import Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_map_repository import UserMapRepository


class UserMapService:
    def __init__(self, db: Session):
        self.db = db
        self.user_map_repo = UserMapRepository(db)

    def _validate_map_json(self, map_json: Dict[str, Any]):
        required_fields = ["metrics", "rooms", "walls", "openings", "radiators"]

        for field in required_fields:
            if field not in map_json:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"В map_json отсутствует поле: {field}"
                )

        list_fields = ["rooms", "walls", "openings", "radiators"]

        for field in list_fields:
            if not isinstance(map_json.get(field), list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Поле {field} должно быть массивом"
                )

        if not isinstance(map_json.get("metrics"), dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поле metrics должно быть объектом"
            )

    def get_my_map(self, user_id: int):
        user_map = self.user_map_repo.get_by_user_id(user_id)

        if not user_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Карта пользователя не найдена"
            )

        return user_map

    def save_my_map(self, user_id: int, map_json: Dict[str, Any]):
        self._validate_map_json(map_json)

        user_map = self.user_map_repo.get_by_user_id(user_id)

        if not user_map:
            return self.user_map_repo.create(
                user_id=user_id,
                map_json=map_json
            )

        return self.user_map_repo.update(
            user_map=user_map,
            map_json=map_json
        )