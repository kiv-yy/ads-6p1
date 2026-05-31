from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column("notification_id", primary_key=True, default=uuid4, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=True)
    type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    target_url: Mapped[str] = mapped_column(String(255), nullable=False)
    item_id: Mapped[UUID | None] = mapped_column(ForeignKey("posts.post_id"), index=True, nullable=True)
    claim_id: Mapped[UUID | None] = mapped_column(ForeignKey("claims.claim_id"), index=True, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    actor: Mapped["User | None"] = relationship(foreign_keys=[actor_id])
