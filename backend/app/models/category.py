from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column("category_id", primary_key=True, default=uuid4, index=True)
    name: Mapped[str] = mapped_column("nama_kategori", String(100), unique=True, nullable=False)

    posts: Mapped[list["Item"]] = relationship(back_populates="category_ref")
