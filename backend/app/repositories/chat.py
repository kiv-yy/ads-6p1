from uuid import UUID

from sqlalchemy import and_, or_

from app.models import Chat, ChatMessage, Claim
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository):
    def get_or_create_for_claim(self, claim: Claim) -> Chat:
        owner_id = claim.item.owner_id
        claimant_id = claim.claimant_id
        chat = (
            self.db.query(Chat)
            .filter(
                or_(
                    and_(Chat.sender_id == claimant_id, Chat.receiver_id == owner_id),
                    and_(Chat.sender_id == owner_id, Chat.receiver_id == claimant_id),
                )
            )
            .first()
        )
        if chat:
            return chat
        return self.save(Chat(post_id=claim.item_id, sender_id=claimant_id, receiver_id=owner_id))

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

    def list_messages(self, chat: Chat, skip: int = 0, limit: int = 50) -> list[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat.id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def latest_message_for_chat(self, chat: Chat) -> ChatMessage | None:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat.id)
            .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
            .first()
        )

    def create_message(self, chat_id: UUID, sender_id: UUID, content: str, image_attachment: str | None) -> ChatMessage:
        return self.save(
            ChatMessage(
                chat_id=chat_id,
                sender_id=sender_id,
                content=content,
                image_attachment=image_attachment,
            )
        )
