from uuid import UUID

from sqlalchemy.orm import Session

from app import schemas
from app.dependencies import ApiError
from app.models import Report
from app.repositories.items import ItemRepository
from app.repositories.reports import ReportRepository


class ReportService:
    def __init__(self, db: Session) -> None:
        self.items = ItemRepository(db)
        self.reports = ReportRepository(db)

    def create(self, report_in: schemas.ReportCreate, reporter_id: UUID) -> Report:
        if report_in.post_id and not self.items.get(report_in.post_id):
            raise ApiError.not_found("Item")
        return self.reports.create(Report(post_id=report_in.post_id, reporter_id=reporter_id, reason=report_in.reason))

    def list(self, skip: int = 0, limit: int = 100) -> list[Report]:
        return self.reports.list(skip=skip, limit=limit)

    def update_status(self, report_id: UUID, status: str) -> Report:
        report = self.reports.get(report_id)
        if not report:
            raise ApiError.not_found("Report")
        report.status = status
        return self.reports.save(report)
