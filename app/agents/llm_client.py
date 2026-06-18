"""
LLM-клиент ИИ-прораба (OpenAI-совместимый).

Один и тот же код работает:
  * с облаком  — OpenRouter / OpenAI (нужен AI_API_KEY);
  * локально   — Ollama / vLLM на сервере (RTX 4070), БЕЗ платного ключа.

Переключение — только через .env, без правок кода:

    # --- ВАРИАНТ A: облако (быстрый старт) ---
    AI_BASE_URL=https://openrouter.ai/api/v1
    AI_API_KEY=sk-or-...
    AI_REPLY_MODEL=openai/gpt-4o-mini
    AI_EXTRACT_MODEL=openai/gpt-4o-mini

    # --- ВАРИАНТ B: локально на нашем сервере (Ollama) ---
    # ollama serve  +  ollama pull qwen2.5:14b-instruct
    AI_BASE_URL=http://localhost:11434/v1
    AI_API_KEY=ollama            # любая строка, Ollama ключ игнорирует
    AI_REPLY_MODEL=qwen2.5:14b-instruct      # качество ответа (тон прораба)
    AI_EXTRACT_MODEL=qwen2.5:7b-instruct     # дёшево/быстро (извлечение JSON)
    AI_VISION_MODEL=qwen2.5vl:7b             # разбор фото помещения

Если провайдер не настроен — поднимаем ЯВНУЮ ошибку (бриф: «явная
ошибка без API-ключа»), а не молча отдаём заглушку.
"""
import os

import httpx

# Облачный дефолт. Если AI_BASE_URL не меняли и ключа нет — считаем,
# что провайдер не настроен.
DEFAULT_CLOUD_BASE = "https://openrouter.ai/api/v1"

# Таймаут одного запроса к модели. Локальная 14B на 4070 отвечает
# за единицы секунд; ставим с запасом.
LLM_TIMEOUT_S = float(os.getenv("AI_TIMEOUT_S", "60"))


class LLMNotConfigured(RuntimeError):
    """Провайдер модели не настроен (нет ключа и не указан локальный сервер)."""


class LLMRequestError(RuntimeError):
    """Сетевая ошибка/ошибка провайдера при обращении к модели."""


def _base_url() -> str:
    return os.getenv("AI_BASE_URL", DEFAULT_CLOUD_BASE).rstrip("/")


def _api_key() -> str:
    return os.getenv("AI_API_KEY", "").strip()


def _is_local(base_url: str) -> bool:
    """Локальный сервер (Ollama/vLLM) — ключ не обязателен."""
    return any(h in base_url for h in ("localhost", "127.0.0.1", "0.0.0.0", "host.docker.internal"))


def is_configured() -> bool:
    """Можно ли вообще обращаться к модели."""
    base = _base_url()
    if _is_local(base):
        return True
    # облако: нужен ключ
    return bool(_api_key())


def reply_model() -> str:
    return os.getenv("AI_REPLY_MODEL", os.getenv("AI_MODEL", "openai/gpt-4o-mini"))


def extract_model() -> str:
    return os.getenv("AI_EXTRACT_MODEL", os.getenv("AI_MODEL", "openai/gpt-4o-mini"))


def vision_model() -> str:
    # для разбора фото; по умолчанию — та же reply-модель (если она vision)
    return os.getenv("AI_VISION_MODEL", reply_model())


def ensure_configured() -> None:
    if not is_configured():
        raise LLMNotConfigured(
            "ИИ-провайдер не настроен. Задайте AI_API_KEY (облако) "
            "или AI_BASE_URL на локальный сервер (Ollama/vLLM). "
            "См. app/agents/llm_client.py."
        )


def complete(messages, model=None, temperature=0.7) -> str:
    """Один вызов chat-completions. Возвращает текст ответа модели.

    messages — список в формате OpenAI (role/content). content может быть
    строкой или списком частей (текст + image_url) для vision-моделей.
    """
    ensure_configured()

    model = model or reply_model()
    url = f"{_base_url()}/chat/completions"

    headers = {"Content-Type": "application/json"}
    key = _api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    # OpenRouter рекомендует слать атрибуцию (не обязательно)
    headers.setdefault("HTTP-Referer", os.getenv("AI_APP_URL", "https://pridele.app"))
    headers.setdefault("X-Title", "Pridele AI Foreman")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    try:
        with httpx.Client(timeout=LLM_TIMEOUT_S) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        body = e.response.text[:300] if e.response is not None else ""
        raise LLMRequestError(f"Модель вернула {e.response.status_code}: {body}") from e
    except httpx.HTTPError as e:
        raise LLMRequestError(f"Не удалось обратиться к модели: {e}") from e

    try:
        return data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError) as e:
        raise LLMRequestError(f"Неожиданный ответ модели: {str(data)[:300]}") from e
