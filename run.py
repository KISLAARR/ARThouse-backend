<<<<<<< HEAD
"""
Точка входа для запуска приложения.
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
=======
"""
Точка входа для запуска приложения.
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511
    )