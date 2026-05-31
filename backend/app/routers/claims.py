from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import get_dev_current_user
from app.models import Claim, User
from app.services.claims import ClaimService


router = APIRouter(tags=["Claims"])


@router.post("/claims", response_model=schemas.ClaimRead, status_code=status.HTTP_201_CREATED)
def create_claim(
    claim_in: schemas.ClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Claim:
    return ClaimService(db).create(claim_in, claimant=current_user)


@router.get("/claims/{claim_id}", response_model=schemas.ClaimRead)
def read_claim(
    claim_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Claim:
    return ClaimService(db).get_for_participant(claim_id, current_user)


@router.get("/items/{item_id}/claims", response_model=list[schemas.ClaimRead])
def list_item_claims(
    item_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[Claim]:
    return ClaimService(db).list_for_item(item_id, current_user, skip=skip, limit=limit)


@router.get("/claims", response_model=list[schemas.ClaimRead])
def list_my_claims(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[Claim]:
    return ClaimService(db).list_for_user(current_user, skip=skip, limit=limit)


@router.patch("/claims/{claim_id}", response_model=schemas.ClaimRead)
def update_claim_status(
    claim_id: UUID,
    claim_in: schemas.ClaimUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Claim:
    return ClaimService(db).update_status(claim_id, claim_in, current_user)
