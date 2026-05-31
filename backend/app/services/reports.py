from uuid import UUID

from app import schemas
from app.models import Report
from app.services.base import BaseRepository


class ReportRepository(BaseRepository):
    def create(self, report_in: schemas.ReportCreate, reporter_id: UUID) -> Report:
        report = Report(post_id=report_in.post_id, reporter_id=reporter_id, reason=report_in.reason)
        return self.save(report)

    def get(self, report_id: UUID) -> Report | None:
        return self.db.get(Report, report_id)

    def list(self, skip: int = 0, limit: int = 100) -> list[Report]:
        return self.db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    def update_status(self, report: Report, status: str) -> Report:
        report.status = status
        return self.save(report)
