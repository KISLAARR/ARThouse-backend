"""
Слой 4 — Экспертность (RAG) ИИ-прораба.

Экспертность даём через RAG: курируемая база знаний, из которой консультант
достаёт релевантные куски В МОМЕНТ ответа (а не выдумывает из головы). Базу
обновляют как ПАПКУ ДОКУМЕНТОВ — без дообучения модели, и каждый совет
прослеживается до источника (verifiability).

Почему RAG, а не fine-tune: знания о ремонте меняются (материалы, цены, тренды);
RAG-базу обновляешь как файлы, дообученную модель пришлось бы переучивать.
Fine-tune — позже и только под ТОН, не под знания.

Pinterest НЕ скрапим (юр-риск, ai-datasets §9). Ценность «идей» — это таксономия
(стили, палитры, принципы зонирования), её кодируем легально как СВОИ документы:
data/knowledge/styles.json, zoning_color.json и т.д.

Структура базы:
  data/knowledge/*.json   — папка документов; файл = {doc:{id,title,source}, entries:[...]}
  data/knowledge_base.json — легаси-файл (плоский список), грузится для совместимости

Ретривер сейчас лексический (теги + совпадение слов + бонус за этап/комнату) —
надёжно и без тяжёлых зависимостей. Интерфейс Retriever.search() не изменится
при апгрейде на векторные эмбеддинги (ChromaDB/FAISS) — см. VectorRetriever ниже.
"""
import os
import re
import json
import glob

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", os.path.join(DATA_DIR, "knowledge"))
LEGACY_FILE = os.getenv("KNOWLEDGE_BASE", os.path.join(DATA_DIR, "knowledge_base.json"))

_INTERNAL = {"title": "База знаний Приделе", "kind": "internal", "license": "internal"}
_LEGACY_SOURCE = {"title": "Приделе: эргономика и пространство", "kind": "internal", "license": "internal"}

_STOPWORDS = {
    "и", "в", "на", "с", "по", "за", "к", "от", "до", "для", "что",
    "как", "это", "the", "a", "of", "то", "не", "а", "но", "или",
}


# =========================
# ЗАГРУЗКА БАЗЫ (папка документов + легаси-файл)
# =========================

def _load_entries():
    entries = []

    # 1) папка документов
    for path in sorted(glob.glob(os.path.join(KNOWLEDGE_DIR, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue

        if isinstance(data, dict) and "entries" in data:
            doc = data.get("doc", {})
            src = doc.get("source", _INTERNAL)
            doc_id = doc.get("id", os.path.splitext(os.path.basename(path))[0])
            for e in data["entries"]:
                e.setdefault("source", src)
                e.setdefault("doc", doc_id)
                entries.append(e)
        elif isinstance(data, list):
            for e in data:
                e.setdefault("source", _INTERNAL)
                e.setdefault("doc", os.path.splitext(os.path.basename(path))[0])
                entries.append(e)

    # 2) легаси одиночный файл (совместимость)
    if os.path.exists(LEGACY_FILE):
        try:
            with open(LEGACY_FILE, "r", encoding="utf-8") as f:
                for e in json.load(f):
                    e.setdefault("source", _LEGACY_SOURCE)
                    e.setdefault("doc", "ergonomics_space")
                    entries.append(e)
        except (OSError, json.JSONDecodeError):
            pass

    # дедуп по id
    seen, out = set(), []
    for e in entries:
        eid = e.get("id")
        if eid and eid in seen:
            continue
        if eid:
            seen.add(eid)
        out.append(e)
    return out


_KB = _load_entries()


def _tokens(text):
    words = re.findall(r"[a-zа-яё0-9]+", (text or "").lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def _entry_terms(entry):
    bag = " ".join(entry.get("tags", [])) + " " + entry.get("title", "") + " " + entry.get("text", "")
    return _tokens(bag)


# =========================
# РЕТРИВЕР (абстракция + лексическая реализация)
# =========================

class Retriever:
    """Контракт ретривера. Не меняется при переходе на эмбеддинги."""

    def search(self, query, stage=None, rooms=None, k=3):
        raise NotImplementedError


class LexicalRetriever(Retriever):
    """Лексический скоринг: этап + комната + пересечение слов. Без зависимостей."""

    def __init__(self, entries):
        self.entries = entries

    def search(self, query, stage=None, rooms=None, k=3):
        query_terms = _tokens(query)
        rooms = [r.lower() for r in (rooms or [])]

        scored = []
        for entry in self.entries:
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


class VectorRetriever(Retriever):
    """ЗАГОТОВКА (на «потом»): семантический поиск по эмбеддингам.

    План апгрейда без смены интерфейса:
      1) при индексации эмбеддить entry['text'] (например, multilingual e5 / bge);
      2) хранить в ChromaDB/FAISS;
      3) в search() — эмбеддить query, брать top-k по косинусной близости,
         к скору добавлять те же бонусы за stage/room.
    Пока не реализовано — используем LexicalRetriever.
    """

    def search(self, query, stage=None, rooms=None, k=3):
        raise NotImplementedError("VectorRetriever — на этап «потом». Сейчас KNOWLEDGE_RETRIEVER=lexical.")


def _build_retriever():
    kind = os.getenv("KNOWLEDGE_RETRIEVER", "lexical").lower()
    if kind == "vector":
        try:
            return VectorRetriever()
        except Exception:
            pass  # fail-safe в лексику
    return LexicalRetriever(_KB)


_RETRIEVER = _build_retriever()


# =========================
# ПУБЛИЧНЫЙ API
# =========================

def retrieve(query, stage=None, rooms=None, k=3):
    """Топ-K релевантных записей базы (с полем source)."""
    return _RETRIEVER.search(query, stage=stage, rooms=rooms, k=k)


def source_label(entry):
    src = entry.get("source") or _INTERNAL
    return src.get("title", "База знаний Приделе")


def sources_of(hits):
    """Компактный список источников для ответа API (verifiability)."""
    out, seen = [], set()
    for e in hits:
        src = e.get("source") or _INTERNAL
        key = (e.get("doc"), src.get("title"))
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "id": e.get("id"),
            "title": e.get("title"),
            "doc": e.get("doc"),
            "source": src.get("title"),
            "kind": src.get("kind", "internal"),
        })
    return out


def render_context(hits):
    """Текст справки для СИСТЕМНОЙ инструкции прораба (пользователю не виден).

    Источники наружу не показываем: это живой диалог со специалистом, а не
    справка со ссылками. Модель использует знание своими словами.
    """
    if not hits:
        return ""
    lines = [
        "ЗНАНИЯ ДЛЯ ТЕБЯ (используй своими словами, как опытный прораб; "
        "НЕ цитируй дословно и НЕ ссылайся на источники/базу):"
    ]
    for e in hits:
        lines.append(f"- {e['title']}: {e['text']}")
    return "\n".join(lines)


def knowledge_context(query, stage=None, rooms=None, k=3):
    """Готовый текст справки (обратная совместимость)."""
    return render_context(retrieve(query, stage=stage, rooms=rooms, k=k))


def stats():
    """Сводка по базе — для проверки/мониторинга качества данных."""
    docs = {}
    for e in _KB:
        docs[e.get("doc", "?")] = docs.get(e.get("doc", "?"), 0) + 1
    return {"entries": len(_KB), "by_doc": docs}
