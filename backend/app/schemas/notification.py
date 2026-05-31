from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    id: UUID
    user_id: UUID
    actor_id: UUID | None = None
    type: str
    title: str
    message: str
    target_url: str
    item_id: UUID | None = None
    claim_id: UUID | None = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationSummary(BaseModel):
    unread_count: int
