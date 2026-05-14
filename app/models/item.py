from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ItemType(str, Enum):
    LOST = "LOST"
    FOUND = "FOUND"


class ItemCategory(str, Enum):
    LOST = "Lost"
    FOUND = "Found"


class ItemStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class ClaimStatus(str, Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), default=ItemType.LOST.value, index=True, nullable=False)
    traits: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ItemStatus] = mapped_column(String(30), default=ItemStatus.OPEN.value, index=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="items")
    claims: Mapped[list["Claim"]] = relationship(back_populates="item", cascade="all, delete-orphan")
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="item", cascade="all, delete-orphan")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True, nullable=False)
    claimant_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ClaimStatus] = mapped_column(String(30), default=ClaimStatus.PENDING.value, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    item: Mapped[Item] = relationship(back_populates="claims")
    claimant: Mapped["User"] = relationship(back_populates="claims", foreign_keys=[claimant_id])
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="claim", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"), index=True, nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True, nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    nonce: Mapped[str] = mapped_column(String(255), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(100), default="X25519+AES-256-GCM", nullable=False)
    sender_public_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    claim: Mapped[Claim] = relationship(back_populates="messages")
    item: Mapped[Item] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()

    @property
    def ciphertext(self) -> str:
        return self.content

    @property
    def user_id(self) -> int:
        return self.sender_id
