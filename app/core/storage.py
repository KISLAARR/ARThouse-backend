"""
Файловое хранилище.
"""
import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class StorageBackend(ABC):
    @abstractmethod
    def save(self, user_id: int, kind: str, file_obj: BinaryIO, filename: str) -> dict:
        pass


class LocalStorage(StorageBackend):
    def __init__(self, media_root: str = "media"):
        self.media_root = Path(media_root)

    def save(self, user_id: int, kind: str, file_obj: BinaryIO, filename: str) -> dict:
        ext = Path(filename).suffix.lower()
        file_id = str(uuid.uuid4())

        folder = self.media_root / str(user_id) / kind
        folder.mkdir(parents=True, exist_ok=True)

        file_path = folder / f"{file_id}{ext}"

        size = 0
        with open(file_path, "wb") as f:
            while chunk := file_obj.read(1024 * 1024):
                size += len(chunk)
                f.write(chunk)

        return {
            "id": file_id,
            "url": f"/media/{user_id}/{kind}/{file_id}{ext}",
            "size": size,
        }


class S3Storage(StorageBackend):
    def save(self, user_id: int, kind: str, file_obj: BinaryIO, filename: str) -> dict:
        raise NotImplementedError("S3Storage пока не реализован")


def get_storage_backend() -> StorageBackend:
    backend = os.getenv("STORAGE_BACKEND", "local")
    media_root = os.getenv("MEDIA_ROOT", "media")

    if backend == "local":
        return LocalStorage(media_root=media_root)

    if backend == "s3":
        return S3Storage()

    raise ValueError(f"Неизвестный STORAGE_BACKEND: {backend}")
