from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.snapshot_service import SnapshotService

router = APIRouter(
    prefix="/projects",
    tags=["Project Maps"]
)


@router.get("/{project_id}/map")
async def get_project_map(
    project_id: int,
    db: Session = Depends(get_db),
):

    service = SnapshotService(db)

    return service.get_project_map(project_id)


@router.post("/{project_id}/map")
async def save_project_map(
    project_id: int,
    snapshot_json: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    service = SnapshotService(db)

    return service.save_project_map(
        project_id=project_id,
        user_id=current_user.id,
        editor_role="customer",
        snapshot_json=snapshot_json
    )