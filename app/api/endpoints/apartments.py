from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_apartments():
    return {"message": "Apartments endpoint"}