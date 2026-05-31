from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.models import ReportStatus
from app.schemas.post import ItemRead
from app.schemas.user import UserRead


class ReportCreate(BaseModel):
    post_id: UUID | None = None
    reason: str = Field(min_length=3, max_length=5000)

    @model_validator(mode="before")
    @classmethod
    def accept_indonesian_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        if "item_id" in payload and "post_id" not in payload:
            payload["post_id"] = payload["item_id"]
        if "alasan_report" in payload and "reason" not in payload:
            payload["reason"] = payload["alasan_report"]
        return payload


class ReportUpdate(BaseModel):
    status: ReportStatus


class ReportRead(BaseModel):
    id: UUID
    reporter_id: UUID
    post_id: UUID | None = None
    reason: str
    status: ReportStatus
    created_at: datetime
    post: ItemRead | None = None
    reporter: UserRead | None = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def report_id(self) -> UUID:
        return self.id
