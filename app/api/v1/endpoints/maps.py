"""
Эндпоинты карты пользователя.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user_map import UserMapSaveRequest, UserMapResponse
from app.services.user_map_service import UserMapService

router = APIRouter(prefix="/maps", tags=["Maps"])


@router.get("/me", response_model=UserMapResponse)
async def get_my_map(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = UserMapService(db)
    return service.get_my_map(current_user.id)


@router.put("/me", response_model=UserMapResponse)
async def save_my_map(
    map_data: UserMapSaveRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = UserMapService(db)

    return service.save_my_map(
        user_id=current_user.id,
        map_json=map_data.map_json
    )