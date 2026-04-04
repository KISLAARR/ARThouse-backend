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
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["Задачи"])


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    apartment_id: Optional[int] = Query(None, description="ID квартиры для фильтрации"),
    assigned_to_me: bool = Query(False, description="Показать только задачи, назначенные мне"),
    skip: int = Query(0, ge=0, description="Сколько пропустить"),
    limit: int = Query(100, ge=1, le=200, description="Сколько взять"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка задач с фильтрацией.
    - apartment_id: задачи конкретной квартиры
    - assigned_to_me: задачи, назначенные текущему пользователю
    - skip/limit: пагинация
    """
    service = TaskService(db)
    return service.get_tasks_filtered(
        user_id=current_user.id,
        apartment_id=apartment_id,
        assigned_to_me=assigned_to_me,
        skip=skip,
        limit=limit
    )


@router.get("/my", response_model=List[TaskResponse])
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить все задачи, назначенные текущему пользователю.
    """
    service = TaskService(db)
    return service.get_my_tasks(current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить детали задачи по ID.
    """
    service = TaskService(db)
    return service.get_task(current_user.id, task_id)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать новую задачу.
    """
    service = TaskService(db)
    return service.create_task(current_user.id, task_data)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Полностью обновить задачу.
    """
    service = TaskService(db)
    return service.update_task(current_user.id, task_id, task_data)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить только статус задачи.
    """
    service = TaskService(db)
    return service.update_task_status(current_user.id, task_id, status_data.status)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удалить задачу.
    """
    service = TaskService(db)
    service.delete_task(current_user.id, task_id)
    return None
