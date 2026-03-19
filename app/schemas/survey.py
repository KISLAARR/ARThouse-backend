"""
Pydantic схемы для опросов.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SurveyBase(BaseModel):
    floors: Optional[int] = Field(None, ge=1, le=10)
    rooms_count: Optional[int] = Field(None, ge=1, le=50)
    square_meters: Optional[float] = Field(None, ge=1.0, le=10000.0)
    ceiling_height: Optional[float] = Field(None, ge=1.0, le=10.0)
    additional_info: Optional[Dict[str, Any]] = None
    apartment_id: Optional[int] = None


class SurveyCreate(SurveyBase):
    pass


class SurveyUpdate(BaseModel):
    floors: Optional[int] = Field(None, ge=1, le=10)
    rooms_count: Optional[int] = Field(None, ge=1, le=50)
    square_meters: Optional[float] = Field(None, ge=1.0, le=10000.0)
    ceiling_height: Optional[float] = Field(None, ge=1.0, le=10.0)
    additional_info: Optional[Dict[str, Any]] = None
    is_completed: Optional[bool] = None


class SurveyStepUpdate(BaseModel):
    step_data: Dict[str, Any]
    completion_percentage: int = Field(..., ge=0, le=100)


class SurveyResponse(SurveyBase):
    id: int
    user_id: int
    is_completed: bool
    completion_percentage: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserDashboardResponse(BaseModel):
    user_id: int
    email: str
    username: str
    total_surveys: int
    completed_surveys: int
    latest_survey: Optional[SurveyResponse] = None
    apartments_count: int
