"""
Эндпоинты проектов маркетплейса.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.marketplace_project import MarketplaceProjectStatus
from app.schemas.marketplace_project import (
    MarketplaceProjectCreate,
    MarketplaceProjectUpdate,
    MarketplaceProjectResponse
)
from app.services.marketplace_project_service import MarketplaceProjectService

router = APIRouter()


@router.get("/projects/my", response_model=List[MarketplaceProjectResponse])
async def get_my_projects(
    status_filter: Optional[MarketplaceProjectStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MarketplaceProjectService(db)

    return service.get_my_projects(
        user_id=current_user.id,
        status_filter=status_filter,
        limit=limit,
        offset=offset
    )


@router.post(
    "/projects",
    response_model=MarketplaceProjectResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_project(
    project_data: MarketplaceProjectCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MarketplaceProjectService(db)

    return service.create_project(
        user_id=current_user.id,
        data=project_data
    )


@router.put("/projects/{project_id}", response_model=MarketplaceProjectResponse)
async def update_project(
    project_id: int,
    project_data: MarketplaceProjectUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MarketplaceProjectService(db)

    return service.update_project(
        user_id=current_user.id,
        project_id=project_id,
        data=project_data
    )


@router.post("/projects/{project_id}/publish", response_model=MarketplaceProjectResponse)
async def publish_project(
    project_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MarketplaceProjectService(db)

    return service.publish_project(
        user_id=current_user.id,
        project_id=project_id
    )


@router.post("/projects/{project_id}/close", response_model=MarketplaceProjectResponse)
async def close_project(
    project_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MarketplaceProjectService(db)

    return service.close_project(
        user_id=current_user.id,
        project_id=project_id
    )


@router.post("/projects/{project_id}/archive", response_model=MarketplaceProjectResponse)
async def archive_project(
    project_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MarketplaceProjectService(db)

    return service.archive_project(
        user_id=current_user.id,
        project_id=project_id
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MarketplaceProjectService(db)

    service.delete_project(
        user_id=current_user.id,
        project_id=project_id
    )

    return None


@router.get("/projects/feed", response_model=List[MarketplaceProjectResponse])
async def get_projects_feed(
    work_type: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    service = MarketplaceProjectService(db)

    return service.get_feed(
        work_type=work_type,
        district=district,
        limit=limit,
        offset=offset
    )


@router.get("/projects/{project_id}", response_model=MarketplaceProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    service = MarketplaceProjectService(db)

    return service.get_project_for_view(project_id)
