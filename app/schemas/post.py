from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field, model_validator

from app.models import ItemStatus, ItemType
from app.schemas.user import UserRead


def normalize_item_type(value: str) -> str:
    normalized = value.lower()
    return {"lost": "kehilangan", "found": "temuan"}.get(normalized, normalized)


def normalize_item_status(value: str) -> str:
    normalized = value.lower()
    return {
        "open": "aktif",
        "in progress": "aktif",
        "resolved": "selesai",
        "deleted": "dihapus",
    }.get(normalized, normalized)


class PostImageCreate(BaseModel):
    image_url: HttpUrl


class PostImageRead(BaseModel):
    id: UUID
    post_id: UUID
    image_url: str

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def image_id(self) -> UUID:
        return self.id


class ItemBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    category: str = Field(default="Lainnya", max_length=100)
    type: ItemType = ItemType.LOST
    location: str | None = Field(default=None, max_length=255)
    timestamp: datetime | None = None
    image_url: HttpUrl | None = None
    status: ItemStatus = ItemStatus.OPEN
    traits: str | None = Field(default=None, max_length=2000)
    is_anonymous: bool = False


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
            payload["type"] = normalize_item_type(payload["type"])
        if "status" in payload and isinstance(payload["status"], str):
            payload["status"] = normalize_item_status(payload["status"])
        if "category" not in payload and payload.get("type"):
            payload["category"] = "Lainnya"
        if not payload.get("description") and payload.get("traits"):
            payload["description"] = payload["traits"]
        return payload


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    category: str | None = Field(default=None, max_length=100)
    type: ItemType | None = None
    location: str | None = Field(default=None, max_length=255)
    timestamp: datetime | None = None
    image_url: HttpUrl | None = None
    status: ItemStatus | None = None
    traits: str | None = Field(default=None, max_length=2000)
    is_anonymous: bool | None = None

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
            payload["type"] = normalize_item_type(payload["type"])
        if "status" in payload and isinstance(payload["status"], str):
            payload["status"] = normalize_item_status(payload["status"])
        return payload


class ItemRead(BaseModel):
    id: UUID
    owner_id: UUID
    category_id: UUID
    title: str
    description: str | None = None
    category: str
    type: ItemType
    location: str | None = None
    timestamp: datetime | None = None
    image_url: str | None = None
    status: ItemStatus
    traits: str | None = None
    is_anonymous: bool
    event_date: date | None = None
    event_time: time | None = None
    created_at: datetime
    owner: UserRead | None = None
    images: list[PostImageRead] = []

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def from_orm_post(cls, data: Any) -> Any:
        if isinstance(data, dict) or not hasattr(data, "category_ref"):
            return data
        timestamp = data.created_at
        if data.event_date is not None:
            timestamp = datetime.combine(data.event_date, data.event_time or time.min)
        return {
            "id": data.id,
            "owner_id": data.owner_id,
            "category_id": data.category_id,
            "title": data.title,
            "description": data.description,
            "category": data.category_ref.name if data.category_ref else "Lainnya",
            "type": data.type,
            "location": data.location,
            "timestamp": timestamp,
            "image_url": data.images[0].image_url if data.images else None,
            "status": data.status,
            "traits": data.description,
            "is_anonymous": data.is_anonymous,
            "event_date": data.event_date,
            "event_time": data.event_time,
            "created_at": data.created_at,
            "owner": data.owner,
            "images": data.images,
        }

    @computed_field
    @property
    def post_id(self) -> UUID:
        return self.id

    @computed_field
    @property
    def user_id(self) -> UUID:
        return self.owner_id

    @computed_field
    @property
    def name(self) -> str:
        return self.title

    @computed_field
    @property
    def image(self) -> str | None:
        return self.image_url

    @computed_field
    @property
    def nama_barang(self) -> str:
        return self.title

    @computed_field
    @property
    def tipe_post(self) -> ItemType:
        return self.type

    @computed_field
    @property
    def status_post(self) -> ItemStatus:
        return self.status
