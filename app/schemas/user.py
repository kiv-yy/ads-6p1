from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, field_validator

from app.models import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    faculty: str | None = Field(default=None, max_length=150)
    nim: str | None = Field(default=None, max_length=50)

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

    @computed_field
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


class UserModerationUpdate(BaseModel):
    is_blocked: bool


class AdminStats(BaseModel):
    total_users: int
    blocked_users: int
    total_items: int
    open_items: int
    resolved_items: int
    total_claims: int
    pending_claims: int
    accepted_claims: int
