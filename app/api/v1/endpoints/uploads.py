"""
Эндпоинт загрузки файлов.
"""
from io import BytesIO
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.core.security import get_current_user
from app.core.storage import get_storage_backend

router = APIRouter()

ALLOWED_KINDS = {"portfolio", "certificate", "chat_attachment", "project_photo"}
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
IMAGE_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 10 * 1024 * 1024


@router.post("/uploads")
async def upload_file(
    kind: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    if kind not in ALLOWED_KINDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый kind"
        )

    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый тип файла"
        )

    content = await file.read()

    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Файл больше 10 МБ"
        )

    if file.content_type in IMAGE_MIME:
        try:
            img = Image.open(BytesIO(content))
            img.verify()
        except (UnidentifiedImageError, OSError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл не является валидным изображением"
            )

    storage = get_storage_backend()

    result = storage.save(
        user_id=current_user.id,
        kind=kind,
        file_obj=BytesIO(content),
        filename=file.filename or "file"
    )

    return {
        **result,
        "mime": file.content_type
    }
