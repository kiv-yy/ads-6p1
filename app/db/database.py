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


def ensure_sqlite_compat_columns() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    with engine.begin() as connection:
        user_columns = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(users)").fetchall()}
        item_columns = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(items)").fetchall()}

        if "faculty" not in user_columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN faculty VARCHAR(150)")
        if "nim" not in user_columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN nim VARCHAR(50)")

        if "type" not in item_columns:
            connection.exec_driver_sql("ALTER TABLE items ADD COLUMN type VARCHAR(20) DEFAULT 'LOST' NOT NULL")
        if "traits" not in item_columns:
            connection.exec_driver_sql("ALTER TABLE items ADD COLUMN traits TEXT")
        connection.exec_driver_sql("UPDATE items SET type = 'LOST' WHERE type IS NULL OR type = ''")
        connection.exec_driver_sql("UPDATE items SET type = 'LOST' WHERE category = 'Lost'")
        connection.exec_driver_sql("UPDATE items SET type = 'FOUND' WHERE category = 'Found'")
