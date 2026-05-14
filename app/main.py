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
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse

# Создание экземпляра приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

setup_logging()
app.add_middleware(RequestIDMiddleware)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Слишком много запросов"}
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
