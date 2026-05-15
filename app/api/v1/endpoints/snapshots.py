from fastapi import APIRouter

router = APIRouter(prefix="/snapshots", tags=["Snapshots"])

# Заглушка, потом доделаем
@router.get("/")
async def get_snapshots():
    return {"message": "Snapshots endpoint"}