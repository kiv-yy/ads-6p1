from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import get_dev_admin_user
from app.models import AccountStatus, Report, User
from app.services.admin import AdminService


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_admin_user),
) -> Response:
    AdminService(db).delete_item(item_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/users", response_model=list[schemas.UserRead])
def admin_list_users(
    include_blocked: bool = True,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_dev_admin_user),
) -> list[User]:
    return AdminService(db).list_users(skip=skip, limit=limit, include_blocked=include_blocked)


@router.get("/stats", response_model=schemas.AdminStats)
def admin_read_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_dev_admin_user),
) -> schemas.AdminStats:
    return AdminService(db).stats()


@router.patch("/users/{user_id}/block", response_model=schemas.UserRead)
def admin_block_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_admin_user),
) -> User:
    target = AdminService(db).users.get(user_id)
    is_blocked = target.account_status != AccountStatus.BANNED.value if target else True
    return AdminService(db).set_user_blocked(user_id, is_blocked, current_user)


@router.patch("/users/{user_id}/moderation", response_model=schemas.UserRead)
def admin_update_user_moderation(
    user_id: UUID,
    moderation_in: schemas.UserModerationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_admin_user),
) -> User:
    return AdminService(db).set_user_blocked(user_id, moderation_in.is_blocked, current_user, notes=moderation_in.notes)


@router.get("/reports", response_model=list[schemas.ReportRead])
def admin_list_reports(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_dev_admin_user),
) -> list[Report]:
    return AdminService(db).list_reports(skip=skip, limit=limit)


@router.patch("/reports/{report_id}", response_model=schemas.ReportRead)
def admin_update_report(
    report_id: UUID,
    report_in: schemas.ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_admin_user),
) -> Report:
    return AdminService(db).update_report(report_id, report_in, current_user)
