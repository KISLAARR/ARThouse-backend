"""
Мониторинг и алерты ИИ-прораба.

Меряем время каждого этапа, считаем ошибки, при сбое шлём алерт
(в лог + опц. webhook ALERT_WEBHOOK — Slack/Telegram), чтобы узнать
о проблеме раньше пользователя. Метрики отдаются наружу через get_metrics().
"""
import os
import json
import time
from collections import deque
from contextlib import contextmanager

import httpx
from loguru import logger

log = logger.bind(component="ai-foreman")

# --- метрики в памяти (в проде заменяются на Prometheus/StatsD) ---
METRICS = {"stages": {}}

# Слой 2 (guardrails): счётчики по категориям + окно injection-попыток.
GUARDRAILS = {}                      # category -> count
_INJECTION_TS = deque(maxlen=100)    # метки времени injection-попыток (всплеск)
INJECTION_WINDOW_S = 300
INJECTION_SPIKE = 3                  # >= за окно → алерт P2


def _bucket(name):
    return METRICS["stages"].setdefault(
        name, {"count": 0, "errors": 0, "total_ms": 0.0, "max_ms": 0.0}
    )


def record(stage_name, duration_ms, error=False):
    b = _bucket(stage_name)
    b["count"] += 1
    b["total_ms"] += duration_ms
    b["max_ms"] = max(b["max_ms"], duration_ms)
    if error:
        b["errors"] += 1


def get_metrics():
    out = {}
    for name, b in METRICS["stages"].items():
        avg = b["total_ms"] / b["count"] if b["count"] else 0.0
        out[name] = {
            "count": b["count"],
            "errors": b["errors"],
            "avg_ms": round(avg, 1),
            "max_ms": round(b["max_ms"], 1),
        }
    return out


# =========================
# GUARDRAILS (Слой 2): метрики и алерты
# =========================

def record_guardrail(category):
    """Считаем срабатывание триажа по категории (для Data Quality)."""
    GUARDRAILS[category] = GUARDRAILS.get(category, 0) + 1


def note_injection(sample=""):
    """Фиксируем попытку injection; на всплеск — алерт P2 (сигнал безопасности)."""
    now = time.time()
    _INJECTION_TS.append(now)
    recent = [t for t in _INJECTION_TS if now - t <= INJECTION_WINDOW_S]
    if len(recent) >= INJECTION_SPIKE:
        alert(
            f"P2: всплеск injection-попыток ({len(recent)} за {INJECTION_WINDOW_S // 60} мин)",
            severity="P2",
            sample=(sample or "")[:120],
        )


def guardrail_metrics():
    """Снимок метрик Слоя 2: block_rate, off_topic_rate, injection_attempts, unsafe."""
    total = sum(GUARDRAILS.values())
    out = {"total": total, "by_category": dict(GUARDRAILS)}
    if total:
        valid = GUARDRAILS.get("valid", 0)
        out["guardrail_block_rate"] = round((total - valid) / total, 3)
        out["off_topic_rate"] = round(GUARDRAILS.get("off_topic", 0) / total, 3)
        out["unsafe_rate"] = round(GUARDRAILS.get("unsafe", 0) / total, 3)
    out["injection_attempts"] = GUARDRAILS.get("injection", 0)
    return out


ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK")


def alert(message, **context):
    log.error("ALERT: {} | {}", message, json.dumps(context, ensure_ascii=False))
    if not ALERT_WEBHOOK:
        return
    try:
        httpx.post(
            ALERT_WEBHOOK,
            json={"text": f"🚨 ИИ-прораб: {message}\n{json.dumps(context, ensure_ascii=False)}"},
            timeout=5,
        )
    except Exception as e:  # алерт не должен ронять основной поток
        log.warning("Не удалось отправить алерт в webhook: {}", e)


@contextmanager
def stage(name, **context):
    """Оборачивает этап: лог старт/конец, время, при исключении — алерт."""
    start = time.perf_counter()
    log.info("→ {} {}", name, json.dumps(context, ensure_ascii=False) if context else "")
    try:
        yield
    except Exception as e:
        duration_ms = (time.perf_counter() - start) * 1000
        record(name, duration_ms, error=True)
        alert(f"Ошибка на этапе '{name}': {e}", stage=name, **context)
        raise
    else:
        duration_ms = (time.perf_counter() - start) * 1000
        record(name, duration_ms)
        log.info("✓ {} за {:.0f} мс", name, duration_ms)
