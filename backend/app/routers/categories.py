from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.services.categories import CategoryRepository


router = APIRouter(tags=["Categories"])


@router.get("/categories", response_model=list[schemas.CategoryRead])
def list_categories(db: Session = Depends(get_db)) -> list:
    return CategoryRepository(db).list()
