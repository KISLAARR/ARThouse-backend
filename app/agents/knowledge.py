"""
База знаний прораба (RAG-lite).

Экспертность (эргономика, последовательность ремонта, свет, цвет, стили)
подмешивается в инструкцию модели из кураторской базы data/knowledge_base.json.
Ретривер лексический (теги + совпадение слов) — надёжно и без тяжёлых
зависимостей. Интерфейс retrieve() не изменится при апгрейде на векторные
эмбеддинги позже.

ВАЖНО: контент кураторский. Pinterest/Instagram НЕ скрапим.
"""
import os
import re
import json

BASE_FILE = os.getenv(
    "KNOWLEDGE_BASE",
    os.path.join(os.path.dirname(__file__), "data", "knowledge_base.json"),
)

_STOPWORDS = {
    "и", "в", "на", "с", "по", "за", "к", "от", "до", "для", "что",
    "как", "это", "the", "a", "of", "то", "не", "а", "но", "или",
}


def _load():
    try:
        with open(BASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


_KB = _load()


def _tokens(text):
    words = re.findall(r"[a-zа-яё0-9]+", (text or "").lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def _entry_terms(entry):
    bag = " ".join(entry.get("tags", [])) + " " + entry.get("title", "") + " " + entry.get("text", "")
    return _tokens(bag)


def retrieve(query, stage=None, rooms=None, k=3):
    query_terms = _tokens(query)
    rooms = [r.lower() for r in (rooms or [])]

    scored = []
    for entry in _KB:
        score = 0.0
        if stage and stage in entry.get("stage", []):
            score += 3.0
        entry_rooms = [r.lower() for r in entry.get("room", [])]
        if "any" in entry_rooms:
            score += 0.5
        if rooms and any(r in entry_rooms for r in rooms):
            score += 2.0
        score += len(query_terms & _entry_terms(entry))
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:k]]


def knowledge_context(query, stage=None, rooms=None, k=3):
    hits = retrieve(query, stage=stage, rooms=rooms, k=k)
    if not hits:
        return ""
    lines = ["СПРАВКА ЭКСПЕРТА (опирайся на неё, но не цитируй дословно):"]
    for e in hits:
        lines.append(f"- {e['title']}: {e['text']}")
    return "\n".join(lines)
