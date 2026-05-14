from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UserRole(str, Enum):
    STUDENT = "Student"
    ADMIN = "Admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    faculty: Mapped[str | None] = mapped_column(String(150), nullable=True)
    nim: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(30), default=UserRole.STUDENT.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list["Item"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    claims: Mapped[list["Claim"]] = relationship(
        back_populates="claimant",
        foreign_keys="Claim.claimant_id",
        cascade="all, delete-orphan",
    )
