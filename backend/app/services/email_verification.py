from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from html import escape
from hashlib import sha256
import logging
from secrets import token_urlsafe
import smtplib

import requests
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AccountStatus, EmailVerification, User
from app.repositories.email_verifications import EmailVerificationRepository

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

    def send_email(
        self,
        recipient: str,
        subject: str,
        content: str,
        dev_label: str,
        dev_url: str,
        html_content: str | None = None,
    ) -> None:
        if self.settings.resend_api_key:
            self._send_via_resend(
                recipient=recipient,
                subject=subject,
                content=content,
                html_content=html_content,
            )
            return

        if not self._is_smtp_configured():
            print(f"[DEV {dev_label}] {recipient}: {dev_url}")
            return

        self._send_via_smtp(recipient=recipient, subject=subject, content=content, html_content=html_content)

    def _send_via_resend(self, recipient: str, subject: str, content: str, html_content: str | None = None) -> None:
        payload = {
            "from": self.settings.resend_from_email,
            "to": [recipient],
            "subject": subject,
            "text": content,
        }
        if html_content:
            payload["html"] = html_content
        try:
            response = requests.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.settings.resend_api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "ipb-lost-found/1.0",
                },
                timeout=self.settings.smtp_timeout_seconds,
            )
            response.raise_for_status()
        except requests.HTTPError as error:
            response = error.response
            status_code = response.status_code if response is not None else "unknown"
            detail = response.text if response is not None else str(error)
            logger.error("Resend rejected email delivery with HTTP status %s: %s", status_code, detail)
            raise EmailDeliveryError("Resend menolak pengiriman email.") from error
        except requests.RequestException as error:
            logger.error("Resend email delivery request failed: %s.", type(error).__name__)
            raise EmailDeliveryError("Layanan email tidak dapat dihubungi.") from error

    def _send_via_smtp(self, recipient: str, subject: str, content: str, html_content: str | None = None) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.smtp_from_email
        message["To"] = recipient
        message.set_content(content)
        if html_content:
            message.add_alternative(html_content, subtype="html")

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

    def send_verification_email(self, recipient: str, verification_url: str, full_name: str) -> None:
        safe_name = full_name.strip() or "Pengguna"
        escaped_name = escape(safe_name)
        escaped_url = escape(verification_url)
        text_content = (
            f"Yth. {safe_name}\n\n"
            "Terima kasih telah mendaftarkan akun pada platform Lost & Found IPB. "
            "Untuk menyelesaikan proses pendaftaran dan memastikan validitas alamat email Anda, "
            "silakan melakukan aktivasi akun melalui tautan di bawah ini:\n\n"
            "Klik di Sini untuk Aktivasi Akun\n"
            f"{verification_url}\n\n"
            "Tautan di atas hanya dapat digunakan satu kali dan akan kedaluwarsa dalam waktu 60 menit. "
            "Jika tautan tersebut tidak dapat diklik, Anda dapat menyalin dan menempelkan URL berikut "
            "pada peramban (browser) Anda:\n"
            f"{verification_url}\n\n"
            "Apabila Anda tidak merasa melakukan pendaftaran ini, mohon abaikan email ini.\n\n"
            "Terima kasih atas perhatian dan kerja sama Anda.\n\n"
            "Salam hormat,\n"
            "Tim Pengembang Lost & Found IPB"
        )
        html_content = (
            f"<p>Yth. {escaped_name}</p>"
            "<p>Terima kasih telah mendaftarkan akun pada platform Lost &amp; Found IPB. "
            "Untuk menyelesaikan proses pendaftaran dan memastikan validitas alamat email Anda, "
            "silakan melakukan aktivasi akun melalui tautan di bawah ini:</p>"
            f"<p><a href=\"{escaped_url}\">Klik di Sini untuk Aktivasi Akun</a></p>"
            "<p>Tautan di atas hanya dapat digunakan satu kali dan akan kedaluwarsa dalam waktu 60 menit. "
            "Jika tautan tersebut tidak dapat diklik, Anda dapat menyalin dan menempelkan URL berikut "
            "pada peramban (browser) Anda:</p>"
            f"<p>{escaped_url}</p>"
            "<p>Apabila Anda tidak merasa melakukan pendaftaran ini, mohon abaikan email ini.</p>"
            "<p>Terima kasih atas perhatian dan kerja sama Anda.</p>"
            "<p>Salam hormat,<br>Tim Pengembang Lost &amp; Found IPB</p>"
        )
        self.send_email(
            recipient=recipient,
            subject="Verifikasi Email IPB Lost & Found",
            content=text_content,
            dev_label="EMAIL VERIFICATION",
            dev_url=verification_url,
            html_content=html_content,
        )

    def send_password_reset_email(self, recipient: str, reset_url: str, full_name: str, expire_minutes: int) -> None:
        safe_name = full_name.strip() or "Pengguna"
        escaped_name = escape(safe_name)
        escaped_url = escape(reset_url)
        duration_label = f"{expire_minutes} menit"
        text_content = (
            f"Yth. {safe_name},\n\n"
            "Kami menerima permintaan untuk mengatur ulang kata sandi akun Anda pada platform Lost & Found IPB. "
            "Untuk melanjutkan proses ini dan membuat kata sandi baru, silakan klik tautan di bawah ini:\n\n"
            "Klik di Sini untuk Atur Ulang Kata Sandi\n\n"
            "Tautan di atas hanya dapat digunakan satu kali dan akan kedaluwarsa dalam waktu "
            f"{duration_label} demi menjaga keamanan akun Anda. Jika tautan tersebut tidak dapat diklik, "
            "Anda dapat menyalin dan menempelkan URL berikut pada peramban (browser) Anda:\n"
            f"{reset_url}\n\n"
            "Apabila Anda tidak merasa melakukan permintaan ini, mohon abaikan email ini dan kata sandi Anda akan tetap aman.\n\n"
            "Terima kasih atas perhatian dan kerja sama Anda.\n\n"
            "Salam hormat,\n\n"
            "Tim Pengembang Lost & Found IPB"
        )
        html_content = (
            f"<p>Yth. {escaped_name},</p>"
            "<p>Kami menerima permintaan untuk mengatur ulang kata sandi akun Anda pada platform Lost &amp; Found IPB. "
            "Untuk melanjutkan proses ini dan membuat kata sandi baru, silakan klik tautan di bawah ini:</p>"
            f"<p><a href=\"{escaped_url}\">Klik di Sini untuk Atur Ulang Kata Sandi</a></p>"
            "<p>Tautan di atas hanya dapat digunakan satu kali dan akan kedaluwarsa dalam waktu "
            f"{escape(duration_label)} demi menjaga keamanan akun Anda. Jika tautan tersebut tidak dapat diklik, "
            "Anda dapat menyalin dan menempelkan URL berikut pada peramban (browser) Anda:</p>"
            f"<p>{escaped_url}</p>"
            "<p>Apabila Anda tidak merasa melakukan permintaan ini, mohon abaikan email ini dan kata sandi Anda akan tetap aman.</p>"
            "<p>Terima kasih atas perhatian dan kerja sama Anda.</p>"
            "<p>Salam hormat,</p>"
            "<p>Tim Pengembang Lost &amp; Found IPB</p>"
        )
        self.send_email(
            recipient=recipient,
            subject="Reset Password IPB Lost & Found",
            content=text_content,
            dev_label="PASSWORD RESET",
            dev_url=reset_url,
            html_content=html_content,
        )


