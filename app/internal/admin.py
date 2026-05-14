from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import ApiError, get_dev_admin_user
from app.models import Claim, ClaimStatus, Item, ItemStatus, User
from app.services.item_service import ItemRepository
from app.services.user_service import UserRepository


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_dev_admin_user),
) -> Response:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    items.delete(item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/users", response_model=list[schemas.UserRead])
def admin_list_users(
    include_blocked: bool = True,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_dev_admin_user),
) -> list[User]:
    return UserRepository(db).list(skip=skip, limit=limit, include_blocked=include_blocked)


@router.get("/stats", response_model=schemas.AdminStats)
def admin_read_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_dev_admin_user),
) -> schemas.AdminStats:
    return schemas.AdminStats(
        total_users=db.query(User).count(),
        blocked_users=db.query(User).filter(User.is_blocked.is_(True)).count(),
        total_items=db.query(Item).count(),
        open_items=db.query(Item).filter(Item.status == ItemStatus.OPEN.value).count(),
        resolved_items=db.query(Item).filter(Item.status == ItemStatus.RESOLVED.value).count(),
        total_claims=db.query(Claim).count(),
        pending_claims=db.query(Claim).filter(Claim.status == ClaimStatus.PENDING.value).count(),
        accepted_claims=db.query(Claim).filter(Claim.status == ClaimStatus.ACCEPTED.value).count(),
    )


@router.patch("/users/{user_id}/block", response_model=schemas.UserRead)
def admin_block_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_dev_admin_user),
) -> User:
    users = UserRepository(db)
    user = users.get(user_id)
    if not user:
        raise ApiError.not_found("User")
    return users.set_blocked(user, not user.is_blocked)


@router.patch("/users/{user_id}/moderation", response_model=schemas.UserRead)
def admin_update_user_moderation(
    user_id: int,
    moderation_in: schemas.UserModerationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_dev_admin_user),
) -> User:
    users = UserRepository(db)
    user = users.get(user_id)
    if not user:
        raise ApiError.not_found("User")
    return users.set_blocked(user, moderation_in.is_blocked)
