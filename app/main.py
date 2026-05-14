from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine, ensure_sqlite_compat_columns
from app.internal import admin
from app.models import ChatMessage, Claim, Item, User
from app.routers import items, users


Base.metadata.create_all(bind=engine)
ensure_sqlite_compat_columns()

app = FastAPI(
    title="IPB Lost & Found System",
    description="API boilerplate untuk mahasiswa IPB mencari barang hilang dan barang ditemukan di kampus.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(users.router)
app.include_router(items.router)
app.include_router(admin.router)

__all__ = ["app", "ChatMessage", "Claim", "Item", "User"]
