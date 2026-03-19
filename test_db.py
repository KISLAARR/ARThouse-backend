<<<<<<< HEAD
"""
Скрипт для проверки подключения к БД.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.apartment import Apartment


def test_connection():
    """Проверяет подключение к БД"""
    print("🔌 Проверка подключения к базе данных...")
    try:
        db = SessionLocal()
        # Пробуем выполнить простой запрос
        user_count = db.query(User).count()
        apartment_count = db.query(Apartment).count()
        print(f"✅ Подключение успешно!")
        print(f"   Пользователей в БД: {user_count}")
        print(f"   Квартир в БД: {apartment_count}")
        db.close()
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    return True


if __name__ == "__main__":
=======
"""
Скрипт для проверки подключения к БД.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.apartment import Apartment


def test_connection():
    """Проверяет подключение к БД"""
    print("🔌 Проверка подключения к базе данных...")
    try:
        db = SessionLocal()
        # Пробуем выполнить простой запрос
        user_count = db.query(User).count()
        apartment_count = db.query(Apartment).count()
        print(f"✅ Подключение успешно!")
        print(f"   Пользователей в БД: {user_count}")
        print(f"   Квартир в БД: {apartment_count}")
        db.close()
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    return True


if __name__ == "__main__":
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511
    test_connection()