from app.models import EmailVerification
from app.repositories.base import BaseRepository


class EmailVerificationRepository(BaseRepository):
    def create(self, verification: EmailVerification) -> EmailVerification:
        return self.save(verification)

    def get_pending_by_token_hash(self, token_hash: str) -> EmailVerification | None:
        return (
            self.db.query(EmailVerification)
            .filter(EmailVerification.token_hash == token_hash, EmailVerification.verified_at.is_(None))
            .first()
        )
