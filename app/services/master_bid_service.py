"""
Сервис для откликов мастеров.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.models.master_bid import MasterBid, MasterBidStatus
from app.models.marketplace_project import MarketplaceProjectStatus
from app.models.direct_chat import DirectChatThread
from app.models.contract import Contract, ContractStatus

from app.repositories.user_repository import UserRepository
from app.repositories.master_bid_repository import MasterBidRepository
from app.repositories.marketplace_project_repository import MarketplaceProjectRepository
from app.repositories.direct_chat_repository import DirectChatRepository

from app.schemas.master_bid import MasterBidCreate, MasterBidResponse
from app.services.direct_chat_service import serialize_thread
from app.services.notification_service import NotificationService


class MasterBidService:
    def __init__(self, db: Session):
        self.db = db
        self.bid_repo = MasterBidRepository(db)
        self.project_repo = MarketplaceProjectRepository(db)
        self.user_repo = UserRepository(db)
        self.chat_repo = DirectChatRepository(db)

    def _check_master(self, user_id: int):
        user = self.user_repo.get(user_id)

        if not user or user.role != UserRole.MASTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Откликаться может только мастер"
            )

        return user

    def _serialize_bid(self, bid: MasterBid) -> MasterBidResponse:
        """Обогащает отклик данными мастера (имя, специальность, рейтинг)."""
        master = bid.master
        profile = master.master_profile if master else None

        return MasterBidResponse(
            id=bid.id,
            project_id=bid.project_id,
            master_id=bid.master_user_id,
            master_name=(master.display_name or master.username) if master else None,
            specialty=profile.specialty if profile else None,
            rating=float(profile.rating) if profile and profile.rating is not None else None,
            completed_jobs=profile.completed_jobs if profile else None,
            price_offer=bid.price_offer,
            duration_offer=bid.duration_offer,
            message=bid.message,
            status=bid.status,
            created_at=bid.created_at,
            updated_at=bid.updated_at,
        )

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

        bid = self.bid_repo.create(
            project_id=project_id,
            master_user_id=master_user_id,
            price_offer=data.price_offer,
            duration_offer=data.duration_offer,
            message=data.message,
            status=MasterBidStatus.SENT
        )
        return self._serialize_bid(bid)

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

        return [self._serialize_bid(bid) for bid in self.bid_repo.get_by_project(project_id)]

    def get_my_bids(self, master_user_id: int):
        self._check_master(master_user_id)
        return [self._serialize_bid(bid) for bid in self.bid_repo.get_by_master(master_user_id)]

    def select_master(self, customer_user_id: int, project_id: int, bid_id: int):
        """⭐ Ядро сделки. Заказчик выбирает мастера по проекту.

        Атомарно (один commit):
          1. проект → in_work + selected_master_id/_name;
          2. выбранный отклик → selected, остальные SENT → declined;
          3. заказ уходит из ленты (status != published);
          4. создаётся/находится чат заказчик ↔ мастер;
          5. мастер уведомляется.

        Возвращает диалог (DirectChatThreadResponse).
        """
        project = self.project_repo.get(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        if project.customer_user_id != customer_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Выбрать мастера может только владелец проекта"
            )

        bid = self.bid_repo.get(bid_id)
        if not bid or bid.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отклик не найден"
            )

        already_selected = (
            project.status == MarketplaceProjectStatus.IN_WORK
            and project.selected_master_id == bid.master_user_id
            and bid.status == MasterBidStatus.SELECTED
        )

        is_first_selection = not already_selected

        if is_first_selection:
            if project.status != MarketplaceProjectStatus.PUBLISHED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Выбрать мастера можно только для опубликованного проекта"
                )

            if bid.status != MasterBidStatus.SENT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Можно выбрать только активный отклик"
                )

            master = self.user_repo.get(bid.master_user_id)
            master_name = (master.display_name or master.username) if master else None

            # 1. Проект → «В работе» + кто выбран.
            project.status = MarketplaceProjectStatus.IN_WORK
            project.selected_master_id = bid.master_user_id
            project.selected_master_name = master_name

            # 2. Статусы откликов: выбранный → selected, остальные активные → declined.
            bid.status = MasterBidStatus.SELECTED
            self.db.query(MasterBid).filter(
                MasterBid.project_id == project.id,
                MasterBid.id != bid.id,
                MasterBid.status == MasterBidStatus.SENT,
            ).update(
                {"status": MasterBidStatus.DECLINED},
                synchronize_session=False
            )

        # 4. Чат заказчик ↔ выбранный мастер по проекту (идемпотентно).
        thread = self.chat_repo.get_existing_thread(
            customer_user_id=project.customer_user_id,
            master_user_id=bid.master_user_id,
            project_id=project.id
        )
        if not thread:
            thread = DirectChatThread(
                customer_user_id=project.customer_user_id,
                master_user_id=bid.master_user_id,
                project_id=project.id
            )
            self.db.add(thread)

        self.db.commit()
        self.db.refresh(thread)

        # 5. Уведомить мастера (только при первом выборе).
        if is_first_selection:
            NotificationService(self.db).notify_master_selected(
                bid.master_user_id, project
            )

        return serialize_thread(thread, viewer_user_id=customer_user_id)

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

        return self._serialize_bid(bid)

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

        return self._serialize_bid(bid)

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

        return self._serialize_bid(bid)
