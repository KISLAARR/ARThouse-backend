"""
Репозиторий для карты пользователя.
"""
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models.user_map import UserMap


class UserMapRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[UserMap]:
        return self.db.query(UserMap).filter(
            UserMap.user_id == user_id
        ).first()

    def create(self, user_id: int, map_json: Dict[str, Any]) -> UserMap:
        user_map = UserMap(
            user_id=user_id,
            map_json=map_json,
            revision=1
        )

        self.db.add(user_map)
        self.db.commit()
        self.db.refresh(user_map)

        return user_map

    def update(self, user_map: UserMap, map_json: Dict[str, Any]) -> UserMap:
        user_map.map_json = map_json
        user_map.revision += 1

        self.db.commit()
        self.db.refresh(user_map)

        return user_map