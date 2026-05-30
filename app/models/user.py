from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UserRole(str, Enum):
    STUDENT = "mahasiswa"
    ADMIN = "admin"


class AccountStatus(str, Enum):
    ACTIVE = "aktif"
    INACTIVE = "nonaktif"
    BANNED = "banned"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column("user_id", primary_key=True, default=uuid4, index=True)
    full_name: Mapped[str] = mapped_column("nama", String(100), nullable=False)
    username: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    email: Mapped[str] = mapped_column("email_ipb", String(150), unique=True, index=True, nullable=False)
    nim: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    faculty: Mapped[str | None] = mapped_column("fakultas", String(100), nullable=True)
    hashed_password: Mapped[str] = mapped_column("password", String(255), nullable=False)
    profile_photo: Mapped[str | None] = mapped_column("foto_profile", Text, nullable=True)
    role: Mapped[str] = mapped_column(String(30), default=UserRole.STUDENT.value, nullable=False)
    account_status: Mapped[str] = mapped_column(
        "status_akun",
        String(30),
        default=AccountStatus.ACTIVE.value,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    posts: Mapped[list["Item"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    claims: Mapped[list["Claim"]] = relationship(
        back_populates="claimant",
        foreign_keys="Claim.claimant_id",
        cascade="all, delete-orphan",
    )
    sent_chats: Mapped[list["Chat"]] = relationship(
        back_populates="sender",
        foreign_keys="Chat.sender_id",
        cascade="all, delete-orphan",
    )
    received_chats: Mapped[list["Chat"]] = relationship(
        back_populates="receiver",
        foreign_keys="Chat.receiver_id",
        cascade="all, delete-orphan",
    )
