"""
Сервис для проектов маркетплейса.
"""
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.marketplace_project import MarketplaceProjectStatus
from app.models.user import UserRole
from app.repositories.marketplace_project_repository import MarketplaceProjectRepository
from app.repositories.master_bid_repository import MasterBidRepository
from app.schemas.marketplace_project import MarketplaceProjectCreate, MarketplaceProjectUpdate


class MarketplaceProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = MarketplaceProjectRepository(db)
        self.bid_repo = MasterBidRepository(db)

    def _attach_count(self, project):
        """Проставляет реальное число откликов на один проект."""
        if project is not None:
            project.responses_count = self.bid_repo.count_by_project(project.id)
        return project

    def _attach_counts(self, projects):
        """Проставляет число откликов на список проектов одним запросом."""
        counts = self.bid_repo.counts_by_projects([p.id for p in projects])
        for project in projects:
            project.responses_count = counts.get(project.id, 0)
        return projects

    def get_my_projects(
        self,
        user_id: int,
        status_filter=None,
        limit: int = 50,
        offset: int = 0
    ):
        projects = self.project_repo.get_by_customer(
            user_id=user_id,
            status=status_filter,
            limit=limit,
            offset=offset
        )
        return self._attach_counts(projects)

    def create_project(self, user_id: int, data: MarketplaceProjectCreate):
        project = self.project_repo.create(
            customer_user_id=user_id,
            status=MarketplaceProjectStatus.DRAFT,
            **data.dict(exclude_unset=True)
        )
        return self._attach_count(project)

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
        project = self.project_repo.update(project, **update_data)
        return self._attach_count(project)

    def publish_project(
        self,
        user_id: int,
        project_id: int,
        district: str = None,
        address: str = None
    ):
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

        # Валидация публикации (дублируем фронт): нельзя без типа работ и описания.
        if not (project.work_type and project.work_type.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя опубликовать проект без типа работ (work_type)"
            )

        if not (project.full_spec and project.full_spec.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя опубликовать проект без описания (spec)"
            )

        if district is not None:
            project.district = district
        if address is not None:
            project.address_short = address

        project.status = MarketplaceProjectStatus.PUBLISHED
        project.published_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(project)

        return self._attach_count(project)

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

        return self._attach_count(project)

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

        return self._attach_count(project)

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

    def list_feed_districts(self):
        """Динамический список районов, реально присутствующих в ленте."""
        return self.project_repo.list_feed_districts()

    def get_project_for_view(self, project_id: int):
        project = self.project_repo.get(project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        return self._attach_count(project)
