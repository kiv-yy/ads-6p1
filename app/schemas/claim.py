from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, computed_field, ConfigDict, model_validator

from app.models import ClaimStatus
from app.schemas.post import ItemRead
from app.schemas.user import UserRead


def normalize_claim_status(value: str) -> str:
    normalized = value.lower()
    return {"pending": "pending", "accepted": "diterima", "rejected": "ditolak"}.get(normalized, normalized)


class ClaimCreate(BaseModel):
    item_id: UUID
    message: str | None = Field(default=None, max_length=5000)
    description: str | None = Field(default=None, max_length=5000)
    claimant_name: str | None = Field(default=None, max_length=100)
    proof_image_url: HttpUrl | None = None
    additional_info: dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def accept_post_id(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        if "post_id" in payload and "item_id" not in payload:
            payload["item_id"] = payload["post_id"]
        if "alasan_kepemilikan" in payload and "message" not in payload:
            payload["message"] = payload["alasan_kepemilikan"]
        if "nama_pengklaim" in payload and "claimant_name" not in payload:
            payload["claimant_name"] = payload["nama_pengklaim"]
        if "bukti_foto" in payload and "proof_image_url" not in payload:
            payload["proof_image_url"] = payload["bukti_foto"]
        return payload

    @model_validator(mode="after")
    def normalize_message(self) -> "ClaimCreate":
        if self.message is None:
            self.message = self.description
        return self


class ClaimUpdate(BaseModel):
    status: ClaimStatus

    @model_validator(mode="before")
    @classmethod
    def accept_old_status_names(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        if "status" in payload and isinstance(payload["status"], str):
            payload["status"] = normalize_claim_status(payload["status"])
        return payload


class ClaimRead(BaseModel):
    id: UUID
    item_id: UUID
    claimant_id: UUID
    claimant_name: str
    message: str
    proof_image_url: str | None = None
    status: ClaimStatus
    created_at: datetime
    latest_message_at: datetime | None = None
    latest_message_preview: str | None = None
    item: ItemRead | None = None
    claimant: UserRead | None = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def claim_id(self) -> UUID:
        return self.id

    @computed_field
    @property
    def post_id(self) -> UUID:
        return self.item_id

    @computed_field
    @property
    def claimer_id(self) -> UUID:
        return self.claimant_id

    @computed_field
    @property
    def claim_user_id(self) -> UUID:
        return self.claimant_id

    @computed_field
    @property
    def item_user_id(self) -> UUID | None:
        return self.item.owner_id if self.item else None

    @computed_field
    @property
    def claim_user(self) -> UserRead | None:
        return self.claimant
