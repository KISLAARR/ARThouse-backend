"""
ИИ-прораб «Приделе» — перенос логики бота (AI-bot/logic.py) в backend.

Точка входа: chat(message, state, image) -> dict с контрактом фронта:
    {reply_text, emotion, stage, object_card, estimate_ready}

Диалог по шагам (бриф Дианы):
    Шаг 0 цель → Шаг 1 объект → комнаты → Шаг 2 «до» →
    Шаг 3 «после» → Шаг 4 бюджет/смета → Шаг 5 готово.

Главное правило общения: ДИАЛОГ, а не монолог. Быстрый вопрос —
быстрый ответ, один вопрос за раз, коротко, без воды.
"""
import json
import re

from . import llm_client
from .estimate import build_estimate, catalog_for_prompt
from .knowledge import knowledge_context
from .monitoring import stage as monitor_stage, alert

HISTORY_LIMIT = 20


# =========================
# OBJECT CARD (артефакт прораба)
# =========================

def empty_object_card():
    return {
        "meta": {
            "version": "0.1", "status": "draft", "composed_by": "ai_foreman",
            "title": None, "subtitle": None, "tags": [],
        },
        "passport": {
            "client_name": None,
            "goal": None,            # ремонт с нуля / обновление / перепланировка / меблировка / совет
            "object_type": None,     # квартира / дом / офис / коммерция
            "city": None,            # город/район — для подбора мастеров рядом
            "total_area_sqm": None,
            "ceiling_height_m": None,
            "rooms_count": None,
            "rooms_summary": None,
            "last_repair_year": None,
            "duration_weeks": None,
            "start_date": None,
            "budget_rub": None,
            "format": None,          # самостоятельная закупка / полная комплектация
            "master_type": None,     # узкий специалист / бригада «под ключ»
        },
        "rooms": [],  # [{id, name, area_sqm, width_m, length_m, note}] — width/length для редактора карты
        "design": {
            "style": None, "style_confidence": 0, "alternatives": [],
            "preferences": {
                "colors": [], "materials": [],
                "likes_bright": None, "likes_minimalism": None, "likes_natural": None,
            },
            "furniture_notes": [], "lighting_notes": [], "storage_notes": [],
            "references": [],  # фото/ссылки/Pinterest — сюда складывается выбор «тиндера»
        },
        "before": {"summary": None, "surfaces": []},
        "after": {"summary": None, "surfaces": []},
        "estimate": {
            "currency": "RUB", "reserve_percent": 12, "sections": [],
            "totals": {"materials": 0, "labor": 0, "reserve": 0, "grand_total": 0},
        },
    }


def create_empty_state():
    return {"object_card": empty_object_card(), "stage": "goal", "history": []}


# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
Ты — ИИ-прораб приложения «Приделе».

ЗАЧЕМ ТЫ НУЖЕН (если спросят — ответь коротко):
помогаешь собрать качественное ТЗ на ремонт, советуешь и ориентируешь
(что нужно для ремонта, как выбрать хорошего мастера) и собираешь
карточку-объявление проекта для биржи мастеров.

ГЛАВНОЕ ПРАВИЛО — КАК ТЫ ОБЩАЕШЬСЯ:
- Это ДИАЛОГ, а не монолог. Быстрый вопрос — быстрый ответ.
- Коротко, без воды. Обычно 1–2 коротких предложения.
- Сначала в двух словах подтверди ответ, потом задай ОДИН следующий вопрос.
  Пример: «Окей, потолки 2,40. Сколько комнат?»
- НЕ пиши длинные списки и лекции в чате. НЕ задавай несколько вопросов сразу.
- Один вопрос за раз. Не переспрашивай уже известное.
- Исключение: если человек совсем не знает, чего хочет — предложи
  2 коротких варианта на выбор.
- Если нужно показать, где что нажать в приложении — скажи коротко и по делу
  (в какую вкладку зайти, какую кнопку нажать).

ЗАКОННОСТЬ И БЕЗОПАСНОСТЬ (важно):
Если просьба незаконна, опасна или невозможна — НЕ соглашайся.
Коротко объясни почему и предложи законную альтернативу:
- несущие стены — только по проекту и с согласованием, не сносим;
- санузел и кухню нельзя переносить на жилые комнаты соседей;
- входную дверь нельзя переносить в нарушение норм эвакуации/общего имущества;
- газ, вентиляцию, общие стояки — только по проекту и согласованию;
- абсурдные/опасные просьбы (например «дверь с балкона в обрыв») — мягко
  верни к реальности и предложи разумный вариант.
Ты помощник по отделке и планированию, юр-гарантий не даёшь — при
необходимости советуй согласовать с УК или проектной организацией.

ЧТО ТЫ СОБИРАЕШЬ ПО ПОРЯДКУ:
цель → объект (тип, площадь, потолки, комнаты, адрес) → состояние «до» →
желаемое «после» (стиль, цвета, материалы, референсы) → бюджет и сроки →
виды работ. Не переходи к предложениям, пока не собрал нужное.
Цены — только из справочника, не называй суммы из головы.
"""


# =========================
# HISTORY HELPERS
# =========================

def build_user_content(text, image=None):
    if not image:
        return text
    return [
        {"type": "text", "text": text or "Вот фото помещения."},
        {"type": "image_url", "image_url": {"url": image}},
    ]


def add_user_message(state, text, image=None):
    state["history"].append({"role": "user", "content": build_user_content(text, image)})


def add_assistant_message(state, text):
    state["history"].append({"role": "assistant", "content": text})


# =========================
# LLM CALLS
# =========================

def run_llm(state, instruction, temperature=0.7):
    """Ответ модели с памятью о диалоге. instruction — режиссура этапа."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + instruction}]
    messages += state["history"][-HISTORY_LIMIT:]
    with monitor_stage("llm_reply", model=llm_client.reply_model(), stage_name=state.get("stage")):
        return llm_client.complete(messages, model=llm_client.reply_model(), temperature=temperature)


def clean_json(text):
    match = re.search(r"[\{\[].*[\}\]]", text or "", re.DOTALL)
    return match.group(0) if match else (text or "")


def merge_dict(old, new):
    for k, v in new.items():
        if isinstance(v, dict) and k in old and isinstance(old[k], dict):
            merge_dict(old[k], v)
        else:
            if v not in [None, "", [], {}]:
                old[k] = v


def update_object_card(user_message, state):
    """Отдельный дешёвый вызов: извлекает данные из реплики в object_card."""
    card = state["object_card"]
    prompt = f"""
Ты извлекаешь данные для карточки объекта ремонта (object_card).

ТЕКУЩАЯ КАРТОЧКА:
{json.dumps(card, ensure_ascii=False)}

ЭТАП: {state["stage"]}

СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ:
{user_message}

Верни ТОЛЬКО JSON с теми полями object_card, которые надо обновить.
Правила:
- Числа возвращай числом (64.3, не "~64 м²").
- Обновляй только то, что пользователь явно сказал.
- НЕ трогай поле estimate — его считает отдельный модуль.
- rooms — массив объектов {{id, name, area_sqm, width_m, length_m, note}}.
- Не добавляй пояснений вне JSON.
"""
    with monitor_stage("update_object_card", model=llm_client.extract_model()):
        raw = llm_client.complete(
            [
                {"role": "system", "content": "Ты извлекаешь структурированные данные для object_card."},
                {"role": "user", "content": prompt},
            ],
            model=llm_client.extract_model(),
            temperature=0,
        )
    content = clean_json(raw)
    try:
        new_data = json.loads(content)
        new_data.pop("estimate", None)
        merge_dict(card, new_data)
    except Exception:
        alert("Не распарсил JSON object_card", raw=content[:300])
    return card


