from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import ReportStatus


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column("report_id", primary_key=True, default=uuid4, index=True)
    reporter_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=False)
    post_id: Mapped[UUID | None] = mapped_column(ForeignKey("posts.post_id"), index=True, nullable=True)
    reason: Mapped[str] = mapped_column("alasan_report", Text, nullable=False)
    status: Mapped[str] = mapped_column("status_report", String(30), default=ReportStatus.PENDING.value, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    post: Mapped["Item | None"] = relationship(back_populates="reports")
    reporter: Mapped["User"] = relationship()
