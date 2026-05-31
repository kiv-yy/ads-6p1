from sqlalchemy.orm import Session

from app.models import Category
from app.repositories.categories import CategoryRepository


class CategoryService:
    def __init__(self, db: Session) -> None:
        self.categories = CategoryRepository(db)

    def list(self) -> list[Category]:
        return self.categories.list()
