"""
Главный файл приложения FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router


def create_app() -> FastAPI:
    """
    Фабрика приложения FastAPI.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",  # Всегда включаем документацию
        redoc_url="/redoc",  # Всегда включаем ReDoc
    )
    
    # Настройка CORS (чтобы фронтенд мог обращаться)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене заменить на конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Подключаем роутеры
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    @app.get("/")
    async def root():
        """Корневой эндпоинт для проверки работы сервера"""
        return {
            "message": f"Добро пожаловать в {settings.APP_NAME}!",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    @app.get("/health")
    async def health_check():
        """Проверка здоровья сервера"""
        return {"status": "healthy"}
    
    return app


# Создаём приложение
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )