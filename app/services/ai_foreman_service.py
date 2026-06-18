"""
Сервис ИИ-прораба.

Заменяет прежнюю заглушку: гоняет настоящий агент (app/agents/ai_foreman_agent),
хранит состояние диалога в треде (context_json), подмешивает опросы и комнаты
из редактора карты, и отдаёт единый артефакт object_card + смету + этап.
"""
import copy

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents import ai_foreman_agent as agent
from app.agents import llm_client
from app.agents.ai_foreman_agent import merge_dict
from app.models.ai_foreman import AIForemanMessageRole, AIForemanThread
from app.repositories.ai_foreman_repository import AIForemanRepository
from app.schemas.ai_foreman import (
    AIForemanThreadCreate,
    AIForemanMessageCreate,
    AIForemanChatRequest,
)


class AIForemanService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AIForemanRepository(db)

    # ---------- доступ / тред ----------

    def _check_thread_access(self, user_id: int, thread_id: int) -> AIForemanThread:
        thread = self.repo.get_thread(thread_id)
        if not thread:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Тред ИИ-прораба не найден")
        if thread.user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Нет доступа к этому треду")
        return thread

    def get_threads(self, user_id: int):
        return self.repo.get_user_threads(user_id)

    def create_thread(self, user_id: int, data: AIForemanThreadCreate):
        return self.repo.create_thread(user_id=user_id, title=data.title)

    def get_messages(self, user_id: int, thread_id: int):
        self._check_thread_access(user_id, thread_id)
        return self.repo.get_messages(thread_id)

    # ---------- состояние ----------

    def _load_state(self, thread: AIForemanThread) -> dict:
        state = thread.context_json
        if not state or "object_card" not in state:
            return agent.create_empty_state()
        # подстраховка от частично заполненного состояния
        state.setdefault("stage", "goal")
        state.setdefault("history", [])
        return copy.deepcopy(state)

    def _is_fresh(self, state: dict) -> bool:
        return not state.get("history")

    # ---------- подмешивание данных платформы ----------

    def _seed_from_survey(self, card: dict, survey: dict | None):
        """surveys → стартовый object_card (бриф)."""
        if not survey:
            return
        # кладём сырой опрос, чтобы модель могла на него опереться
        card["meta"]["survey"] = survey
        p = card["passport"]
        mapping = {
            "object_type": ["object_type", "premise_type", "type"],
            "city": ["city", "town"],
            "district": ["district", "region"],
            "total_area_sqm": ["total_area_sqm", "total_area_m2", "area", "area_m2"],
            "ceiling_height_m": ["ceiling_height_m", "ceiling_height", "height"],
            "rooms_count": ["rooms_count", "rooms"],
            "goal": ["goal"],
        }
        for target, keys in mapping.items():
            if p.get(target):
                continue
            for k in keys:
                if survey.get(k) not in (None, "", []):
                    p[target] = survey[k]
                    break

    def _merge_premise_rooms(self, card: dict, premise_rooms: list | None):
        """Комнаты из редактора карты ↔ object_card.rooms (двусторонняя связка).

        Диана: пользователь нарисовал форму квартиры и назвал комнаты — ИИ
        должен знать их размеры и уметь поправить цифры по диалогу.
        """
        if not premise_rooms:
            return
        rooms = card.setdefault("rooms", [])
        by_name = {str(r.get("name", "")).strip().lower(): r for r in rooms if r.get("name")}

        for pr in premise_rooms:
            name = pr.get("name") or pr.get("title") or pr.get("type") or pr.get("label")
            if not name:
                continue
            width = pr.get("width_m") or pr.get("width")
            length = pr.get("length_m") or pr.get("length")
            area = pr.get("area_sqm") or pr.get("area_m2") or pr.get("area")
            key = str(name).strip().lower()
            existing = by_name.get(key)
            if existing:
                existing.setdefault("name", name)
                if width and not existing.get("width_m"):
                    existing["width_m"] = width
                if length and not existing.get("length_m"):
                    existing["length_m"] = length
                if area and not existing.get("area_sqm"):
                    existing["area_sqm"] = area
            else:
                room = {"id": pr.get("id") or key, "name": name}
                if width:
                    room["width_m"] = width
                if length:
                    room["length_m"] = length
                if area:
                    room["area_sqm"] = area
                rooms.append(room)
                by_name[key] = room

    # ---------- выходные артефакты для фронта ----------

    @staticmethod
    def _project_map_data(card: dict) -> dict:
        """object_card.rooms (с размерами) → данные для редактора карты."""
        rooms_out = []
        total = 0.0
        for r in card.get("rooms", []):
            area = r.get("area_sqm")
            if isinstance(area, (int, float)):
                total += area
            rooms_out.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "width_m": r.get("width_m"),
                "length_m": r.get("length_m"),
                "area_m2": area,
            })
        return {
            "source": "ai_foreman",
            "rooms": rooms_out,
            "total_area_m2": round(total, 2) if total else None,
        }

    @staticmethod
    def _add_front_mirrors(card: dict):
        """Зеркальные поля под текущий фронт (scene-панель читает *_m2/min_rub)."""
        p = card.get("passport", {})
        if p.get("total_area_sqm") and not p.get("total_area_m2"):
            p["total_area_m2"] = p["total_area_sqm"]
        for r in card.get("rooms", []):
            if r.get("area_sqm") and not r.get("area_m2"):
                r["area_m2"] = r["area_sqm"]

    @staticmethod
    def _sanitize_history(state: dict):
        """Перед сохранением убираем тяжёлые data-URL фото из истории:
        оставляем только текст (object_card уже впитал нужное)."""
        clean = []
        for msg in state.get("history", []):
            content = msg.get("content")
            if isinstance(content, list):
                text = " ".join(
                    part.get("text", "") for part in content
                    if isinstance(part, dict) and part.get("type") == "text"
                ).strip()
                clean.append({"role": msg["role"], "content": text or "[фото]"})
            else:
                clean.append(msg)
        state["history"] = clean

    # ---------- общий ход диалога ----------

    def _run_turn(self, thread, message, image, *, object_card=None,
                  survey=None, premise_rooms=None, approved=False, persist_messages=True):
        if not llm_client.is_configured():
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "ИИ-провайдер не настроен: задайте AI_API_KEY (облако) или "
                "AI_BASE_URL на локальный сервер (Ollama/vLLM).",
            )

        state = self._load_state(thread)

        # seed только на свежем треде, кроме комнат карты (их мёржим всегда)
        if self._is_fresh(state):
            if object_card:
                merge_dict(state["object_card"], object_card)
            self._seed_from_survey(state["object_card"], survey)
        self._merge_premise_rooms(state["object_card"], premise_rooms)

        try:
            result = agent.chat(message, state, image=image, approved=approved)
        except llm_client.LLMNotConfigured as e:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
        except llm_client.LLMRequestError as e:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Ошибка ИИ-провайдера: {e}")

        # сохраняем состояние и историю сообщений
        self._sanitize_history(state)
        self.repo.set_context(thread, state)
        if persist_messages:
            self.repo.create_message(thread.id, AIForemanMessageRole.USER, message or "[фото]")
            self.repo.create_message(thread.id, AIForemanMessageRole.ASSISTANT, result["reply_text"])

        self._add_front_mirrors(result["object_card"])
        return result

    # ---------- эндпоинт /ai-foreman/chat (контракт фронта) ----------

    def chat(self, user_id: int, req: AIForemanChatRequest) -> dict:
        if req.thread_id:
            thread = self._check_thread_access(user_id, req.thread_id)
        else:
            title = (req.message or "ИИ-прораб").strip()[:60] or "ИИ-прораб"
            thread = self.repo.create_thread(user_id=user_id, title=title)

        result = self._run_turn(
            thread, req.message, req.image,
            object_card=req.object_card, survey=req.survey,
            premise_rooms=req.premise_rooms, approved=req.approved,
        )

        card = result["object_card"]
        return {
            "text": result["reply_text"],
            "reply_text": result["reply_text"],
            "emotion": result["emotion"],
            "stage": result["stage"],
            "object_card": card,
            "estimate_ready": result["estimate_ready"],
            "thread_id": thread.id,
            "project_map_data": self._project_map_data(card),
            "source": "ai_foreman",
        }

    # ---------- эндпоинт /threads/{id}/messages (контракт брифа) ----------

    def send_message(self, user_id: int, thread_id: int, data: AIForemanMessageCreate):
        thread = self._check_thread_access(user_id, thread_id)

        user_message = self.repo.create_message(
            thread_id, AIForemanMessageRole.USER, data.body
        )
        result = self._run_turn(
            thread, data.body, data.image, persist_messages=False
        )
        assistant_message = self.repo.create_message(
            thread_id, AIForemanMessageRole.ASSISTANT, result["reply_text"]
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "reply_text": result["reply_text"],
            "emotion": result["emotion"],
            "stage": result["stage"],
            "object_card": result["object_card"],
            "estimate_ready": result["estimate_ready"],
        }
