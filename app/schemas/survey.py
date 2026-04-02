"""
Pydantic схемы для опросов.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SurveyBase(BaseModel):
    floors: Optional[int] = Field(None, ge=1, le=10)
    rooms_count: Optional[int] = Field(None, ge=1, le=50)
    square_meters: Optional[float] = Field(None, ge=1.0, le=10000.0)
    ceiling_height: Optional[float] = Field(None, ge=1.0, le=10.0)
    additional_info: Optional[Dict[str, Any]] = None
    apartment_id: Optional[int] = None

    property_type: Optional[str] = None

    total_area: Optional[float] = Field(None, ge=0.0)
    total_area_unit: Optional[str] = None

    ceiling_height_unit: Optional[str] = None

    floors_count: Optional[int] = Field(None, ge=0)

    rooms_details: Optional[List[Dict[str, Any]]] = None

    residents: Optional[Dict[str, Any]] = None

    activities: Optional[List[Any]] = None
    priorities: Optional[List[Any]] = None
    problem_areas: Optional[List[Any]] = None
    style_preferences: Optional[List[Any]] = None

    photos_paths: Optional[List[str]] = None
    floor_plan_path: Optional[str] = None


class SurveyCreate(SurveyBase):
    pass


class SurveyUpdate(BaseModel):
    floors: Optional[int] = Field(None, ge=1, le=10)
    rooms_count: Optional[int] = Field(None, ge=1, le=50)
    square_meters: Optional[float] = Field(None, ge=1.0, le=10000.0)
    ceiling_height: Optional[float] = Field(None, ge=1.0, le=10.0)
    additional_info: Optional[Dict[str, Any]] = None

    property_type: Optional[str] = None

    total_area: Optional[float] = Field(None, ge=0.0)
    total_area_unit: Optional[str] = None

    ceiling_height_unit: Optional[str] = None

    floors_count: Optional[int] = Field(None, ge=0)

    rooms_details: Optional[List[Dict[str, Any]]] = None

    residents: Optional[Dict[str, Any]] = None

    activities: Optional[List[Any]] = None
    priorities: Optional[List[Any]] = None
    problem_areas: Optional[List[Any]] = None
    style_preferences: Optional[List[Any]] = None

    photos_paths: Optional[List[str]] = None
    floor_plan_path: Optional[str] = None

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
