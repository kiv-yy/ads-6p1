from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import ApiError, get_dev_current_user
from app.models import Claim, ItemStatus, ItemType, User, UserRole
from app.services.authorization import AuthorizationPolicy
from app.services.claims import ClaimRepository
from app.services.posts import ItemRepository


router = APIRouter(tags=["Claims"])


@router.post("/claims", response_model=schemas.ClaimRead, status_code=status.HTTP_201_CREATED)
def create_claim(
    claim_in: schemas.ClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Claim:
    item = ItemRepository(db).get(claim_in.item_id)
    if not item:
        raise ApiError.not_found("Item")
    if item.owner_id == current_user.id:
        raise ApiError.bad_request("You cannot claim your own item")
    if item.type != ItemType.FOUND.value:
        raise ApiError.bad_request("Only found items can be claimed")
    if item.status != ItemStatus.OPEN.value:
        raise ApiError.bad_request("Only active found items can be claimed")
    claims = ClaimRepository(db)
    if claims.get_active_for_item_and_claimant(item.id, current_user.id):
        raise ApiError.bad_request("You already have an active claim for this item")
    return claims.create(claim_in, claimant=current_user)


@router.get("/claims/{claim_id}", response_model=schemas.ClaimRead)
def read_claim(
    claim_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Claim:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_access_claim(claim, current_user):
        raise ApiError.forbidden("Only claim participants can access this resource")
    return claim


@router.get("/items/{item_id}/claims", response_model=list[schemas.ClaimRead])
def list_item_claims(
    item_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[Claim]:
    item = ItemRepository(db).get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Only item owner can view item claims")
    return ClaimRepository(db).list_for_item(item_id=item.id, skip=skip, limit=limit)


@router.get("/claims", response_model=list[schemas.ClaimRead])
def list_my_claims(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[Claim]:
    if current_user.role == UserRole.ADMIN.value:
        return ClaimRepository(db).list_all(skip=skip, limit=limit)
    return ClaimRepository(db).list_for_user(current_user.id)


@router.patch("/claims/{claim_id}", response_model=schemas.ClaimRead)
def update_claim_status(
    claim_id: UUID,
    claim_in: schemas.ClaimUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Claim:
    claims = ClaimRepository(db)
    claim = claims.get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_moderate_claim(claim, current_user):
        raise ApiError.forbidden("Only item owner can moderate claims")
    return claims.update_status(claim, claim_in.status)
