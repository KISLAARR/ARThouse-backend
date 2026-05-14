"""
Главный модуль приложения.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.core.database import SessionLocal

# Создание экземпляра приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.mount("/media", StaticFiles(directory="media"), name="media")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "ARThouse API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "ok"
        }
    except Exception:
        return {
            "status": "unhealthy",
            "database": "error"
        }
    finally:
        db.close()
