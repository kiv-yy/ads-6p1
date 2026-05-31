from uuid import UUID

from sqlalchemy.orm import Session

from app import schemas
from app.dependencies import ApiError
from app.models import AdminActionType, ItemStatus, Report, User
from app.repositories.admin_stats import AdminStatsRepository
from app.repositories.items import ItemRepository
from app.services.admin_actions import AdminActionService
from app.services.reports import ReportService
from app.services.user_service import UserService


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.items = ItemRepository(db)
        self.users = UserService(db)
        self.reports = ReportService(db)
        self.actions = AdminActionService(db)
        self.stats_repository = AdminStatsRepository(db)

    def delete_item(self, item_id: UUID, admin: User) -> None:
        item = self.items.get(item_id)
        if not item:
            raise ApiError.not_found("Item")
        item.status = ItemStatus.DELETED.value
        self.items.save(item)
        self.actions.log(
            admin_id=admin.id,
            post_id=item.id,
            action_type=AdminActionType.TAKEDOWN,
            notes="Post dihapus oleh admin",
        )

    def list_users(self, skip: int, limit: int, include_blocked: bool) -> list[User]:
        return self.users.list(skip=skip, limit=limit, include_blocked=include_blocked)

    def stats(self) -> schemas.AdminStats:
        return self.stats_repository.read()

    def set_user_blocked(self, user_id: UUID, is_blocked: bool, admin: User, notes: str | None = None) -> User:
        updated = self.users.set_blocked(user_id, is_blocked)
        self.actions.log(
            admin_id=admin.id,
            user_target_id=updated.id,
            action_type=AdminActionType.BAN_USER,
            notes=notes or "Toggle blokir user",
        )
        return updated

    def list_reports(self, skip: int, limit: int) -> list[Report]:
        return self.reports.list(skip=skip, limit=limit)

    def update_report(self, report_id: UUID, report_in: schemas.ReportUpdate, admin: User) -> Report:
        updated = self.reports.update_status(report_id, report_in.status.value)
        self.actions.log(
            admin_id=admin.id,
            post_id=updated.post_id,
            action_type=AdminActionType.WARNING,
            notes=f"Report status diubah menjadi {report_in.status.value}",
        )
        return updated
