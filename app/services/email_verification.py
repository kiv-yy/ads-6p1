from __future__ import annotations

from datetime import datetime, timedelta
from email.message import EmailMessage
from hashlib import sha256
import json
import logging
from secrets import token_urlsafe
import smtplib
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AccountStatus, EmailVerification, User
from app.services.base import BaseRepository


logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return bool(self.settings.resend_api_key or self._is_smtp_configured())

    def _is_smtp_configured(self) -> bool:
        return bool(self.settings.smtp_host and self.settings.smtp_username and self.settings.smtp_password)

    def send_email(self, recipient: str, subject: str, content: str, dev_label: str, dev_url: str) -> None:
        if self.settings.resend_api_key:
            self._send_via_resend(recipient=recipient, subject=subject, content=content)
            return

        if not self._is_smtp_configured():
            print(f"[DEV {dev_label}] {recipient}: {dev_url}")
            return

        self._send_via_smtp(recipient=recipient, subject=subject, content=content)

    def _send_via_resend(self, recipient: str, subject: str, content: str) -> None:
        payload = json.dumps(
            {
                "from": self.settings.resend_from_email,
                "to": [recipient],
                "subject": subject,
                "text": content,
            }
        ).encode("utf-8")
        request = Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.settings.smtp_timeout_seconds) as response:
                if response.status >= 300:
                    raise EmailDeliveryError("Resend menolak pengiriman email.")
        except HTTPError as error:
            logger.error("Resend rejected email delivery with HTTP status %s.", error.code)
            raise EmailDeliveryError("Resend menolak pengiriman email.") from error
        except (URLError, TimeoutError, OSError) as error:
            logger.error("Resend email delivery request failed: %s.", type(error).__name__)
            raise EmailDeliveryError("Layanan email tidak dapat dihubungi.") from error

    def _send_via_smtp(self, recipient: str, subject: str, content: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.smtp_from_email
        message["To"] = recipient
        message.set_content(content)

        try:
            with smtplib.SMTP(
                self.settings.smtp_host,
                self.settings.smtp_port,
                timeout=self.settings.smtp_timeout_seconds,
            ) as smtp:
                if self.settings.smtp_use_tls:
                    smtp.starttls()
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
                smtp.send_message(message)
        except (smtplib.SMTPException, TimeoutError, OSError) as error:
            logger.error("SMTP email delivery failed: %s.", type(error).__name__)
            raise EmailDeliveryError("Layanan email tidak dapat dihubungi.") from error

    def send_verification_email(self, recipient: str, verification_url: str) -> None:
        self.send_email(
            recipient=recipient,
            subject="Verifikasi Email IPB Lost & Found",
            content=(
                "Halo,\n\n"
                "Klik link berikut untuk memverifikasi akun IPB Lost & Found kamu:\n"
                f"{verification_url}\n\n"
                "Jika kamu tidak merasa mendaftar, abaikan email ini."
            ),
            dev_label="EMAIL VERIFICATION",
            dev_url=verification_url,
        )

    def send_password_reset_email(self, recipient: str, reset_url: str) -> None:
        self.send_email(
            recipient=recipient,
            subject="Reset Password IPB Lost & Found",
            content=(
                "Halo,\n\n"
                "Klik link berikut untuk membuat password baru akun IPB Lost & Found kamu:\n"
                f"{reset_url}\n\n"
                "Link berlaku sementara. Jika kamu tidak meminta reset password, abaikan email ini."
            ),
            dev_label="PASSWORD RESET",
            dev_url=reset_url,
        )


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
