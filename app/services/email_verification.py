from __future__ import annotations

from datetime import datetime, timedelta
from email.message import EmailMessage
from hashlib import sha256
from secrets import token_urlsafe
import smtplib

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AccountStatus, EmailVerification, User
from app.services.base import BaseRepository


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return bool(self.settings.smtp_host and self.settings.smtp_username and self.settings.smtp_password)

    def send_verification_email(self, recipient: str, verification_url: str) -> None:
        if not self.is_configured():
            print(f"[DEV EMAIL VERIFICATION] {recipient}: {verification_url}")
            return

        message = EmailMessage()
        message["Subject"] = "Verifikasi Email IPB Lost & Found"
        message["From"] = self.settings.smtp_from_email
        message["To"] = recipient
        message.set_content(
            "Halo,\n\n"
            "Klik link berikut untuk memverifikasi akun IPB Lost & Found kamu:\n"
            f"{verification_url}\n\n"
            "Jika kamu tidak merasa mendaftar, abaikan email ini."
        )

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as smtp:
            if self.settings.smtp_use_tls:
                smtp.starttls()
            smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)


class EmailVerificationRepository(BaseRepository):
    def __init__(self, db: Session, email_service: EmailService | None = None) -> None:
        super().__init__(db)
        self.settings = get_settings()
        self.email_service = email_service or EmailService()

    @staticmethod
    def hash_token(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    def create_token(self, user: User) -> tuple[EmailVerification, str]:
        token = token_urlsafe(32)
        verification = EmailVerification(
            user_id=user.id,
            token_hash=self.hash_token(token),
            expires_at=datetime.utcnow() + timedelta(minutes=self.settings.email_verification_expire_minutes),
        )
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        return verification, token

    def build_verification_url(self, token: str) -> str:
        return f"{self.settings.frontend_url.rstrip('/')}/verify-email?token={token}"

    def create_and_send(self, user: User) -> str | None:
        _, token = self.create_token(user)
        verification_url = self.build_verification_url(token)
        self.email_service.send_verification_email(user.email, verification_url)
        return None if self.email_service.is_configured() else verification_url

    def verify(self, token: str) -> User | None:
        verification = (
            self.db.query(EmailVerification)
            .filter(EmailVerification.token_hash == self.hash_token(token), EmailVerification.verified_at.is_(None))
            .first()
        )
        if not verification or verification.expires_at < datetime.utcnow():
            return None

        verification.verified_at = datetime.utcnow()
        verification.user.account_status = AccountStatus.ACTIVE.value
        self.db.commit()
        self.db.refresh(verification.user)
        return verification.user
