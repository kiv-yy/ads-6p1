from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field, model_validator

from app.models import ClaimStatus, ItemStatus, ItemType
from app.schemas.user import UserRead


class ItemBase(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    description: str = Field(default="", max_length=5000)
    category: str = Field(default="Lainnya", max_length=100)
    type: ItemType = ItemType.LOST
    location: str = Field(min_length=2, max_length=150)
    timestamp: datetime | None = None
    image_url: HttpUrl | None = None
    status: ItemStatus = ItemStatus.OPEN
    traits: str | None = Field(default=None, max_length=2000)


class ItemCreate(ItemBase):
    @model_validator(mode="before")
    @classmethod
    def accept_frontend_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        if "name" in payload and "title" not in payload:
            payload["title"] = payload["name"]
        if "image" in payload and "image_url" not in payload:
            payload["image_url"] = payload["image"]
        if "type" in payload and isinstance(payload["type"], str):
            payload["type"] = payload["type"].upper()
        if not payload.get("description") and payload.get("traits"):
            payload["description"] = payload["traits"]
        return payload


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    category: str | None = Field(default=None, max_length=100)
    type: ItemType | None = None
    location: str | None = Field(default=None, min_length=2, max_length=150)
    timestamp: datetime | None = None
    image_url: HttpUrl | None = None
    status: ItemStatus | None = None
    traits: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        if "name" in payload and "title" not in payload:
            payload["title"] = payload["name"]
        if "image" in payload and "image_url" not in payload:
            payload["image_url"] = payload["image"]
        if "type" in payload and isinstance(payload["type"], str):
            payload["type"] = payload["type"].upper()
        return payload


class ItemRead(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: UserRead | None = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def name(self) -> str:
        return self.title

    @computed_field
    @property
    def image(self) -> str | None:
        return str(self.image_url) if self.image_url else None

    @computed_field
    @property
    def user_id(self) -> int:
        return self.owner_id

    @computed_field
    @property
    def user(self) -> UserRead | None:
        return self.owner


class ClaimCreate(BaseModel):
    item_id: int
    message: str | None = Field(default=None, max_length=2000)
    description: str | None = Field(default=None, max_length=2000)
    additional_info: dict[str, Any] | None = None

    @model_validator(mode="after")
    def normalize_message(self) -> "ClaimCreate":
        if self.message is None:
            self.message = self.description
        return self


class ClaimUpdate(BaseModel):
    status: ClaimStatus


class ClaimRead(BaseModel):
    id: int
    item_id: int
    claimant_id: int
    message: str | None
    status: ClaimStatus
    created_at: datetime
    updated_at: datetime | None
    item: ItemRead | None = None
    claimant: UserRead | None = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def claim_user_id(self) -> int:
        return self.claimant_id

    @computed_field
    @property
    def item_user_id(self) -> int | None:
        return self.item.owner_id if self.item else None

    @computed_field
    @property
    def claim_user(self) -> UserRead | None:
        return self.claimant


class ChatMessageCreate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=8000)
    ciphertext: str | None = Field(default=None, min_length=1, max_length=8000)
    nonce: str = Field(default="plaintext-dev", min_length=1, max_length=255)
    algorithm: str = Field(default="PLAINTEXT_DEV", max_length=100)
    sender_public_key: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def normalize_content(self) -> "ChatMessageCreate":
        if self.ciphertext is None:
            self.ciphertext = self.content
        if self.content is None:
            self.content = self.ciphertext
        return self


class ChatMessageRead(BaseModel):
    id: int
    claim_id: int
    item_id: int
    sender_id: int
    ciphertext: str
    nonce: str
    algorithm: str
    sender_public_key: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def user_id(self) -> int:
        return self.sender_id

    @computed_field
    @property
    def content(self) -> str:
        return self.ciphertext


class ChatWebSocketEvent(BaseModel):
    type: str = "encrypted_message"
    message: ChatMessageRead


class ChatRoomInfo(BaseModel):
    claim_id: int
    item_id: int
    participants: list[int]
    is_realtime_enabled: bool
    encryption: str
    active_connections: int
    status: ClaimStatus | None = None
    item: ItemRead | None = None
    claim_user: UserRead | None = None
    item_user_id: int | None = None
