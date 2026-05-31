from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import PasswordService
from app.models import PasswordResetToken, User
from app.repositories.password_resets import PasswordResetRepository
from app.services.email_verification import EmailService


class PasswordResetService:
    def __init__(
        self,
        db: Session,
        email_service: EmailService | None = None,
        password_service: PasswordService | None = None,
    ) -> None:
        self.settings = get_settings()
        self.email_service = email_service or EmailService()
        self.password_service = password_service or PasswordService()
        self.resets = PasswordResetRepository(db)

    @staticmethod
    def hash_token(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def is_expired(cls, expires_at: datetime) -> bool:
        now = cls.utc_now() if expires_at.tzinfo else datetime.now()
        return expires_at < now

    def build_reset_url(self, token: str) -> str:
        return f"{self.settings.frontend_url.rstrip('/')}/reset-password?token={token}"

    def create_and_send(self, user: User) -> str | None:
        token = token_urlsafe(32)
        reset = PasswordResetToken(
            user_id=user.id,
            token_hash=self.hash_token(token),
            expires_at=self.utc_now() + timedelta(minutes=self.settings.password_reset_expire_minutes),
        )
        self.resets.create(reset)
        reset_url = self.build_reset_url(token)
        self.email_service.send_password_reset_email(
            user.email,
            reset_url,
            user.full_name,
            self.settings.password_reset_expire_minutes,
        )
        return None if self.email_service.is_configured() else reset_url

    def reset_password(self, token: str, new_password: str) -> User | None:
        reset = self.resets.get_pending_by_token_hash(self.hash_token(token))
        if not reset or self.is_expired(reset.expires_at):
            return None
        reset.user.hashed_password = self.password_service.hash(new_password)
        reset.used_at = self.utc_now()
        self.resets.save(reset)
        return reset.user
