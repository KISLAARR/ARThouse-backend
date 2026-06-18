"""
Репозиторий для откликов мастеров.
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.master_bid import MasterBid, MasterBidStatus
from app.repositories.base import BaseRepository


class MasterBidRepository(BaseRepository[MasterBid]):
    def __init__(self, db: Session):
        super().__init__(MasterBid, db)

    def count_by_project(self, project_id: int) -> int:
        return (
            self.db.query(func.count(MasterBid.id))
            .filter(MasterBid.project_id == project_id)
            .scalar()
        ) or 0

    def counts_by_projects(self, project_ids: List[int]) -> Dict[int, int]:
        if not project_ids:
            return {}

        rows = (
            self.db.query(MasterBid.project_id, func.count(MasterBid.id))
            .filter(MasterBid.project_id.in_(project_ids))
            .group_by(MasterBid.project_id)
            .all()
        )

        return {project_id: count for project_id, count in rows}

    def get_by_project(self, project_id: int) -> List[MasterBid]:
        return self.db.query(MasterBid).filter(
            MasterBid.project_id == project_id
        ).order_by(desc(MasterBid.created_at)).all()

    def get_by_master(self, master_user_id: int) -> List[MasterBid]:
        return self.db.query(MasterBid).filter(
            MasterBid.master_user_id == master_user_id
        ).order_by(desc(MasterBid.created_at)).all()

    def get_by_project_and_master(
        self,
        project_id: int,
        master_user_id: int
    ) -> Optional[MasterBid]:
        return self.db.query(MasterBid).filter(
            MasterBid.project_id == project_id,
            MasterBid.master_user_id == master_user_id
        ).first()

    def decline_other_bids(self, project_id: int, accepted_bid_id: int):
        self.db.query(MasterBid).filter(
            MasterBid.project_id == project_id,
            MasterBid.id != accepted_bid_id,
            MasterBid.status == MasterBidStatus.SENT
        ).update(
            {"status": MasterBidStatus.DECLINED},
            synchronize_session=False
        )

        self.db.commit()
