from uuid import UUID

from sqlalchemy import or_

from app.models import Category, Item, ItemStatus, ItemType, PostImage, User, UserRole
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository):
    def create(self, item: Item) -> Item:
        return self.save(item)

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
        current_user: User | None = None,
    ) -> list[Item]:
        query = self.db.query(Item).join(Category)
        if current_user and current_user.role == UserRole.ADMIN.value:
            query = query.filter(Item.status == status.value) if status else query.filter(Item.status != ItemStatus.DELETED.value)
        elif current_user:
            if status:
                query = query.filter(Item.status == status.value)
            else:
                query = query.filter(or_(Item.status == ItemStatus.OPEN.value, Item.owner_id == current_user.id)).filter(
                    Item.status != ItemStatus.DELETED.value
                )
        else:
            query = query.filter(Item.status == status.value) if status else query.filter(Item.status == ItemStatus.OPEN.value)

        if category:
            query = query.filter(Category.name.ilike(f"%{category}%"))
        if item_type:
            query = query.filter(Item.type == item_type.value)
        if location:
            query = query.filter(Item.location.ilike(f"%{location}%"))
        if keyword:
            pattern = f"%{keyword}%"
            query = query.filter(or_(Item.title.ilike(pattern), Item.description.ilike(pattern), Item.location.ilike(pattern)))
        return query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()

    def add_image(self, item: Item, image_url: str) -> PostImage:
        return self.save(PostImage(post_id=item.id, image_url=image_url))
