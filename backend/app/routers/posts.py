from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Request, Response, UploadFile, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import get_dev_current_user, get_optional_current_user
from app.models import Item, User
from app.services.posts import ItemService


router = APIRouter(tags=["Items"])


@router.post("/items", response_model=schemas.ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Item:
    return ItemService(db).create(item_in, owner=current_user)


@router.post("/items/upload-image", response_model=schemas.PostImageCreate)
async def upload_item_image(
    request: Request,
    file: UploadFile = File(...),
    _: User = Depends(get_dev_current_user),
    db: Session = Depends(get_db),
) -> schemas.PostImageCreate:
    return await ItemService(db).upload_image(request, file)


@router.get("/items", response_model=list[schemas.ItemRead])
def list_items(
    category: str | None = None,
    item_type: str | None = Query(default=None, alias="type"),
    item_status: str | None = Query(default=None, alias="status"),
    location: str | None = None,
    keyword: str | None = None,
    q: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> list[Item]:
    return ItemService(db).list(
        category=category,
        item_type=item_type,
        item_status=item_status,
        location=location,
        keyword=keyword or q,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )


@router.get("/items/{item_id}", response_model=schemas.ItemRead)
def read_item(item_id: UUID, db: Session = Depends(get_db)) -> Item:
    return ItemService(db).get_public(item_id)


@router.patch("/items/{item_id}", response_model=schemas.ItemRead)
def update_item(
    item_id: UUID,
    item_in: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Item:
    return ItemService(db).update(item_id, item_in, current_user)


@router.post("/items/{item_id}/images", response_model=schemas.PostImageRead, status_code=status.HTTP_201_CREATED)
def add_item_image(
    item_id: UUID,
    image_in: schemas.PostImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
):
    return ItemService(db).add_image(item_id, image_in, current_user)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Response:
    ItemService(db).delete_own_item(item_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/items/{item_id}/resolve", response_model=schemas.ItemRead)
def resolve_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Item:
    return ItemService(db).resolve(item_id, current_user)
