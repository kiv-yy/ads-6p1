from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import Request, UploadFile
from sqlalchemy.orm import Session

from app import schemas
from app.dependencies import ApiError
from app.models import Item, ItemStatus, ItemType, PostImage, User
from app.repositories.categories import CategoryRepository
from app.repositories.items import ItemRepository
from app.services.authorization import AuthorizationPolicy


class ItemService:
    upload_dir = Path("app/static/uploads")
    allowed_image_types = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}

    def __init__(self, db: Session) -> None:
        self.items = ItemRepository(db)
        self.categories = CategoryRepository(db)

    def create(self, item_in: schemas.ItemCreate, owner: User) -> Item:
        category = self.categories.get_or_create(item_in.category)
        timestamp = item_in.timestamp or datetime.utcnow()
        item = Item(
            owner_id=owner.id,
            category_id=category.id,
            type=item_in.type.value,
            title=item_in.title,
            description=item_in.description or item_in.traits,
            location=item_in.location,
            event_date=timestamp.date(),
            event_time=timestamp.time().replace(microsecond=0),
            is_anonymous=item_in.is_anonymous,
            status=item_in.status.value,
        )
        saved_item = self.items.create(item)
        if item_in.image_url is not None:
            self.items.add_image(saved_item, str(item_in.image_url))
        return saved_item

    async def upload_image(self, request: Request, file: UploadFile) -> schemas.PostImageCreate:
        extension = self.allowed_image_types.get(file.content_type or "")
        if extension is None:
            raise ApiError.bad_request("File harus berupa gambar JPG, PNG, WEBP, atau GIF")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4()}{extension}"
        target = self.upload_dir / filename
        target.write_bytes(await file.read())
        return schemas.PostImageCreate(image_url=str(request.base_url).rstrip("/") + f"/static/uploads/{filename}")

    def list(
        self,
        category: str | None,
        item_type: str | None,
        item_status: str | None,
        location: str | None,
        keyword: str | None,
        skip: int,
        limit: int,
        current_user: User | None,
    ) -> list[Item]:
        return self.items.list(
            category=category,
            item_type=ItemType(schemas.normalize_item_type(item_type)) if item_type else None,
            status=ItemStatus(schemas.normalize_item_status(item_status)) if item_status else None,
            location=location,
            keyword=keyword,
            skip=skip,
            limit=limit,
            current_user=current_user,
        )

    def get_public(self, item_id: UUID) -> Item:
        item = self.items.get(item_id)
        if not item or item.status == ItemStatus.DELETED.value:
            raise ApiError.not_found("Item")
        return item

    def update(self, item_id: UUID, item_in: schemas.ItemUpdate, current_user: User) -> Item:
        item = self._get_manageable_item(item_id, current_user, "Not enough permissions")
        update_data = item_in.model_dump(exclude_unset=True)
        if "category" in update_data and update_data["category"] is not None:
            item.category_id = self.categories.get_or_create(update_data.pop("category")).id
        if "timestamp" in update_data and update_data["timestamp"] is not None:
            timestamp = update_data.pop("timestamp")
            item.event_date = timestamp.date()
            item.event_time = timestamp.time().replace(microsecond=0)
        if "image_url" in update_data:
            image_url = update_data.pop("image_url")
            if image_url is not None:
                self.items.add_image(item, str(image_url))
        if "traits" in update_data and "description" not in update_data:
            update_data["description"] = update_data.pop("traits")
        for field, value in update_data.items():
            setattr(item, field, value.value if hasattr(value, "value") else value)
        return self.items.save(item)

    def add_image(self, item_id: UUID, image_in: schemas.PostImageCreate, current_user: User) -> PostImage:
        item = self._get_manageable_item(item_id, current_user, "Not enough permissions")
        return self.items.add_image(item, str(image_in.image_url))

    def delete_own_item(self, item_id: UUID, current_user: User) -> None:
        item = self._get_manageable_item(item_id, current_user, "Not enough permissions")
        item.status = ItemStatus.DELETED.value
        self.items.save(item)

    def resolve(self, item_id: UUID, current_user: User) -> Item:
        item = self._get_manageable_item(item_id, current_user, "Only item owner can resolve this item")
        item.status = ItemStatus.RESOLVED.value
        return self.items.save(item)

    def _get_manageable_item(self, item_id: UUID, current_user: User, forbidden_message: str) -> Item:
        item = self.items.get(item_id)
        if not item:
            raise ApiError.not_found("Item")
        if not AuthorizationPolicy.can_manage_item(item, current_user):
            raise ApiError.forbidden(forbidden_message)
        return item
