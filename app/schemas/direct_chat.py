"""
Pydantic схемы для чатов.

Имена полей в ответах согласованы с фронтом (marketplace-backend-spec.md):
диалог — peer_name/master_id/project_title, сообщение — text/mine/at/image_path.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DirectChatOpenCreate(BaseModel):
    """Тело POST /chats — создать/найти диалог. Идемпотентно."""
    master_id: int
    project_id: Optional[int] = None


class DirectChatThreadResponse(BaseModel):
    id: int

    peer_name: Optional[str] = None
    master_id: int
    project_id: Optional[int] = None
    project_title: Optional[str] = None

    last_message_preview: Optional[str] = None
    updated_at: datetime


class DirectChatMessageCreate(BaseModel):
    """Тело POST /chats/{threadId}/messages.

    `image` — путь/URL уже загруженной картинки (см. POST /uploads).
    Допускается пустой text при наличии image.
    """
    text: str = Field("", max_length=4000)
    image: Optional[str] = None


class DirectChatMessageResponse(BaseModel):
    id: int
    thread_id: int

    text: str
    image_path: Optional[str] = None

    author_id: int
    mine: bool

    at: datetime
