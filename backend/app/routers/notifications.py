from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import get_dev_current_user
from app.models import Notification, User
from app.services.notifications import NotificationService


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[schemas.NotificationRead])
def list_notifications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[Notification]:
    return NotificationService(db).list_for_user(current_user.id, skip=skip, limit=limit)


@router.get("/summary", response_model=schemas.NotificationSummary)
def notification_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> schemas.NotificationSummary:
    return schemas.NotificationSummary(unread_count=NotificationService(db).unread_count(current_user.id))


@router.patch("/{notification_id}/read", response_model=schemas.NotificationRead)
def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Notification:
    return NotificationService(db).mark_read(notification_id, current_user.id)


@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Response:
    NotificationService(db).mark_all_read(current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
