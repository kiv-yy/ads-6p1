from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = (CheckConstraint("sender_id <> receiver_id", name="chk_chats_different_users"),)

    id: Mapped[UUID] = mapped_column("chat_id", primary_key=True, default=uuid4, index=True)
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.post_id"), index=True, nullable=False)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=False)
    receiver_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    post: Mapped["Item"] = relationship(back_populates="chats")
    sender: Mapped["User"] = relationship(back_populates="sent_chats", foreign_keys=[sender_id])
    receiver: Mapped["User"] = relationship(back_populates="received_chats", foreign_keys=[receiver_id])
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="chat", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint("isi_pesan IS NOT NULL OR image_attachment IS NOT NULL", name="chk_message_has_content"),
    )

    id: Mapped[UUID] = mapped_column("message_id", primary_key=True, default=uuid4, index=True)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.chat_id"), index=True, nullable=False)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=False)
    content: Mapped[str | None] = mapped_column("isi_pesan", Text, nullable=True)
    image_attachment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("sent_at", DateTime(timezone=True), server_default=func.now())
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    chat: Mapped[Chat] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()
