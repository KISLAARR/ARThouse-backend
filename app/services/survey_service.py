"""
Сервис для опросов.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.repositories.survey_repository import SurveyRepository
from app.repositories.user_repository import UserRepository
from app.repositories.apartment_repository import ApartmentRepository
from app.schemas.survey import SurveyCreate, SurveyUpdate, SurveyStepUpdate
from app.models.survey import Survey


class SurveyService:
    def __init__(self, db: Session):
        self.db = db
        self.survey_repo = SurveyRepository(db)
        self.user_repo = UserRepository(db)
        self.apartment_repo = ApartmentRepository(db)
    
    def get_user_surveys(self, user_id: int) -> List[Survey]:
        return self.survey_repo.get_by_user(user_id)
    
    def get_latest_survey(self, user_id: int) -> Optional[Survey]:
        return self.survey_repo.get_latest_by_user(user_id)
    
    def get_survey(self, user_id: int, survey_id: int) -> Survey:
        survey = self.survey_repo.get(survey_id)
        if not survey or survey.user_id != user_id:
            raise HTTPException(status_code=404, detail="прос не найден")
        return survey
    
    def create_survey(self, user_id: int, survey_data: SurveyCreate) -> Survey:
        return self.survey_repo.create(
            user_id=user_id,
            apartment_id=survey_data.apartment_id,
            floors=survey_data.floors,
            rooms_count=survey_data.rooms_count,
            square_meters=survey_data.square_meters,
            ceiling_height=survey_data.ceiling_height,
            additional_info=survey_data.additional_info or {},
            is_completed=False,
            completion_percentage=0
        )
    
    def update_survey(self, user_id: int, survey_id: int, survey_data: SurveyUpdate) -> Survey:
        survey = self.get_survey(user_id, survey_id)
        update_data = survey_data.dict(exclude_unset=True)
        return self.survey_repo.update(survey, **update_data)
    
    def update_survey_step(self, user_id: int, survey_id: int, step_data: SurveyStepUpdate) -> Survey:
        survey = self.get_survey(user_id, survey_id)
        current = survey.additional_info or {}
        current.update(step_data.step_data)
        survey.additional_info = current
        survey.completion_percentage = step_data.completion_percentage
        if step_data.completion_percentage == 100:
            survey.is_completed = True
        self.db.commit()
        self.db.refresh(survey)
        return survey
    
    def delete_survey(self, user_id: int, survey_id: int) -> bool:
        survey = self.get_survey(user_id, survey_id)
        self.survey_repo.delete(survey)
        return True
    
    def get_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        user = self.user_repo.get(user_id)
        surveys = self.survey_repo.get_by_user(user_id)
        completed = [s for s in surveys if s.is_completed]
        apartments = self.apartment_repo.get_by_user(user_id)
        latest = self.survey_repo.get_latest_by_user(user_id)
        
        return {
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "total_surveys": len(surveys),
            "completed_surveys": len(completed),
            "latest_survey": latest,
            "apartments_count": len(apartments)
        }
