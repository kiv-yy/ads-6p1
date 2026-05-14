from collections import defaultdict
from datetime import datetime
from typing import Any

from fastapi import WebSocket
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import schemas
from app.models import ChatMessage, Claim, ClaimStatus, Item, ItemStatus, ItemType, User, UserRole


class BaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, entity: Any) -> Any:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: Any) -> None:
        self.db.delete(entity)
        self.db.commit()


class ItemRepository(BaseRepository):
    def create(self, item_in: schemas.ItemCreate, owner_id: int) -> Item:
        item_data = item_in.model_dump()
        if item_data["timestamp"] is None:
            item_data["timestamp"] = datetime.utcnow()
        if item_data["image_url"] is not None:
            item_data["image_url"] = str(item_data["image_url"])
        item_data["type"] = item_data["type"].value
        item_data["status"] = item_data["status"].value

        item = Item(**item_data, owner_id=owner_id)
        return self.save(item)

    def get(self, item_id: int) -> Item | None:
        return self.db.get(Item, item_id)

    def list(
        self,
        category: str | None = None,
        item_type: ItemType | None = None,
        status: ItemStatus | None = None,
        location: str | None = None,
        keyword: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Item]:
        query = self.db.query(Item)
        if category:
            query = query.filter(Item.category.ilike(f"%{category}%"))
        if item_type:
            query = query.filter(Item.type == item_type.value)
        if status:
            query = query.filter(Item.status == status.value)
        if location:
            query = query.filter(Item.location.ilike(f"%{location}%"))
        if keyword:
            pattern = f"%{keyword}%"
            query = query.filter(or_(Item.title.ilike(pattern), Item.description.ilike(pattern)))
        return query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, item: Item, item_in: schemas.ItemUpdate) -> Item:
        update_data = item_in.model_dump(exclude_unset=True)
        if "image_url" in update_data and update_data["image_url"] is not None:
            update_data["image_url"] = str(update_data["image_url"])
        for field, value in update_data.items():
            setattr(item, field, value.value if hasattr(value, "value") else value)
        return self.save(item)


class ClaimRepository(BaseRepository):
    def create(self, claim_in: schemas.ClaimCreate, claimant_id: int) -> Claim:
        claim = Claim(
            item_id=claim_in.item_id,
            claimant_id=claimant_id,
            message=claim_in.message,
        )
        return self.save(claim)

    def get(self, claim_id: int) -> Claim | None:
        return self.db.get(Claim, claim_id)

    def get_active_for_item_and_claimant(self, item_id: int, claimant_id: int) -> Claim | None:
        return (
            self.db.query(Claim)
            .filter(
                Claim.item_id == item_id,
                Claim.claimant_id == claimant_id,
                Claim.status.in_([ClaimStatus.PENDING.value, ClaimStatus.ACCEPTED.value]),
            )
            .first()
        )

    def list_for_item(self, item_id: int, skip: int = 0, limit: int = 50) -> list[Claim]:
        return (
            self.db.query(Claim)
            .filter(Claim.item_id == item_id)
            .order_by(Claim.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_for_user(self, user_id: int) -> list[Claim]:
        return (
            self.db.query(Claim)
            .join(Item)
            .filter(or_(Claim.claimant_id == user_id, Item.owner_id == user_id))
            .order_by(Claim.created_at.desc())
            .all()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Claim]:
        return self.db.query(Claim).order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()

    def update_status(self, claim: Claim, status: ClaimStatus) -> Claim:
        claim.status = status.value
        if status == ClaimStatus.ACCEPTED:
            claim.item.status = ItemStatus.IN_PROGRESS.value
        return self.save(claim)


class ChatRepository(BaseRepository):
    def list_messages(self, claim_id: int, skip: int = 0, limit: int = 50) -> list[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.claim_id == claim_id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_message(
        self,
        claim: Claim,
        sender_id: int,
        message_in: schemas.ChatMessageCreate,
    ) -> ChatMessage:
        message = ChatMessage(
            claim_id=claim.id,
            item_id=claim.item_id,
            sender_id=sender_id,
            content=message_in.ciphertext or "",
            nonce=message_in.nonce,
            algorithm=message_in.algorithm,
            sender_public_key=message_in.sender_public_key,
        )
        return self.save(message)


class AuthorizationPolicy:
    @staticmethod
    def can_manage_item(item: Item, user: User) -> bool:
        return item.owner_id == user.id or user.role == UserRole.ADMIN.value

    @staticmethod
    def can_access_claim(claim: Claim, user: User) -> bool:
        return claim.claimant_id == user.id or claim.item.owner_id == user.id

    @staticmethod
    def can_moderate_claim(claim: Claim, user: User) -> bool:
        return claim.item.owner_id == user.id or user.role == UserRole.ADMIN.value

    @staticmethod
    def can_chat(claim: Claim, user: User) -> bool:
        return AuthorizationPolicy.can_access_claim(claim, user) and claim.status == ClaimStatus.ACCEPTED.value


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, claim_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[claim_id].append(websocket)

    def disconnect(self, claim_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(claim_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and claim_id in self.active_connections:
            del self.active_connections[claim_id]

    async def broadcast_to_claim(self, claim_id: int, payload: dict) -> None:
        for connection in list(self.active_connections.get(claim_id, [])):
            await connection.send_json(payload)

    def count_for_claim(self, claim_id: int) -> int:
        return len(self.active_connections.get(claim_id, []))


chat_manager = ChatConnectionManager()
