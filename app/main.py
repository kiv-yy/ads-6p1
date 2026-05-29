from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.db.database import Base, engine, seed_default_categories
from app.internal import admin
from app.models import AdminAction, Category, Chat, ChatMessage, Claim, Item, PostImage, Report, User
from app.routers import categories, chat, claims, notifications, posts, reports, users


Path("app/static/uploads").mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)
seed_default_categories()

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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(users.router)
app.include_router(categories.router)
app.include_router(posts.router)
app.include_router(claims.router)
app.include_router(reports.router)
app.include_router(chat.router)
app.include_router(notifications.router)
app.include_router(admin.router)

__all__ = ["app", "AdminAction", "Category", "Chat", "ChatMessage", "Claim", "Item", "PostImage", "Report", "User"]
