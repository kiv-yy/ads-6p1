from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field, model_validator

from app.models import ClaimStatus
from app.schemas.post import ItemRead
from app.schemas.user import UserRead


class ChatMessageCreate(BaseModel):
    content: str | None = Field(default=None, max_length=8000)
    ciphertext: str | None = Field(default=None, max_length=8000)
    nonce: str = Field(default="client-managed", max_length=255)
    algorithm: str = Field(default="client-side-e2ee", max_length=100)
    sender_public_key: str | None = Field(default=None, max_length=2000)
    image_attachment: HttpUrl | None = None

    @model_validator(mode="after")
    def normalize_content(self) -> "ChatMessageCreate":
        if self.ciphertext is None:
            self.ciphertext = self.content
        if self.content is None:
            self.content = self.ciphertext
        return self


class ChatMessageRead(BaseModel):
    id: UUID
    claim_id: UUID
    item_id: UUID
    sender_id: UUID
    ciphertext: str
    nonce: str
    algorithm: str
    sender_public_key: str | None
    image_attachment: str | None = None
    created_at: datetime
    is_read: bool = False

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def from_orm_message(cls, data: Any) -> Any:
        if isinstance(data, dict) or not hasattr(data, "chat_id"):
            return data
        return {
            "id": data.id,
            "claim_id": data.chat_id,
            "item_id": data.chat.post_id,
            "sender_id": data.sender_id,
            "ciphertext": data.content or "",
            "nonce": "client-managed",
            "algorithm": "client-side-e2ee",
            "sender_public_key": None,
            "image_attachment": data.image_attachment,
            "created_at": data.created_at,
            "is_read": data.is_read,
        }

    @computed_field
    @property
    def message_id(self) -> UUID:
        return self.id

    @computed_field
    @property
    def chat_id(self) -> UUID:
        return self.claim_id

    @computed_field
    @property
    def user_id(self) -> UUID:
        return self.sender_id

    @computed_field
    @property
    def content(self) -> str:
        return self.ciphertext


class ChatWebSocketEvent(BaseModel):
    type: str = "encrypted_message"
    message: ChatMessageRead


class ChatRoomInfo(BaseModel):
    claim_id: UUID
    item_id: UUID
    chat_id: UUID
    participants: list[UUID]
    is_realtime_enabled: bool
    encryption: str
    active_connections: int
    status: ClaimStatus | None = None
    item: ItemRead | None = None
    claim_user: UserRead | None = None
    item_user_id: UUID | None = None
