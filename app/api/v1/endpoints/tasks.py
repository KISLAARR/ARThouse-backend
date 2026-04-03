"""
Эндпоинты для работы с задачами.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate
from app.services.task_service import TaskService
from app.models.task import Task

router = APIRouter(prefix="/tasks", tags=["Задачи"])


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    apartment_id: Optional[int] = Query(None),
    assigned_to_me: bool = Query(False),
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = TaskService(db)

    query = db.query(Task)

    if apartment_id:
        service._check_apartment_access(user_id, apartment_id)
        query = query.filter(Task.apartment_id == apartment_id)

    if assigned_to_me:
        query = query.filter(Task.assigned_to == user_id)

    if not apartment_id and not assigned_to_me:
        query = query.filter(Task.assigned_to == user_id)

    return query.offset(skip).limit(limit).all()


@router.get("/my", response_model=List[TaskResponse])
async def get_my_tasks(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = TaskService(db)
    return service.get_my_tasks(user_id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = TaskService(db)
    return service.get_task(user_id, task_id)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = TaskService(db)
    return service.create_task(user_id, task_data)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = TaskService(db)
    return service.update_task(user_id, task_id, task_data)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = TaskService(db)
    return service.update_task_status(user_id, task_id, status_data.status)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("id")
    service = TaskService(db)
    service.delete_task(user_id, task_id)
    return None
