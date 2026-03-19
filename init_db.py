<<<<<<< HEAD
"""
Скрипт для создания таблиц в базе данных.
Запускать один раз при первом развёртывании.
"""
import sys
import os

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models import user, apartment, survey  # Импортируем все модели


def init_database():
    """Создаёт все таблицы в БД"""
    print("🚀 Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы успешно созданы!")


if __name__ == "__main__":
=======
"""
Скрипт для создания таблиц в базе данных.
Запускать один раз при первом развёртывании.
"""
import sys
import os

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models import user, apartment, survey  # Импортируем все модели


def init_database():
    """Создаёт все таблицы в БД"""
    print("🚀 Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы успешно созданы!")


if __name__ == "__main__":
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511
    init_database()