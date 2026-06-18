"""
Смета ИИ-прораба.

Принцип: LLM выбирает только catalog_work_id + qty, цену НЕ придумывает —
цена всегда берётся из каталога работ. Источник каталога:
  1) data/work_price_catalog.json (по умолчанию, тот же файл, что у фронта);
  2) позже — таблица/справочник в БД: передайте готовый index в build_estimate().
"""
import json
import os

CATALOG_FILE = os.getenv(
    "WORK_PRICE_CATALOG",
    os.path.join(os.path.dirname(__file__), "data", "work_price_catalog.json"),
)


def load_catalog():
    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def catalog_index(catalog=None):
    """id -> позиция каталога."""
    items = catalog if catalog is not None else load_catalog()
    return {item["id"]: item for item in items}


def catalog_for_prompt(catalog=None):
    """Короткий список для LLM: какие id вообще существуют."""
    items = catalog if catalog is not None else load_catalog()
    return [{"id": i["id"], "work": i["work"], "unit": i["unit"]} for i in items]


def build_estimate(lines, reserve_percent=12, index=None):
    """Считает смету из строк {catalog_work_id, qty}.

    index — заранее построенный id->позиция (например, из БД). Если None,
    берём из бандл-каталога. Неизвестные id помечаются price_missing и
    не идут в сумму (цену не выдумываем).
    """
    if index is None:
        index = catalog_index()

    sections = {}
    labor_total = 0
    missing = []

    for line in lines:
        cid = line.get("catalog_work_id")
        qty = line.get("qty") or 0
        item = index.get(cid)

        if item is None:
            missing.append(cid)
            section = sections.setdefault("99", {
                "code": "99", "title": "Требует уточнения цены",
                "lines": [], "subtotal": 0,
            })
            section["lines"].append({
                "id": cid, "work": line.get("work", cid), "unit": line.get("unit", ""),
                "qty": qty, "price_per_unit": 0, "total": 0, "price_missing": True,
            })
            continue

        total = round(item["price_per_unit"] * qty)
        labor_total += total
        section = sections.setdefault(item["section_code"], {
            "code": item["section_code"], "title": item["section_title"],
            "lines": [], "subtotal": 0,
        })
        section["lines"].append({
            "id": cid, "work": item["work"], "unit": item["unit"], "qty": qty,
            "price_per_unit": item["price_per_unit"], "total": total, "price_missing": False,
        })
        section["subtotal"] += total

    reserve = round(labor_total * reserve_percent / 100)
    grand_total = labor_total + reserve
    ordered = [sections[c] for c in sorted(sections.keys())]

    return {
        "currency": "RUB",
        "reserve_percent": reserve_percent,
        "sections": ordered,
        "totals": {
            "materials": 0,
            "labor": labor_total,
            "reserve": reserve,
            "grand_total": grand_total,
        },
        # удобные для фронта поля диапазона (scene-панель читает min_rub/max_rub)
        "min_rub": round(grand_total * 0.9),
        "max_rub": round(grand_total * 1.1),
        "price_missing": missing,
    }
