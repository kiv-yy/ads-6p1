from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
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


def ensure_user_profile_columns() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    if "username" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(50)"))
