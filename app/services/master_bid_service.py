"""
Сервис для откликов мастеров.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.models.master_bid import MasterBidStatus
from app.models.marketplace_project import MarketplaceProjectStatus
from app.models.contract import Contract, ContractStatus

from app.repositories.user_repository import UserRepository
from app.repositories.master_bid_repository import MasterBidRepository
from app.repositories.marketplace_project_repository import MarketplaceProjectRepository

from app.schemas.master_bid import MasterBidCreate


class MasterBidService:
    def __init__(self, db: Session):
        self.db = db
        self.bid_repo = MasterBidRepository(db)
        self.project_repo = MarketplaceProjectRepository(db)
        self.user_repo = UserRepository(db)

    def _check_master(self, user_id: int):
        user = self.user_repo.get(user_id)

        if not user or user.role != UserRole.MASTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Откликаться может только мастер"
            )

        return user

    def create_bid(self, project_id: int, master_user_id: int, data: MasterBidCreate):
        self._check_master(master_user_id)

        project = self.project_repo.get(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        if project.status != MarketplaceProjectStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Откликаться можно только на опубликованный проект"
            )

        if project.customer_user_id == master_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя откликнуться на свой проект"
            )

        existing_bid = self.bid_repo.get_by_project_and_master(
            project_id=project_id,
            master_user_id=master_user_id
        )

        if existing_bid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже откликались на этот проект"
            )

        return self.bid_repo.create(
            project_id=project_id,
            master_user_id=master_user_id,
            price_offer=data.price_offer,
            duration_offer=data.duration_offer,
            message=data.message,
            status=MasterBidStatus.SENT
        )

    def get_project_bids(self, project_id: int, customer_user_id: int):
        project = self.project_repo.get(project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        if project.customer_user_id != customer_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Смотреть отклики может только владелец проекта"
            )

        return self.bid_repo.get_by_project(project_id)

    def get_my_bids(self, master_user_id: int):
        self._check_master(master_user_id)
        return self.bid_repo.get_by_master(master_user_id)

    def accept_bid(self, bid_id: int, customer_user_id: int):
        bid = self.bid_repo.get(bid_id)

        if not bid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отклик не найден"
            )

        project = self.project_repo.get(bid.project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        if project.customer_user_id != customer_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Принять отклик может только владелец проекта"
            )

        if bid.status != MasterBidStatus.SENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Можно принять только активный отклик"
            )

        bid.status = MasterBidStatus.ACCEPTED
        project.status = MarketplaceProjectStatus.IN_WORK

        contract = Contract(
            project_id=project.id,
            customer_user_id=project.customer_user_id,
            master_user_id=bid.master_user_id,
            price=bid.price_offer,
            duration=bid.duration_offer,
            status=ContractStatus.PENDING
        )

        self.db.add(contract)
        self.db.commit()
        self.db.refresh(bid)

        self.bid_repo.decline_other_bids(
            project_id=project.id,
            accepted_bid_id=bid.id
        )

        return bid

    def decline_bid(self, bid_id: int, customer_user_id: int):
        bid = self.bid_repo.get(bid_id)

        if not bid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отклик не найден"
            )

        project = self.project_repo.get(bid.project_id)

        if not project or project.customer_user_id != customer_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Отклонить отклик может только владелец проекта"
            )

        bid.status = MasterBidStatus.DECLINED

        self.db.commit()
        self.db.refresh(bid)

        return bid

    def withdraw_bid(self, bid_id: int, master_user_id: int):
        bid = self.bid_repo.get(bid_id)

        if not bid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отклик не найден"
            )

        if bid.master_user_id != master_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Отозвать можно только свой отклик"
            )

        if bid.status != MasterBidStatus.SENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Можно отозвать только активный отклик"
            )

        bid.status = MasterBidStatus.WITHDRAWN

        self.db.commit()
        self.db.refresh(bid)

        return bid
