from uuid import UUID
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Query, Request, Response, UploadFile, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import ApiError, get_dev_current_user, get_optional_current_user
from app.models import Item, ItemStatus, ItemType, User
from app.services.authorization import AuthorizationPolicy
from app.services.posts import ItemRepository


router = APIRouter(tags=["Items"])
UPLOAD_DIR = Path("app/static/uploads")
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}


@router.post("/items", response_model=schemas.ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Item:
    return ItemRepository(db).create(item_in, owner_id=current_user.id)


@router.post("/items/upload-image", response_model=schemas.PostImageCreate)
async def upload_item_image(
    request: Request,
    file: UploadFile = File(...),
    _: User = Depends(get_dev_current_user),
) -> schemas.PostImageCreate:
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if extension is None:
        raise ApiError.bad_request("File harus berupa gambar JPG, PNG, WEBP, atau GIF")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4()}{extension}"
    target = UPLOAD_DIR / filename
    content = await file.read()
    target.write_bytes(content)

    image_url = str(request.base_url).rstrip("/") + f"/static/uploads/{filename}"
    return schemas.PostImageCreate(image_url=image_url)


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
    return ItemRepository(db).list(
        category=category,
        item_type=ItemType(schemas.normalize_item_type(item_type)) if item_type else None,
        status=ItemStatus(schemas.normalize_item_status(item_status)) if item_status else None,
        location=location,
        keyword=keyword or q,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )


@router.get("/items/{item_id}", response_model=schemas.ItemRead)
def read_item(item_id: UUID, db: Session = Depends(get_db)) -> Item:
    item = ItemRepository(db).get(item_id)
    if not item or item.status == ItemStatus.DELETED.value:
        raise ApiError.not_found("Item")
    return item


@router.patch("/items/{item_id}", response_model=schemas.ItemRead)
def update_item(
    item_id: UUID,
    item_in: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Item:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Not enough permissions")
    return items.update(item, item_in)


@router.post("/items/{item_id}/images", response_model=schemas.PostImageRead, status_code=status.HTTP_201_CREATED)
def add_item_image(
    item_id: UUID,
    image_in: schemas.PostImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
):
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Not enough permissions")
    return items.add_image(item, str(image_in.image_url))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Response:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Not enough permissions")
    items.soft_delete(item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/items/{item_id}/resolve", response_model=schemas.ItemRead)
def resolve_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Item:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Only item owner can resolve this item")
    return items.update(item, schemas.ItemUpdate(status=ItemStatus.RESOLVED))
