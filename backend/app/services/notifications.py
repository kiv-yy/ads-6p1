from uuid import UUID

from sqlalchemy.orm import Session

from app.dependencies import ApiError
from app.models import Notification
from app.repositories.notifications import NotificationRepository


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.notifications = NotificationRepository(db)

    def create(
        self,
        user_id: UUID,
        type: str,
        title: str,
        message: str,
        target_url: str,
        actor_id: UUID | None = None,
        item_id: UUID | None = None,
        claim_id: UUID | None = None,
    ) -> Notification:
        return self.notifications.create(
            Notification(
                user_id=user_id,
                actor_id=actor_id,
                type=type,
                title=title,
                message=message,
                target_url=target_url,
                item_id=item_id,
                claim_id=claim_id,
            )
        )

    def list_for_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Notification]:
        return self.notifications.list_for_user(user_id, skip=skip, limit=limit)

    def unread_count(self, user_id: UUID) -> int:
        return self.notifications.unread_count(user_id)

    def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        notification = self.notifications.get_for_user(notification_id, user_id)
        if not notification:
            raise ApiError.not_found("Notification")
        notification.is_read = True
        return self.notifications.save(notification)

    def mark_all_read(self, user_id: UUID) -> None:
        self.notifications.mark_all_read(user_id)
