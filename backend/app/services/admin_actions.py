from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AdminAction, AdminActionType
from app.repositories.admin_actions import AdminActionRepository


class AdminActionService:
    def __init__(self, db: Session) -> None:
        self.actions = AdminActionRepository(db)

    def log(
        self,
        admin_id: UUID,
        action_type: AdminActionType,
        post_id: UUID | None = None,
        user_target_id: UUID | None = None,
        notes: str | None = None,
    ) -> AdminAction:
        return self.actions.create(
            AdminAction(
                admin_id=admin_id,
                post_id=post_id,
                user_target_id=user_target_id,
                action_type=action_type.value,
                notes=notes,
            )
        )