def detect_intent(message):
    prompt = f"""
Определи intent пользователя.

Варианты:
- answer
- approval
- rejection
- uncertainty
- ask_examples
- change_direction

Сообщение:
{message}

Верни только intent одним словом.
"""
    with monitor_stage("detect_intent", model=llm_client.extract_model()):
        raw = llm_client.complete(
            [{"role": "user", "content": prompt}],
            model=llm_client.extract_model(),
            temperature=0,
        )
    return (raw or "answer").strip().lower()


def emotion_for(state, intent, estimate_ready):
    """Эмоция аватара во Flutter: обычный | think | рад."""
    if estimate_ready or intent == "approval":
        return "рад"
    if intent in ("uncertainty", "ask_examples"):
        return "think"
    return "обычный"


# =========================
# STAGES
# =========================

STAGES = ["goal", "discovery", "rooms", "before", "after", "estimate", "done"]


def next_stage(state):
    idx = STAGES.index(state["stage"])
    if idx < len(STAGES) - 1:
        state["stage"] = STAGES[idx + 1]


STAGE_INSTRUCTIONS = {
    "goal": """
ЭТАП 0: ЦЕЛЬ. Узнай одним коротким вопросом, что человек планирует:
ремонт с нуля, частичное обновление, перепланировка, меблировка или просто совет.
Коротко, дружелюбно, один вопрос.
""",
    "discovery": """
ЭТАП 1: ОБЪЕКТ. Собери по одному короткому вопросу за раз то, чего ещё нет:
тип (квартира/дом/офис/коммерция), площадь м², высота потолков, число комнат,
город/район (для поиска мастеров рядом). Подтверди предыдущий ответ в двух словах
и задай следующий вопрос. Только один вопрос.
""",
    "rooms": """
ЭТАП: КОМНАТЫ. Уточни комнаты (кухня/зал/спальня/санузел…) и их размеры.
Если называют длину/ширину стен — зафиксируй. Коротко, один вопрос за раз.
""",
    "before": """
ЭТАП 2: «ДО». Коротко узнай текущее состояние: когда был ремонт, материалы
(пол/стены/потолок), проблемы (сырость, трещины, проводка), что не устраивает.
По одному короткому вопросу. Если просьба незаконна/опасна — мягко поправь.
""",
    "after": """
ЭТАП 3: «ПОСЛЕ». Коротко выясни желаемое: что меняем (стены/пол/потолок/
планировка/коммуникации), стиль, цвета, материалы, есть ли референсы (фото/ссылки).
Со стилем помогай через предпочтения, не вопросом «какой стиль?». Один вопрос за раз.
Когда направление ясно — в одном коротком сообщении предложи его и спроси,
согласуем ли. Незаконные/опасные просьбы — коротко объясни и предложи альтернативу.
""",
    "estimate": """
ЭТАП 4: БЮДЖЕТ И ВИДЫ РАБОТ. Коротко собери бюджет, сроки, формат
(сам закупает / полная комплектация), кого ищет (узкий спец / бригада).
Затем в двух словах прокомментируй смету (она из справочника работ; цены
не из головы). Спроси, согласовать ли. Один вопрос за раз.
""",
    "done": """
ЭТАП 5: ГОТОВО. Очень коротко: карточка проекта и виды работ собраны —
можно публиковать на бирже, дальше подбор мастеров. Без воды.
""",
}


def last_user_text(state):
    for msg in reversed(state["history"]):
        if msg["role"] != "user":
            continue
        content = msg["content"]
        if isinstance(content, str):
            return content
        for part in content:
            if part.get("type") == "text":
                return part.get("text", "")
    return ""


def room_hints(state):
    return [r.get("name", "") for r in state["object_card"].get("rooms", []) if r.get("name")]


def stage_reply(state):
    instruction = STAGE_INSTRUCTIONS.get(state["stage"], STAGE_INSTRUCTIONS["discovery"])
    query = (last_user_text(state) + " " + " ".join(room_hints(state))).strip()
    expert = knowledge_context(query, stage=state["stage"], rooms=room_hints(state))
    if expert:
        instruction += "\n\n" + expert
    instruction += f"\n\nТЕКУЩАЯ КАРТОЧКА:\n{json.dumps(state['object_card'], ensure_ascii=False)}"
    return run_llm(state, instruction)


