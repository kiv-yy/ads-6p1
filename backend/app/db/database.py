from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


settings = get_settings()

engine = create_engine(settings.database_url)
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


def ensure_runtime_columns() -> None:
    inspector = inspect(engine)
    with engine.begin() as connection:
        if inspector.has_table("users"):
            user_columns = {column["name"] for column in inspector.get_columns("users")}
            if "username" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(50)"))
            if "jurusan" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN jurusan VARCHAR(100)"))
            if engine.dialect.name == "postgresql":
                connection.execute(text("ALTER TABLE users ALTER COLUMN nim DROP NOT NULL"))

        if inspector.has_table("chat_messages"):
            chat_columns = {column["name"] for column in inspector.get_columns("chat_messages")}
            if "image_attachment" not in chat_columns:
                connection.execute(text("ALTER TABLE chat_messages ADD COLUMN image_attachment TEXT"))


def ensure_user_profile_columns() -> None:
    ensure_runtime_columns()
