from app.models import AdminAction
from app.repositories.base import BaseRepository


class AdminActionRepository(BaseRepository):
    def create(self, action: AdminAction) -> AdminAction:
        return self.save(action)
