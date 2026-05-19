from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import ApiError, get_dev_current_user
from app.models import User
from app.services.posts import ItemRepository
from app.services.reports import ReportRepository


router = APIRouter(tags=["Reports"])


@router.post("/reports", response_model=schemas.ReportRead, status_code=status.HTTP_201_CREATED)
def create_report(
    report_in: schemas.ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
):
    if report_in.post_id and not ItemRepository(db).get(report_in.post_id):
        raise ApiError.not_found("Item")
    return ReportRepository(db).create(report_in, reporter_id=current_user.id)
