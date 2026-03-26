"""
Pydantic схемы для снимков состояния квартиры.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class FurnitureItem(BaseModel):
    """Модель предмета мебели"""
    id: str
    type: str
    model: Optional[str] = None
    position: List[float]  # [x, y] или [x, y, z]
    rotation: float = 0
    scale: List[float] = [1, 1, 1]


class RoomData(BaseModel):
    """Модель комнаты"""
    id: int
    name: str
    type: Optional[str] = None
    vertices: List[List[float]]  # [[x1,y1], [x2,y2], ...]
    furniture: List[FurnitureItem] = []


class WallData(BaseModel):
    """Модель стены"""
    start: List[float]  # [x, y]
    end: List[float]    # [x, y]
    height: float = 2.7


class DoorData(BaseModel):
    """Модель двери"""
    position: List[float]  # [x, y]
    width: float = 0.9
    height: float = 2.1


class WindowData(BaseModel):
    """Модель окна"""
    position: List[float]  # [x, y]
    width: float = 1.5
    height: float = 1.4


class CameraData(BaseModel):
    """Модель камеры в 3D"""
    position: List[float]  # [x, y, z]
    target: List[float]    # [x, y, z]


class LightingData(BaseModel):
    """Модель освещения"""
    ambient: List[float] = [0.3, 0.3, 0.4]
    directional: Dict[str, Any] = {
        "direction": [0, -1, 0],
        "color": [1, 0.95, 0.8]
    }


class MapSnapshot(BaseModel):
    """Полная модель снимка карты"""
    version: int = 1
    format: str = "unity_2023"
    rooms: List[RoomData] = []
    walls: List[WallData] = []
    doors: List[DoorData] = []
    windows: List[WindowData] = []
    cameras: Optional[CameraData] = None
    lighting: Optional[LightingData] = None


class ApartmentSnapshotCreate(BaseModel):
    """Создание снимка"""
    apartment_id: int
    snapshot_json: MapSnapshot
    version: int = 1


class ApartmentSnapshotResponse(BaseModel):
    """Ответ с данными снимка"""
    id: int
    apartment_id: int
    snapshot_json: MapSnapshot
    version: int
    created_at: datetime
    
    class Config:
        from_attributes = True