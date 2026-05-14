"""
Репозиторий для проектов маркетплейса.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.marketplace_project import MarketplaceProject, MarketplaceProjectStatus
from app.repositories.base import BaseRepository


class MarketplaceProjectRepository(BaseRepository[MarketplaceProject]):
    def __init__(self, db: Session):
        super().__init__(MarketplaceProject, db)

    def get_user_project(
        self,
        user_id: int,
        project_id: int
    ) -> Optional[MarketplaceProject]:
        return self.db.query(MarketplaceProject).filter(
            MarketplaceProject.id == project_id,
            MarketplaceProject.customer_user_id == user_id
        ).first()

    def get_by_customer(
        self,
        user_id: int,
        status: Optional[MarketplaceProjectStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MarketplaceProject]:
        query = self.db.query(MarketplaceProject).filter(
            MarketplaceProject.customer_user_id == user_id
        )

        if status:
            query = query.filter(MarketplaceProject.status == status)

        return (
            query
            .order_by(desc(MarketplaceProject.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_feed(
        self,
        work_type: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MarketplaceProject]:
        query = self.db.query(MarketplaceProject).filter(
            MarketplaceProject.status == MarketplaceProjectStatus.PUBLISHED
        )

        if work_type:
            query = query.filter(MarketplaceProject.work_type.ilike(f"%{work_type}%"))

        if district:
            query = query.filter(MarketplaceProject.district.ilike(f"%{district}%"))

        return (
            query
            .order_by(desc(MarketplaceProject.published_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
