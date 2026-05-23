from uuid import UUID

from app.models import Notification
from app.services.base import BaseRepository


class NotificationRepository(BaseRepository):
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
        notification = Notification(
            user_id=user_id,
            actor_id=actor_id,
            type=type,
            title=title,
            message=message,
            target_url=target_url,
            item_id=item_id,
            claim_id=claim_id,
        )
        return self.save(notification)

    def delete_chat_notification_for_claim(self, user_id: UUID, claim_id: UUID) -> None:
        self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.claim_id == claim_id,
            Notification.type == "chat_new",
        ).delete(synchronize_session=False)
        self.db.commit()

    def list_for_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def unread_count(self, user_id: UUID) -> int:
        return self.db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read.is_(False)).count()

    def get_for_user(self, notification_id: UUID, user_id: UUID) -> Notification | None:
        return (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )

    def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        return self.save(notification)

    def mark_all_read(self, user_id: UUID) -> None:
        self.db.query(Notification).filter(Notification.user_id == user_id).update(
            {Notification.is_read: True},
            synchronize_session=False,
        )
        self.db.commit()
