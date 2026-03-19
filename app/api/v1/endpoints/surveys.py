"""
Эндпоинты для работы с опросами.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.survey import (
    SurveyCreate, SurveyUpdate, SurveyResponse, 
    SurveyStepUpdate, UserDashboardResponse
)
from app.services.survey_service import SurveyService
from app.models.user import User

router = APIRouter(prefix="/surveys", tags=["Опросы"])


@router.get("/dashboard", response_model=UserDashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить данные для личного кабинета пользователя.
    """
    service = SurveyService(db)
    return service.get_dashboard_data(current_user.id)


@router.get("/", response_model=List[SurveyResponse])
async def get_my_surveys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить все опросы текущего пользователя.
    """
    service = SurveyService(db)
    return service.get_user_surveys(current_user.id)


@router.get("/latest", response_model=SurveyResponse)
async def get_latest_survey(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить последний опрос пользователя.
    """
    service = SurveyService(db)
    survey = service.get_latest_survey(current_user.id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Опросы не найдены"
        )
    return survey


@router.get("/{survey_id}", response_model=SurveyResponse)
async def get_survey(
    survey_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить конкретный опрос по ID.
    """
    service = SurveyService(db)
    return service.get_survey(current_user.id, survey_id)


@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(
    survey_data: SurveyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать новый опрос.
    """
    service = SurveyService(db)
    return service.create_survey(current_user.id, survey_data)


@router.put("/{survey_id}", response_model=SurveyResponse)
async def update_survey(
    survey_id: int,
    survey_data: SurveyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить существующий опрос.
    """
    service = SurveyService(db)
    return service.update_survey(current_user.id, survey_id, survey_data)


@router.patch("/{survey_id}/step", response_model=SurveyResponse)
async def update_survey_step(
    survey_id: int,
    step_data: SurveyStepUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить один шаг опроса (для пошагового заполнения).
    """
    service = SurveyService(db)
    return service.update_survey_step(current_user.id, survey_id, step_data)


@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(
    survey_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удалить опрос.
    """
    service = SurveyService(db)
    service.delete_survey(current_user.id, survey_id)
    return None
