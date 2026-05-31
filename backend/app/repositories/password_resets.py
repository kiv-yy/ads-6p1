from app.models import PasswordResetToken
from app.repositories.base import BaseRepository


class PasswordResetRepository(BaseRepository):
    def create(self, reset: PasswordResetToken) -> PasswordResetToken:
        return self.save(reset)

    def get_pending_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        return (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash, PasswordResetToken.used_at.is_(None))
            .first()
        )
