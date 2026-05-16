"""
Общий rate limiter для FastAPI.

slowapi по умолчанию читает `.env` через Starlette Config в системной кодировке
(на Windows часто cp932/cp1251) и падает на UTF-8 комментариях. Настройки
приложения загружаются через pydantic-settings отдельно.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, config_filename="")
