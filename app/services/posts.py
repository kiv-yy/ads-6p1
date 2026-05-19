from datetime import datetime
from uuid import UUID

from sqlalchemy import or_

from app import schemas
from app.models import Category, Item, ItemStatus, ItemType, PostImage
from app.services.base import BaseRepository
from app.services.categories import CategoryRepository


class ItemRepository(BaseRepository):
    def create(self, item_in: schemas.ItemCreate, owner_id: UUID) -> Item:
        category = CategoryRepository(self.db).get_or_create(item_in.category)
        timestamp = item_in.timestamp or datetime.utcnow()
        item = Item(
            owner_id=owner_id,
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
        self.db.add(item)
        self.db.flush()
        if item_in.image_url is not None:
            self.db.add(PostImage(post_id=item.id, image_url=str(item_in.image_url)))
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, item_id: UUID) -> Item | None:
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
        query = self.db.query(Item).join(Category)
        if category:
            query = query.filter(Category.name.ilike(f"%{category}%"))
        if item_type:
            query = query.filter(Item.type == item_type.value)
        if status:
            query = query.filter(Item.status == status.value)
        else:
            query = query.filter(Item.status != ItemStatus.DELETED.value)
        if location:
            query = query.filter(Item.location.ilike(f"%{location}%"))
        if keyword:
            pattern = f"%{keyword}%"
            query = query.filter(or_(Item.title.ilike(pattern), Item.description.ilike(pattern), Item.location.ilike(pattern)))
        return query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, item: Item, item_in: schemas.ItemUpdate) -> Item:
        update_data = item_in.model_dump(exclude_unset=True)
        if "category" in update_data and update_data["category"] is not None:
            item.category_id = CategoryRepository(self.db).get_or_create(update_data.pop("category")).id
        if "timestamp" in update_data and update_data["timestamp"] is not None:
            timestamp = update_data.pop("timestamp")
            item.event_date = timestamp.date()
            item.event_time = timestamp.time().replace(microsecond=0)
        if "image_url" in update_data:
            image_url = update_data.pop("image_url")
            if image_url is not None:
                self.add_image(item, str(image_url))
        if "traits" in update_data and "description" not in update_data:
            update_data["description"] = update_data.pop("traits")
        for field, value in update_data.items():
            setattr(item, field, value.value if hasattr(value, "value") else value)
        return self.save(item)

    def add_image(self, item: Item, image_url: str) -> PostImage:
        image = PostImage(post_id=item.id, image_url=image_url)
        return self.save(image)

    def soft_delete(self, item: Item) -> Item:
        item.status = ItemStatus.DELETED.value
        return self.save(item)
