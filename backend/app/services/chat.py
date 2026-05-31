from collections import defaultdict
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import Request, UploadFile, WebSocket
from sqlalchemy.orm import Session

from app import schemas
from app.dependencies import ApiError
from app.models import Chat, ChatMessage, Claim, User
from app.repositories.chat import ChatRepository
from app.repositories.claims import ClaimRepository
from app.repositories.notifications import NotificationRepository
from app.services.authorization import AuthorizationPolicy
from app.services.notifications import NotificationService


class ChatService:
    upload_dir = Path("app/static/uploads")
    allowed_file_types = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "application/pdf": ".pdf",
    }
    max_file_size = 8 * 1024 * 1024

    def __init__(self, db: Session) -> None:
        self.claims = ClaimRepository(db)
        self.chats = ChatRepository(db)
        self.notification_repository = NotificationRepository(db)
        self.notifications = NotificationService(db)

    def get_chat_claim(self, claim_id: UUID, current_user: User) -> Claim:
        claim = self.claims.get(claim_id)
        if not claim:
            raise ApiError.not_found("Claim")
        if not AuthorizationPolicy.can_chat(claim, current_user):
            raise ApiError.forbidden("Chat is available only for accepted claims")
        return claim

    def list_messages(self, claim_id: UUID, current_user: User, skip: int, limit: int) -> list[ChatMessage]:
        claim = self.get_chat_claim(claim_id, current_user)
        chat = self.chats.get_or_create_for_claim(claim)
        return self.chats.list_messages(chat, skip=skip, limit=limit)

    def get_room_info(self, claim_id: UUID, current_user: User) -> schemas.ChatRoomInfo:
        claim = self.get_chat_claim(claim_id, current_user)
        chat = self.chats.get_or_create_for_claim(claim)
        return schemas.ChatRoomInfo(
            claim_id=claim.id,
            item_id=claim.item_id,
            chat_id=chat.id,
            participants=[claim.item.owner_id, claim.claimant_id],
            is_realtime_enabled=True,
            encryption="client-side end-to-end; server stores ciphertext in chat_messages.isi_pesan",
            active_connections=chat_manager.count_for_chat(chat.id),
            status=claim.status,
            item=claim.item,
            claim_user=claim.claimant,
            item_user_id=claim.item.owner_id,
        )

    def send_message(self, claim: Claim, sender_id: UUID, message_in: schemas.ChatMessageCreate) -> ChatMessage:
        chat = self.chats.get_or_create_for_claim(claim)
        message = self.chats.create_message(
            chat_id=chat.id,
            sender_id=sender_id,
            content=message_in.ciphertext or message_in.content,
            image_attachment=str(message_in.image_attachment) if message_in.image_attachment else None,
        )
        receiver_id = claim.item.owner_id if sender_id == claim.claimant_id else claim.claimant_id
        self.notification_repository.delete_chat_notification_for_claim(user_id=receiver_id, claim_id=claim.id)
        self.notifications.create(
            user_id=receiver_id,
            actor_id=sender_id,
            type="chat_new",
            title="Pesan baru",
            message=f"Pesan baru terkait {claim.item.title}.",
            target_url=f"/messages/{claim.id}",
            item_id=claim.item_id,
            claim_id=claim.id,
        )
        return message

    def send_message_by_claim_id(self, claim_id: UUID, current_user: User, message_in: schemas.ChatMessageCreate) -> ChatMessage:
        claim = self.get_chat_claim(claim_id, current_user)
        return self.send_message(claim, sender_id=current_user.id, message_in=message_in)

    async def upload_attachment(self, claim_id: UUID, current_user: User, request: Request, file: UploadFile) -> schemas.PostImageCreate:
        self.get_chat_claim(claim_id, current_user)
        extension = self.allowed_file_types.get(file.content_type or "")
        if extension is None:
            raise ApiError.bad_request("File chat harus berupa gambar JPG, PNG, WEBP, GIF, atau PDF")
        content = await file.read()
        if len(content) > self.max_file_size:
            raise ApiError.bad_request("Ukuran file chat maksimal 8 MB")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"chat-{uuid4()}{extension}"
        target = self.upload_dir / filename
        target.write_bytes(content)
        return schemas.PostImageCreate(image_url=str(request.base_url).rstrip("/") + f"/static/uploads/{filename}")

    def get_realtime_session(self, claim_id: UUID, user: User) -> tuple[Claim, Chat]:
        claim = self.get_chat_claim(claim_id, user)
        return claim, self.chats.get_or_create_for_claim(claim)


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[UUID, list[WebSocket]] = defaultdict(list)

    async def connect(self, chat_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, chat_id: UUID, websocket: WebSocket) -> None:
        connections = self.active_connections.get(chat_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and chat_id in self.active_connections:
            del self.active_connections[chat_id]

    async def broadcast_to_chat(self, chat_id: UUID, payload: dict) -> None:
        stale_connections: list[WebSocket] = []
        for connection in list(self.active_connections.get(chat_id, [])):
            try:
                await connection.send_json(payload)
            except RuntimeError:
                stale_connections.append(connection)
        for connection in stale_connections:
            self.disconnect(chat_id, connection)

    def count_for_chat(self, chat_id: UUID) -> int:
        return len(self.active_connections.get(chat_id, []))


chat_manager = ChatConnectionManager()
