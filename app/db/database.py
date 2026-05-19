from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_default_categories() -> None:
    from app.models import Category

    default_categories = [
        "Elektronik",
        "Dompet / Tas",
        "Kartu Identitas",
        "Kunci",
        "Pakaian",
        "Lainnya",
    ]
    with SessionLocal() as db:
        existing = {name for (name,) in db.query(Category.name).all()}
        for name in default_categories:
            if name not in existing:
                db.add(Category(name=name))
        db.commit()
