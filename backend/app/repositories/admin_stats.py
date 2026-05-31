from sqlalchemy.orm import Session

from app import schemas
from app.models import AccountStatus, Claim, ClaimStatus, Item, ItemStatus, Report, ReportStatus, User


class AdminStatsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def read(self) -> schemas.AdminStats:
        return schemas.AdminStats(
            total_users=self.db.query(User).count(),
            blocked_users=self.db.query(User).filter(User.account_status == AccountStatus.BANNED.value).count(),
            total_items=self.db.query(Item).count(),
            open_items=self.db.query(Item).filter(Item.status == ItemStatus.OPEN.value).count(),
            resolved_items=self.db.query(Item).filter(Item.status == ItemStatus.RESOLVED.value).count(),
            total_claims=self.db.query(Claim).count(),
            pending_claims=self.db.query(Claim).filter(Claim.status == ClaimStatus.PENDING.value).count(),
            accepted_claims=self.db.query(Claim).filter(Claim.status == ClaimStatus.ACCEPTED.value).count(),
            total_reports=self.db.query(Report).count(),
            pending_reports=self.db.query(Report).filter(Report.status == ReportStatus.PENDING.value).count(),
        )
