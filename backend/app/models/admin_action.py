from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AdminAction(Base):
    __tablename__ = "admin_actions"

    id: Mapped[UUID] = mapped_column("action_id", primary_key=True, default=uuid4, index=True)
    admin_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=False)
    post_id: Mapped[UUID | None] = mapped_column(ForeignKey("posts.post_id"), index=True, nullable=True)
    user_target_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=True)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
