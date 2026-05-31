from uuid import UUID

from app.models import AdminAction, AdminActionType
from app.services.base import BaseRepository


class AdminActionRepository(BaseRepository):
    def log(
        self,
        admin_id: UUID,
        action_type: AdminActionType,
        post_id: UUID | None = None,
        user_target_id: UUID | None = None,
        notes: str | None = None,
    ) -> AdminAction:
        action = AdminAction(
            admin_id=admin_id,
            post_id=post_id,
            user_target_id=user_target_id,
            action_type=action_type.value,
            notes=notes,
        )
        return self.save(action)
