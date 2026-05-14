"""
Сервис для прямых чатов.
"""
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.direct_chat_repository import DirectChatRepository
from app.repositories.user_repository import UserRepository
from app.repositories.marketplace_project_repository import MarketplaceProjectRepository
from app.schemas.direct_chat import DirectChatOpenCreate, DirectChatMessageCreate


class DirectChatService:
    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = DirectChatRepository(db)
        self.user_repo = UserRepository(db)
        self.project_repo = MarketplaceProjectRepository(db)

    def _check_thread_access(self, user_id: int, thread_id: int):
        thread = self.chat_repo.get_thread(thread_id)

        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )

        if thread.customer_user_id != user_id and thread.master_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к чату"
            )

        return thread

    def get_my_threads(self, user_id: int):
        return self.chat_repo.get_user_threads(user_id)

    def open_thread(self, current_user_id: int, data: DirectChatOpenCreate):
        master = self.user_repo.get(data.master_user_id)

        if not master:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Мастер не найден"
            )

        customer_user_id = data.customer_user_id or current_user_id

        if current_user_id not in [customer_user_id, data.master_user_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя открыть чат за другого пользователя"
            )

        if data.project_id:
            project = self.project_repo.get(data.project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Проект не найден"
                )

        existing = self.chat_repo.get_existing_thread(
            customer_user_id=customer_user_id,
            master_user_id=data.master_user_id,
            project_id=data.project_id
        )

        if existing:
            return existing

        return self.chat_repo.create_thread(
            customer_user_id=customer_user_id,
            master_user_id=data.master_user_id,
            project_id=data.project_id
        )

    def get_messages(
        self,
        user_id: int,
        thread_id: int,
        before=None,
        limit: int = 50
    ):
        self._check_thread_access(user_id, thread_id)

        return self.chat_repo.get_messages(
            thread_id=thread_id,
            before=before,
            limit=limit
        )

    def send_message(
        self,
        user_id: int,
        thread_id: int,
        data: DirectChatMessageCreate
    ):
        self._check_thread_access(user_id, thread_id)

        return self.chat_repo.create_message(
            thread_id=thread_id,
            sender_user_id=user_id,
            body=data.body,
            attachments_json=data.attachments_json
        )
