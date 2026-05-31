from app.models import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    def get_or_create(self, name: str | None) -> Category:
        category_name = name or "Lainnya"
        category = self.db.query(Category).filter(Category.name == category_name).first()
        if category:
            return category
        return self.save(Category(name=category_name))

    def list(self) -> list[Category]:
        return self.db.query(Category).order_by(Category.name.asc()).all()
