from app.models import Category
from app.services.base import BaseRepository


class CategoryRepository(BaseRepository):
    def get_or_create(self, name: str | None) -> Category:
        category_name = name or "Lainnya"
        category = self.db.query(Category).filter(Category.name == category_name).first()
        if category:
            return category
        category = Category(name=category_name)
        return self.save(category)

    def list(self) -> list[Category]:
        return self.db.query(Category).order_by(Category.name.asc()).all()
