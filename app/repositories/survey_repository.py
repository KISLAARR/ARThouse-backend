"""
епозиторий для опросов.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.survey import Survey
from app.repositories.base import BaseRepository


class SurveyRepository(BaseRepository[Survey]):
    def __init__(self, db: Session):
        super().__init__(Survey, db)
    
    def get_by_user(self, user_id: int) -> List[Survey]:
        return self.db.query(Survey).filter(Survey.user_id == user_id).order_by(Survey.created_at.desc()).all()
    
    def get_by_apartment(self, apartment_id: int) -> List[Survey]:
        return self.db.query(Survey).filter(Survey.apartment_id == apartment_id).all()
    
    def get_latest_by_user(self, user_id: int) -> Optional[Survey]:
        return self.db.query(Survey).filter(
            Survey.user_id == user_id
        ).order_by(Survey.created_at.desc()).first()
    
    def get_completed_by_user(self, user_id: int) -> List[Survey]:
        return self.db.query(Survey).filter(
            and_(Survey.user_id == user_id, Survey.is_completed == True)
        ).all()
