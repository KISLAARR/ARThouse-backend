"""
Точка входа для запуска приложения.
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    # 0.0.0.0 — чтобы телефон в той же Wi‑Fi сети мог достучаться до API.
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )