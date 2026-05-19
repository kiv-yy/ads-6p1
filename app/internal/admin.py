from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import ApiError, get_dev_admin_user
from app.models import (
    AccountStatus,
    AdminActionType,
    Claim,
    ClaimStatus,
    Item,
    ItemStatus,
    Report,
    ReportStatus,
    User,
)
from app.services.admin_actions import AdminActionRepository
from app.services.posts import ItemRepository
from app.services.reports import ReportRepository
from app.services.user_service import UserRepository


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_admin_user),
) -> Response:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    items.soft_delete(item)
    AdminActionRepository(db).log(
        admin_id=current_user.id,
        post_id=item.id,
        action_type=AdminActionType.TAKEDOWN,
        notes="Post dihapus oleh admin",
    )
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
        blocked_users=db.query(User).filter(User.account_status == AccountStatus.BANNED.value).count(),
        total_items=db.query(Item).count(),
        open_items=db.query(Item).filter(Item.status == ItemStatus.OPEN.value).count(),
        resolved_items=db.query(Item).filter(Item.status == ItemStatus.RESOLVED.value).count(),
        total_claims=db.query(Claim).count(),
        pending_claims=db.query(Claim).filter(Claim.status == ClaimStatus.PENDING.value).count(),
        accepted_claims=db.query(Claim).filter(Claim.status == ClaimStatus.ACCEPTED.value).count(),
        total_reports=db.query(Report).count(),
        pending_reports=db.query(Report).filter(Report.status == ReportStatus.PENDING.value).count(),
    )


@router.patch("/users/{user_id}/block", response_model=schemas.UserRead)
def admin_block_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_admin_user),
) -> User:
    users = UserRepository(db)
    user = users.get(user_id)
    if not user:
        raise ApiError.not_found("User")
    updated = users.set_blocked(user, user.account_status != AccountStatus.BANNED.value)
    AdminActionRepository(db).log(
        admin_id=current_user.id,
        user_target_id=user.id,
        action_type=AdminActionType.BAN_USER,
        notes="Toggle blokir user",
    )
    return updated


@router.patch("/users/{user_id}/moderation", response_model=schemas.UserRead)
def admin_update_user_moderation(
    user_id: UUID,
    moderation_in: schemas.UserModerationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_admin_user),
) -> User:
    users = UserRepository(db)
    user = users.get(user_id)
    if not user:
        raise ApiError.not_found("User")
    updated = users.set_blocked(user, moderation_in.is_blocked)
    AdminActionRepository(db).log(
        admin_id=current_user.id,
        user_target_id=user.id,
        action_type=AdminActionType.BAN_USER,
        notes=moderation_in.notes,
    )
    return updated


@router.get("/reports", response_model=list[schemas.ReportRead])
def admin_list_reports(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_dev_admin_user),
) -> list[Report]:
    return ReportRepository(db).list(skip=skip, limit=limit)


@router.patch("/reports/{report_id}", response_model=schemas.ReportRead)
def admin_update_report(
    report_id: UUID,
    report_in: schemas.ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_admin_user),
) -> Report:
    reports = ReportRepository(db)
    report = reports.get(report_id)
    if not report:
        raise ApiError.not_found("Report")
    updated = reports.update_status(report, report_in.status.value)
    AdminActionRepository(db).log(
        admin_id=current_user.id,
        post_id=report.post_id,
        action_type=AdminActionType.WARNING,
        notes=f"Report status diubah menjadi {report_in.status.value}",
    )
    return updated
