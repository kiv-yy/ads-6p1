from uuid import UUID

from app.models import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    def create(self, report: Report) -> Report:
        return self.save(report)

    def get(self, report_id: UUID) -> Report | None:
        return self.db.get(Report, report_id)

    def list(self, skip: int = 0, limit: int = 100) -> list[Report]:
        return self.db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
