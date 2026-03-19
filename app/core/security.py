"""
<<<<<<< HEAD
Функции для безопасности: хеширование паролей, создание и проверка JWT токенов.
Используем встроенный модуль hashlib + дополнительная соль
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
import base64

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

# --- Хеширование паролей с помощью hashlib (не зависит от bcrypt) ---

def get_password_hash(password: str) -> str:
    """
    Хеширует пароль с помощью SHA-256 + соль.
    Не имеет ограничения на длину пароля.
    """
    try:
        # Преобразуем в строку
        password = str(password)

        # Генерируем случайную соль
        salt = secrets.token_hex(16)  # 16 байт = 32 символа в hex

        # Смешиваем пароль с солью
        salted = password + salt

        # Хешируем SHA-256
        hash_obj = hashlib.sha256(salted.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()

        # Сохраняем соль и хеш вместе (формат: salt$hash)
        return f"{salt}${hash_hex}"

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при хешировании пароля: {str(e)}"
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, совпадает ли пароль с хешем.
    """
    try:
        # Преобразуем в строки
        plain_password = str(plain_password)
        hashed_password = str(hashed_password)

        # Разделяем соль и хеш
        if '$' not in hashed_password:
            return False

        salt, original_hash = hashed_password.split('$', 1)

        # Хешируем введённый пароль с той же солью
        salted = plain_password + salt
        hash_obj = hashlib.sha256(salted.encode('utf-8'))
        new_hash = hash_obj.hexdigest()

        # Сравниваем хеши
        return new_hash == original_hash

    except Exception:
        return False


# --- JWT токены ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT токен.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependency для получения текущего пользователя по JWT токену.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Получаем пользователя из БД
    from app.repositories.user_repository import UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get(int(user_id))
    
    if user is None:
        raise credentials_exception
    
    return user
=======
Модуль безопасности: хеширование паролей и JWT токены
"""
from datetime import datetime, timedelta
from typing import Optional, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Получить хеш пароля"""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Создать JWT токен"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[str]:
    """Декодировать токен и вернуть subject (user_id)"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None
>>>>>>> 7a2eea49b24341b939241f3433708164a87b6511
