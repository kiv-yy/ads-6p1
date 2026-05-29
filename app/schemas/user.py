from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, field_validator

from app.models import AccountStatus, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: UUID | None = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    faculty: str | None = Field(default=None, max_length=100)
    nim: str = Field(min_length=3, max_length=20)

    @field_validator("email")
    @classmethod
    def validate_ipb_email(cls, value: str) -> str:
        if not value.lower().endswith("@apps.ipb.ac.id"):
            raise ValueError("Gunakan email institusi IPB dengan domain @apps.ipb.ac.id.")
        return value.lower()


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: UUID
    profile_photo: str | None = None
    role: UserRole
    account_status: AccountStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def user_id(self) -> UUID:
        return self.id

    @computed_field
    @property
    def nama(self) -> str:
        return self.full_name

    @computed_field
    @property
    def email_ipb(self) -> str:
        return str(self.email)

    @computed_field
    @property
    def fakultas(self) -> str | None:
        return self.faculty

    @computed_field
    @property
    def is_active(self) -> bool:
        return self.account_status == AccountStatus.ACTIVE

    @computed_field
    @property
    def is_blocked(self) -> bool:
        return self.account_status == AccountStatus.BANNED

    @computed_field
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


class RegisterResponse(BaseModel):
    user: UserRead
    message: str
    verification_url: str | None = None


class VerifyEmailResponse(BaseModel):
    message: str
    user: UserRead


class ResendVerificationRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_ipb_email(cls, value: str) -> str:
        if not value.lower().endswith("@apps.ipb.ac.id"):
            raise ValueError("Gunakan email institusi IPB dengan domain @apps.ipb.ac.id.")
        return value.lower()


class PasswordResetRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_ipb_email(cls, value: str) -> str:
        if not value.lower().endswith("@apps.ipb.ac.id"):
            raise ValueError("Hanya untuk email IPB dengan domain @apps.ipb.ac.id.")
        return value.lower()


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=10)
    new_password: str = Field(min_length=8, max_length=128)


class PasswordResetResponse(BaseModel):
    message: str
    reset_url: str | None = None


class UserModerationUpdate(BaseModel):
    is_blocked: bool
    notes: str | None = Field(default=None, max_length=1000)


class AdminStats(BaseModel):
    total_users: int
    blocked_users: int
    total_items: int
    open_items: int
    resolved_items: int
    total_claims: int
    pending_claims: int
    accepted_claims: int
    total_reports: int = 0
    pending_reports: int = 0
