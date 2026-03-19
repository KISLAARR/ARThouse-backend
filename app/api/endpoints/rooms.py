from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_rooms():
    return {"message": "Rooms endpoint"}