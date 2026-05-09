from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import PasswordService


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


class UserRepository(BaseRepository):
    def __init__(self, db: Session, password_service: PasswordService | None = None) -> None:
        super().__init__(db)
        self.password_service = password_service or PasswordService()

    def create(self, user_in: schemas.UserCreate) -> models.User:
        user = models.User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=self.password_service.hash(user_in.password),
        )
        return self.save(user)

    def get(self, user_id: int) -> models.User | None:
        return self.db.get(models.User, user_id)

    def get_by_email(self, email: str) -> models.User | None:
        return self.db.query(models.User).filter(models.User.email == email.lower()).first()

    def block(self, user: models.User) -> models.User:
        user.is_blocked = True
        return self.save(user)


class ItemRepository(BaseRepository):
    def create(self, item_in: schemas.ItemCreate, owner_id: int) -> models.Item:
        item_data = item_in.model_dump()
        if item_data["timestamp"] is None:
            item_data["timestamp"] = datetime.utcnow()
        if item_data["image_url"] is not None:
            item_data["image_url"] = str(item_data["image_url"])
        item_data["category"] = item_data["category"].value
        item_data["status"] = item_data["status"].value

        item = models.Item(**item_data, owner_id=owner_id)
        return self.save(item)

    def get(self, item_id: int) -> models.Item | None:
        return self.db.get(models.Item, item_id)

    def list(
        self,
        category: models.ItemCategory | None = None,
        location: str | None = None,
        keyword: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[models.Item]:
        query = self.db.query(models.Item)
        if category:
            query = query.filter(models.Item.category == category.value)
        if location:
            query = query.filter(models.Item.location.ilike(f"%{location}%"))
        if keyword:
            pattern = f"%{keyword}%"
            query = query.filter(or_(models.Item.title.ilike(pattern), models.Item.description.ilike(pattern)))
        return query.order_by(models.Item.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, item: models.Item, item_in: schemas.ItemUpdate) -> models.Item:
        update_data = item_in.model_dump(exclude_unset=True)
        if "image_url" in update_data and update_data["image_url"] is not None:
            update_data["image_url"] = str(update_data["image_url"])
        for field, value in update_data.items():
            setattr(item, field, value.value if hasattr(value, "value") else value)
        return self.save(item)


class ClaimRepository(BaseRepository):
    def create(self, claim_in: schemas.ClaimCreate, claimant_id: int) -> models.Claim:
        claim = models.Claim(
            item_id=claim_in.item_id,
            claimant_id=claimant_id,
            message=claim_in.message,
        )
        return self.save(claim)

    def get(self, claim_id: int) -> models.Claim | None:
        return self.db.get(models.Claim, claim_id)

    def list_for_user(self, user_id: int) -> list[models.Claim]:
        return (
            self.db.query(models.Claim)
            .join(models.Item)
            .filter(or_(models.Claim.claimant_id == user_id, models.Item.owner_id == user_id))
            .order_by(models.Claim.created_at.desc())
            .all()
        )

    def update_status(self, claim: models.Claim, status: models.ClaimStatus) -> models.Claim:
        claim.status = status.value
        if status == models.ClaimStatus.ACCEPTED:
            claim.item.status = models.ItemStatus.IN_PROGRESS.value
        return self.save(claim)


class ChatRepository(BaseRepository):
    def create_message(
        self,
        claim: models.Claim,
        sender_id: int,
        message_in: schemas.ChatMessageCreate,
    ) -> models.ChatMessage:
        message = models.ChatMessage(
            claim_id=claim.id,
            item_id=claim.item_id,
            sender_id=sender_id,
            content=message_in.ciphertext,
            nonce=message_in.nonce,
            algorithm=message_in.algorithm,
            sender_public_key=message_in.sender_public_key,
        )
        return self.save(message)


class AuthorizationPolicy:
    @staticmethod
    def can_manage_item(item: models.Item, user: models.User) -> bool:
        return item.owner_id == user.id or user.role == models.UserRole.ADMIN.value

    @staticmethod
    def can_access_claim(claim: models.Claim, user: models.User) -> bool:
        return claim.claimant_id == user.id or claim.item.owner_id == user.id

    @staticmethod
    def can_moderate_claim(claim: models.Claim, user: models.User) -> bool:
        return claim.item.owner_id == user.id or user.role == models.UserRole.ADMIN.value

    @staticmethod
    def can_chat(claim: models.Claim, user: models.User) -> bool:
        return AuthorizationPolicy.can_access_claim(claim, user) and claim.status == models.ClaimStatus.ACCEPTED.value