# =========================
# ESTIMATE
# =========================

def propose_estimate_lines(state, catalog=None):
    card = state["object_card"]
    catalog_list = catalog_for_prompt(catalog)
    prompt = f"""
Ты составляешь смету ремонта. Выбери нужные работы ТОЛЬКО из каталога ниже.

КАРТОЧКА ОБЪЕКТА:
{json.dumps(card, ensure_ascii=False)}

КАТАЛОГ РАБОТ (разрешённые id):
{json.dumps(catalog_list, ensure_ascii=False)}

Верни ТОЛЬКО JSON-массив строк вида:
[{{"catalog_work_id": "wall_paint", "qty": 45}}]

Правила:
- Используй только id из каталога.
- qty — число (объём в указанной единице), оцени из площадей карточки.
- Не придумывай цены и не добавляй текст вне JSON.
"""
    with monitor_stage("propose_estimate", model=llm_client.extract_model()):
        raw = llm_client.complete(
            [
                {"role": "system", "content": "Ты подбираешь позиции сметы по каталогу."},
                {"role": "user", "content": prompt},
            ],
            model=llm_client.extract_model(),
            temperature=0,
        )
    content = clean_json(raw)
    try:
        lines = json.loads(content)
        if isinstance(lines, list):
            return lines
    except Exception:
        alert("Не распарсил JSON сметы", raw=content[:300])
    return []


def generate_estimate(state, catalog=None, index=None):
    card = state["object_card"]
    lines = propose_estimate_lines(state, catalog=catalog)
    reserve = card["estimate"].get("reserve_percent", 12)
    card["estimate"] = build_estimate(lines, reserve_percent=reserve, index=index)
    return card["estimate"]


# =========================
# STAGE ROUTING
# =========================

def goal_ready(card):
    return bool(card["passport"].get("goal"))


def discovery_ready(card):
    p = card["passport"]
    return bool(p.get("object_type")) and bool(p.get("total_area_sqm"))


def route_stage(state, intent, catalog=None, index=None):
    card = state["object_card"]
    stage = state["stage"]

    if stage == "goal":
        if goal_ready(card):
            next_stage(state)
        return stage_reply(state)

    if stage == "discovery":
        if discovery_ready(card):
            next_stage(state)
        return stage_reply(state)

    if stage == "rooms":
        if card["rooms"]:
            next_stage(state)
        return stage_reply(state)

    if stage == "before":
        if card["before"]["surfaces"]:
            next_stage(state)
        return stage_reply(state)

    if stage == "after":
        if intent == "approval":
            next_stage(state)
            generate_estimate(state, catalog=catalog, index=index)
        return stage_reply(state)

    if stage == "estimate":
        if not card["estimate"]["sections"]:
            generate_estimate(state, catalog=catalog, index=index)
        if intent == "approval":
            card["meta"]["status"] = "agreed"
            next_stage(state)
        return stage_reply(state)

    return stage_reply(state)


# =========================
# MAIN ENTRY
# =========================

def chat(user_message, state, image=None, catalog=None, index=None, approved=False):
    """Один ход диалога. Возвращает контракт фронта.

    catalog / index — опц. источник цен из БД (см. estimate.build_estimate).
    approved — явная кнопка «согласовать» с фронта (приравнивается к intent approval).
    """
    with monitor_stage("chat_turn", stage_name=state.get("stage"), has_image=bool(image)):
        add_user_message(state, user_message, image)
        update_object_card(user_message, state)
        intent = detect_intent(user_message)
        if approved:
            intent = "approval"
        reply_text = route_stage(state, intent, catalog=catalog, index=index)
        add_assistant_message(state, reply_text)

    estimate_ready = bool(state["object_card"]["estimate"]["sections"])
    return {
        "reply_text": reply_text,
        "emotion": emotion_for(state, intent, estimate_ready),
        "stage": state["stage"],
        "object_card": state["object_card"],
        "estimate_ready": estimate_ready,
    }
