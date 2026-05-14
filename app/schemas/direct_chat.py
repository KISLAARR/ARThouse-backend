"""
Pydantic схемы для прямых чатов.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DirectChatOpenCreate(BaseModel):
    customer_user_id: Optional[int] = None
    master_user_id: int
    project_id: Optional[int] = None


class DirectChatThreadResponse(BaseModel):
    id: int

    project_id: Optional[int] = None
    customer_user_id: int
    master_user_id: int

    last_message_preview: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class DirectChatMessageCreate(BaseModel):
    body: str = Field(..., min_length=1)
    attachments_json: Optional[List[Dict[str, Any]]] = None


class DirectChatMessageResponse(BaseModel):
    id: int

    thread_id: int
    sender_user_id: int

    body: str
    attachments_json: Optional[List[Dict[str, Any]]] = None

    sent_at: datetime

    class Config:
        from_attributes = True
