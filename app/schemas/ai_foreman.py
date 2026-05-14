"""
Pydantic схемы для ИИ-прораба.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.ai_foreman import AIForemanMessageRole


class AIForemanThreadCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=160)


class AIForemanThreadResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class AIForemanMessageCreate(BaseModel):
    body: str = Field(..., min_length=1)


class AIForemanMessageResponse(BaseModel):
    id: int
    thread_id: int
    role: AIForemanMessageRole
    body: str
    sent_at: datetime

    class Config:
        from_attributes = True


class AIForemanSendMessageResponse(BaseModel):
    user_message: AIForemanMessageResponse
    assistant_message: AIForemanMessageResponse
