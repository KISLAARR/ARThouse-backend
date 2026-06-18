"""
Тесты Слоя 4 (Экспертность / RAG): загрузка курируемой базы, релевантность
поиска и прослеживаемость источников. Без LLM.

Запуск:  pytest test_knowledge.py -v
"""
from app.agents import knowledge


def test_corpus_loaded_with_docs():
    st = knowledge.stats()
    assert st["entries"] >= 25, "база слишком маленькая — документы не подхватились"
    # ключевые документы на месте
    for doc in ("styles", "zoning_color", "norms_safety", "sequence_materials"):
        assert doc in st["by_doc"], f"нет документа {doc}"
    # легаси-файл (эргономика) тоже загрузился
    assert "ergonomics_space" in st["by_doc"]


def test_every_entry_has_source():
    for e in knowledge._KB:
        assert e.get("source"), f"у записи {e.get('id')} нет источника"
        assert e.get("doc"), f"у записи {e.get('id')} нет doc"
        assert e["source"].get("title")


def _ids(hits):
    return [h.get("id") for h in hits]


def test_retrieve_style():
    hits = knowledge.retrieve("нравится скандинавский стиль, светло и дерево",
                              stage="after", rooms=[])
    assert "style_scandi" in _ids(hits)


def test_retrieve_safety_norm():
    hits = knowledge.retrieve("хочу снести несущую стену сам",
                              stage="before", rooms=[])
    assert "norm_load_bearing" in _ids(hits)


def test_retrieve_kitchen_ergonomics():
    hits = knowledge.retrieve("как расставить кухню, рабочий треугольник",
                              stage="after", rooms=["кухня"])
    assert any(h.get("doc") in ("ergonomics_space",) for h in hits)


def test_retrieve_sequence():
    hits = knowledge.retrieve("в каком порядке делать ремонт, этапы",
                              stage="before", rooms=[])
    assert "seq_order" in _ids(hits)


def test_sources_are_traceable():
    hits = knowledge.retrieve("скандинавский стиль", stage="after")
    srcs = knowledge.sources_of(hits)
    assert srcs and all("source" in s and "title" in s for s in srcs)
    # дедуп: один источник не повторяется
    keys = [(s["doc"], s["source"]) for s in srcs]
    assert len(keys) == len(set(keys))


def test_render_context_internal_only():
    hits = knowledge.retrieve("освещение свет сценарии", stage="after")
    text = knowledge.render_context(hits)
    # справка идёт в системную инструкцию; модели велено НЕ ссылаться на источники
    assert "ЗНАНИЯ ДЛЯ ТЕБЯ" in text
    assert "НЕ ссылайся на источники" in text


def test_empty_query_no_crash():
    assert knowledge.retrieve("", stage=None, rooms=None) == [] or isinstance(
        knowledge.retrieve("", stage=None), list
    )
