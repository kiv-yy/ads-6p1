from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import ItemStatus, ItemType


class Item(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column("post_id", primary_key=True, default=uuid4, index=True)
    owner_id: Mapped[UUID] = mapped_column("user_id", ForeignKey("users.user_id"), index=True, nullable=False)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.category_id"), index=True, nullable=False)
    type: Mapped[str] = mapped_column("tipe_post", String(30), default=ItemType.LOST.value, index=True, nullable=False)
    title: Mapped[str] = mapped_column("nama_barang", String(200), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column("deskripsi", Text, nullable=True)
    location: Mapped[str | None] = mapped_column("lokasi", String(255), index=True, nullable=True)
    event_date: Mapped[date | None] = mapped_column("tanggal_kejadian", Date, nullable=True)
    event_time: Mapped[time | None] = mapped_column("waktu_kejadian", Time, nullable=True)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column("status_post", String(30), default=ItemStatus.OPEN.value, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="posts")
    category_ref: Mapped["Category"] = relationship(back_populates="posts")
    images: Mapped[list["PostImage"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    claims: Mapped[list["Claim"]] = relationship(back_populates="item", cascade="all, delete-orphan")
    chats: Mapped[list["Chat"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="post")


class PostImage(Base):
    __tablename__ = "post_images"

    id: Mapped[UUID] = mapped_column("image_id", primary_key=True, default=uuid4, index=True)
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.post_id"), index=True, nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)

    post: Mapped[Item] = relationship(back_populates="images")
