from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket
from sqlalchemy import and_, or_

from app import schemas
from app.models import Chat, ChatMessage, Claim
from app.services.base import BaseRepository
from app.services.notifications import NotificationRepository


class ChatRepository(BaseRepository):
    def get_or_create_for_claim(self, claim: Claim) -> Chat:
        owner_id = claim.item.owner_id
        sender_id = claim.claimant_id
        chat = (
            self.db.query(Chat)
            .filter(
                or_(
                    and_(Chat.sender_id == sender_id, Chat.receiver_id == owner_id),
                    and_(Chat.sender_id == owner_id, Chat.receiver_id == sender_id),
                )
            )
            .first()
        )
        if chat:
            return chat
        chat = Chat(post_id=claim.item_id, sender_id=sender_id, receiver_id=owner_id)
        return self.save(chat)

    def get_for_claim(self, claim: Claim) -> Chat | None:
        return (
            self.db.query(Chat)
            .filter(
                or_(
                    and_(Chat.sender_id == claim.claimant_id, Chat.receiver_id == claim.item.owner_id),
                    and_(Chat.sender_id == claim.item.owner_id, Chat.receiver_id == claim.claimant_id),
                )
            )
            .first()
        )

    def list_messages(self, claim: Claim, skip: int = 0, limit: int = 50) -> list[ChatMessage]:
        chat = self.get_or_create_for_claim(claim)
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat.id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_message(self, claim: Claim, sender_id: UUID, message_in: schemas.ChatMessageCreate) -> ChatMessage:
        chat = self.get_or_create_for_claim(claim)
        message = ChatMessage(
            chat_id=chat.id,
            sender_id=sender_id,
            content=message_in.ciphertext or message_in.content,
            image_attachment=str(message_in.image_attachment) if message_in.image_attachment else None,
        )
        saved_message = self.save(message)
        receiver_id = claim.item.owner_id if sender_id == claim.claimant_id else claim.claimant_id
        notifications = NotificationRepository(self.db)
        notifications.delete_chat_notification_for_claim(user_id=receiver_id, claim_id=claim.id)
        notifications.create(
            user_id=receiver_id,
            actor_id=sender_id,
            type="chat_new",
            title="Pesan baru",
            message=f"Pesan baru terkait {claim.item.title}.",
            target_url=f"/messages/{claim.id}",
            item_id=claim.item_id,
            claim_id=claim.id,
        )
        return saved_message


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[UUID, list[WebSocket]] = defaultdict(list)

    async def connect(self, claim_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[claim_id].append(websocket)

    def disconnect(self, claim_id: UUID, websocket: WebSocket) -> None:
        connections = self.active_connections.get(claim_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and claim_id in self.active_connections:
            del self.active_connections[claim_id]

    async def broadcast_to_claim(self, claim_id: UUID, payload: dict) -> None:
        for connection in list(self.active_connections.get(claim_id, [])):
            await connection.send_json(payload)

    def count_for_claim(self, claim_id: UUID) -> int:
        return len(self.active_connections.get(claim_id, []))


chat_manager = ChatConnectionManager()
