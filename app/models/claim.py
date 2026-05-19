from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import ClaimStatus


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[UUID] = mapped_column("claim_id", primary_key=True, default=uuid4, index=True)
    item_id: Mapped[UUID] = mapped_column("post_id", ForeignKey("posts.post_id"), index=True, nullable=False)
    claimant_id: Mapped[UUID] = mapped_column("claimer_id", ForeignKey("users.user_id"), index=True, nullable=False)
    claimant_name: Mapped[str] = mapped_column("nama_pengklaim", String(100), nullable=False)
    message: Mapped[str] = mapped_column("alasan_kepemilikan", Text, nullable=False)
    proof_image_url: Mapped[str | None] = mapped_column("bukti_foto", Text, nullable=True)
    status: Mapped[str] = mapped_column("status_claim", String(30), default=ClaimStatus.PENDING.value, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    item: Mapped["Item"] = relationship(back_populates="claims")
    claimant: Mapped["User"] = relationship(back_populates="claims", foreign_keys=[claimant_id])
