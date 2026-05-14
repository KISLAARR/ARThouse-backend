"""
Репозиторий для чатов.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.models.direct_chat import DirectChatThread, DirectChatMessage


class DirectChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_threads(self, user_id: int) -> List[DirectChatThread]:
        return self.db.query(DirectChatThread).filter(
            or_(
                DirectChatThread.customer_user_id == user_id,
                DirectChatThread.master_user_id == user_id
            )
        ).order_by(desc(DirectChatThread.updated_at)).all()

    def get_thread(self, thread_id: int) -> Optional[DirectChatThread]:
        return self.db.query(DirectChatThread).filter(
            DirectChatThread.id == thread_id
        ).first()

    def get_existing_thread(
        self,
        customer_user_id: int,
        master_user_id: int,
        project_id: Optional[int] = None
    ) -> Optional[DirectChatThread]:
        query = self.db.query(DirectChatThread).filter(
            DirectChatThread.customer_user_id == customer_user_id,
            DirectChatThread.master_user_id == master_user_id
        )

        if project_id is None:
            query = query.filter(DirectChatThread.project_id.is_(None))
        else:
            query = query.filter(DirectChatThread.project_id == project_id)

        return query.first()

    def create_thread(
        self,
        customer_user_id: int,
        master_user_id: int,
        project_id: Optional[int] = None
    ) -> DirectChatThread:
        thread = DirectChatThread(
            customer_user_id=customer_user_id,
            master_user_id=master_user_id,
            project_id=project_id
        )

        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)

        return thread

    def get_messages(
        self,
        thread_id: int,
        before: Optional[datetime] = None,
        limit: int = 50
    ) -> List[DirectChatMessage]:
        query = self.db.query(DirectChatMessage).filter(
            DirectChatMessage.thread_id == thread_id
        )

        if before:
            query = query.filter(DirectChatMessage.sent_at < before)

        return (
            query
            .order_by(desc(DirectChatMessage.sent_at))
            .limit(limit)
            .all()
        )

    def create_message(
        self,
        thread_id: int,
        sender_user_id: int,
        body: str,
        attachments_json=None
    ) -> DirectChatMessage:
        message = DirectChatMessage(
            thread_id=thread_id,
            sender_user_id=sender_user_id,
            body=body,
            attachments_json=attachments_json
        )

        self.db.add(message)

        thread = self.get_thread(thread_id)
        if thread:
            thread.last_message_preview = body[:280]

        self.db.commit()
        self.db.refresh(message)

        return message
