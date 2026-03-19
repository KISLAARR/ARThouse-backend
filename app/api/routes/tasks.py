"""
Роуты задач
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.apartment import Apartment, Task
from app.schemas.apartment import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Задачи"])


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    apartment_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список задач пользователя"""
    
    # Получаем все помещения пользователя
    user_apartments = db.query(Apartment.id).filter(
        Apartment.owner_id == current_user.id
    ).all()
    apartment_ids = [a.id for a in user_apartments]
    
    query = db.query(Task).filter(Task.apartment_id.in_(apartment_ids))
    
    if apartment_id:
        query = query.filter(Task.apartment_id == apartment_id)
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    return query.order_by(Task.due_date, Task.priority.desc()).all()


@router.post("/{apartment_id}", response_model=TaskResponse)
async def create_task(
    apartment_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать задачу"""
    
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.owner_id == current_user.id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Помещение не найдено"
        )
    
    task = Task(
        apartment_id=apartment_id,
        **task_data.model_dump()
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить задачу"""
    
    # Получаем все помещения пользователя
    user_apartments = db.query(Apartment.id).filter(
        Apartment.owner_id == current_user.id
    ).all()
    apartment_ids = [a.id for a in user_apartments]
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.apartment_id.in_(apartment_ids)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    
    update_data = task_data.model_dump(exclude_unset=True)
    
    # Если задача завершена, ставим время завершения
    if update_data.get("status") == "completed" and task.status != "completed":
        update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить задачу"""
    
    user_apartments = db.query(Apartment.id).filter(
        Apartment.owner_id == current_user.id
    ).all()
    apartment_ids = [a.id for a in user_apartments]
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.apartment_id.in_(apartment_ids)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    
    db.delete(task)
    db.commit()
    
    return {"message": "Задача удалена"}
