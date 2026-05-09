from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

from app.models import ClaimStatus, ItemCategory, ItemStatus, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_ipb_email(cls, value: str) -> str:
        allowed_domains = ("@apps.ipb.ac.id", "@ipb.ac.id", "@student.ipb.ac.id")
        if not value.lower().endswith(allowed_domains):
            raise ValueError("Gunakan email institusi IPB.")
        return value.lower()


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_blocked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserModerationUpdate(BaseModel):
    is_blocked: bool


class ItemBase(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10)
    category: ItemCategory
    location: str = Field(min_length=2, max_length=150)
    timestamp: datetime | None = None
    image_url: HttpUrl | None = None
    status: ItemStatus = ItemStatus.OPEN


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, min_length=10)
    category: ItemCategory | None = None
    location: str | None = Field(default=None, min_length=2, max_length=150)
    timestamp: datetime | None = None
    image_url: HttpUrl | None = None
    status: ItemStatus | None = None


class ItemRead(ItemBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimCreate(BaseModel):
    item_id: int
    message: str | None = Field(default=None, max_length=2000)


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

    model_config = ConfigDict(from_attributes=True)


class ChatMessageCreate(BaseModel):
    ciphertext: str = Field(min_length=1, max_length=8000)
    nonce: str = Field(min_length=8, max_length=255)
    algorithm: str = Field(default="X25519+AES-256-GCM", max_length=100)
    sender_public_key: str | None = Field(default=None, max_length=2000)


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