class EmailVerificationService:
    def __init__(self, db: Session, email_service: EmailService | None = None) -> None:
        self.settings = get_settings()
        self.email_service = email_service or EmailService()
        self.verifications = EmailVerificationRepository(db)

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

    def create_token(self, user: User) -> tuple[EmailVerification, str]:
        token = token_urlsafe(32)
        verification = EmailVerification(
            user_id=user.id,
            token_hash=self.hash_token(token),
            expires_at=self.utc_now() + timedelta(minutes=self.settings.email_verification_expire_minutes),
        )
        return self.verifications.create(verification), token

    def build_verification_url(self, token: str) -> str:
        return f"{self.settings.frontend_url.rstrip('/')}/verify-email?token={token}"

    def create_and_send(self, user: User) -> str | None:
        _, token = self.create_token(user)
        verification_url = self.build_verification_url(token)
        self.email_service.send_verification_email(user.email, verification_url, user.full_name)
        return None if self.email_service.is_configured() else verification_url

    def verify(self, token: str) -> User | None:
        verification = self.verifications.get_pending_by_token_hash(self.hash_token(token))
        if not verification or self.is_expired(verification.expires_at):
            return None

        verification.verified_at = self.utc_now()
        verification.user.account_status = AccountStatus.ACTIVE.value
        self.verifications.save(verification)
        return verification.user
