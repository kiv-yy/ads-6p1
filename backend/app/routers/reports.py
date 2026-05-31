from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import get_dev_current_user
from app.models import Report, User
from app.services.reports import ReportService


router = APIRouter(tags=["Reports"])


@router.post("/reports", response_model=schemas.ReportRead, status_code=status.HTTP_201_CREATED)
def create_report(
    report_in: schemas.ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Report:
    return ReportService(db).create(report_in, reporter_id=current_user.id)
