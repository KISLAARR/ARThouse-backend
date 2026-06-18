"""
Сервис для прямых чатов.
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.direct_chat import DirectChatThread, DirectChatMessage
from app.repositories.direct_chat_repository import DirectChatRepository
from app.repositories.user_repository import UserRepository
from app.repositories.marketplace_project_repository import MarketplaceProjectRepository
from app.schemas.direct_chat import (
    DirectChatOpenCreate,
    DirectChatMessageCreate,
    DirectChatThreadResponse,
    DirectChatMessageResponse,
)


def _peer_name(user) -> Optional[str]:
    if user is None:
        return None
    return user.display_name or user.username


def _first_image_path(attachments) -> Optional[str]:
    if not attachments:
        return None
    first = attachments[0]
    if isinstance(first, dict):
        return first.get("path") or first.get("url")
    return None


def serialize_thread(
    thread: DirectChatThread,
    viewer_user_id: int
) -> DirectChatThreadResponse:
    """Диалог глазами viewer'а: peer_name — имя собеседника."""
    if thread.customer_user_id == viewer_user_id:
        peer = thread.master
    else:
        peer = thread.customer

    return DirectChatThreadResponse(
        id=thread.id,
        peer_name=_peer_name(peer),
        master_id=thread.master_user_id,
        project_id=thread.project_id,
        project_title=thread.project.title if thread.project else None,
        last_message_preview=thread.last_message_preview,
        updated_at=thread.updated_at,
    )


def serialize_message(
    message: DirectChatMessage,
    viewer_user_id: int
) -> DirectChatMessageResponse:
    return DirectChatMessageResponse(
        id=message.id,
        thread_id=message.thread_id,
        text=message.body or "",
        image_path=_first_image_path(message.attachments_json),
        author_id=message.sender_user_id,
        mine=message.sender_user_id == viewer_user_id,
        at=message.sent_at,
    )


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
        threads = self.chat_repo.get_user_threads(user_id)
        return [serialize_thread(thread, user_id) for thread in threads]

    def open_thread(self, current_user_id: int, data: DirectChatOpenCreate):
        master = self.user_repo.get(data.master_id)

        if not master:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Мастер не найден"
            )

        if data.master_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя открыть чат с самим собой"
            )

        if data.project_id:
            project = self.project_repo.get(data.project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Проект не найден"
                )

        # Инициатор «Написать» — заказчик; собеседник — мастер.
        existing = self.chat_repo.get_existing_thread(
            customer_user_id=current_user_id,
            master_user_id=data.master_id,
            project_id=data.project_id
        )

        if existing:
            return serialize_thread(existing, current_user_id)

        thread = self.chat_repo.create_thread(
            customer_user_id=current_user_id,
            master_user_id=data.master_id,
            project_id=data.project_id
        )
        return serialize_thread(thread, current_user_id)

    def get_messages(
        self,
        user_id: int,
        thread_id: int,
        before=None,
        limit: int = 50
    ):
        self._check_thread_access(user_id, thread_id)

        messages = self.chat_repo.get_messages(
            thread_id=thread_id,
            before=before,
            limit=limit
        )

        # Репозиторий отдаёт новые сверху (desc) для пагинации по `before`;
        # для показа разворачиваем в хронологический порядок.
        messages = list(reversed(messages))

        return [serialize_message(message, user_id) for message in messages]

    def send_message(
        self,
        user_id: int,
        thread_id: int,
        data: DirectChatMessageCreate
    ):
        self._check_thread_access(user_id, thread_id)

        text = (data.text or "").strip()
        if not text and not data.image:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сообщение не может быть пустым"
            )

        attachments = None
        if data.image:
            attachments = [{"kind": "image", "path": data.image}]

        message = self.chat_repo.create_message(
            thread_id=thread_id,
            sender_user_id=user_id,
            body=text,
            attachments_json=attachments
        )

        return serialize_message(message, user_id)
