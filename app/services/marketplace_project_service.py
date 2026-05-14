"""
Сервис для проектов маркетплейса.
"""
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.marketplace_project import MarketplaceProjectStatus
from app.models.user import UserRole
from app.repositories.marketplace_project_repository import MarketplaceProjectRepository
from app.schemas.marketplace_project import MarketplaceProjectCreate, MarketplaceProjectUpdate


class MarketplaceProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = MarketplaceProjectRepository(db)

    def get_my_projects(
        self,
        user_id: int,
        status_filter=None,
        limit: int = 50,
        offset: int = 0
    ):
        return self.project_repo.get_by_customer(
            user_id=user_id,
            status=status_filter,
            limit=limit,
            offset=offset
        )

    def create_project(self, user_id: int, data: MarketplaceProjectCreate):
        return self.project_repo.create(
            customer_user_id=user_id,
            status=MarketplaceProjectStatus.DRAFT,
            **data.dict(exclude_unset=True)
        )

    def update_project(self, user_id: int, project_id: int, data: MarketplaceProjectUpdate):
        project = self.project_repo.get_user_project(user_id, project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        if project.status != MarketplaceProjectStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Редактировать можно только черновик"
            )

        update_data = data.dict(exclude_unset=True)
        return self.project_repo.update(project, **update_data)

    def publish_project(self, user_id: int, project_id: int):
        project = self.project_repo.get_user_project(user_id, project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        if project.status != MarketplaceProjectStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Опубликовать можно только черновик"
            )

        project.status = MarketplaceProjectStatus.PUBLISHED
        project.published_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(project)

        return project

    def close_project(self, user_id: int, project_id: int):
        project = self.project_repo.get_user_project(user_id, project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        project.status = MarketplaceProjectStatus.CLOSED

        self.db.commit()
        self.db.refresh(project)

        return project

    def archive_project(self, user_id: int, project_id: int):
        project = self.project_repo.get_user_project(user_id, project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        project.status = MarketplaceProjectStatus.ARCHIVED

        self.db.commit()
        self.db.refresh(project)

        return project

    def delete_project(self, user_id: int, project_id: int):
        project = self.project_repo.get_user_project(user_id, project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        if project.status != MarketplaceProjectStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Удалить можно только черновик"
            )

        self.project_repo.delete(project)
        return True

    def get_feed(
        self,
        work_type=None,
        district=None,
        limit: int = 50,
        offset: int = 0
    ):
        return self.project_repo.get_feed(
            work_type=work_type,
            district=district,
            limit=limit,
            offset=offset
        )

    def get_project_for_view(self, project_id: int):
        project = self.project_repo.get(project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        return project
