"""
Сервис уведомлений.

Пока заглушка: пишет в лог. Здесь будет реальная отправка push/почты, чтобы
мастер узнавал результат сделки (см. marketplace-backend-spec.md, п.4 шаг 5
и отчёт тестировщика, п.#2 — мастер не узнаёт, что его выбрали).
"""
import logging

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def notify_master_selected(self, master_user_id: int, project) -> None:
        """Мастера выбрали по проекту — уведомить его."""
        # TODO: интеграция с push (FCM/APNs) и/или e-mail.
        logger.info(
            "notify_master_selected: master_user_id=%s project_id=%s title=%r",
            master_user_id,
            getattr(project, "id", None),
            getattr(project, "title", None),
        )
