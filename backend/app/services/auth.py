from datetime import timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app import schemas
from app.core.config import get_settings
from app.core.security import AuthService as CoreAuthService
from app.core.security import create_access_token
from app.dependencies import ApiError
from app.models import AccountStatus, User
from app.repositories.users import UserRepository
from app.services.email_verification import EmailDeliveryError, EmailVerificationService
from app.services.password_reset import PasswordResetService
from app.services.user_service import UserService


BLOCKED_USER_MESSAGE = "Mohon maaf anda telah diblokir karena telah melakukan pelanggaran"


class AuthFlowService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.users = UserService(db)
        self.email_verifications = EmailVerificationService(db)
        self.password_resets = PasswordResetService(db)

    def register(self, user_in: schemas.UserCreate) -> schemas.RegisterResponse:
        user = self.users.create(user_in)
        try:
            verification_url = self.email_verifications.create_and_send(user)
        except EmailDeliveryError:
            verification_url = None
        return schemas.RegisterResponse(
            user=user,
            message="Pendaftaran berhasil. Silakan verifikasi email @apps.ipb.ac.id sebelum login.",
            verification_url=verification_url,
        )

    def login(self, identifier: str, password: str) -> schemas.Token:
        user = CoreAuthService(self.db).authenticate(identifier, password)
        if not user:
            raise ApiError.unauthorized("Incorrect email or password")
        if user.account_status == AccountStatus.BANNED.value:
            raise ApiError.forbidden(BLOCKED_USER_MESSAGE)
        if user.account_status != AccountStatus.ACTIVE.value:
            raise ApiError.forbidden("Email belum diverifikasi. Silakan cek email IPB kamu.")
        expires_delta = timedelta(minutes=self.settings.access_token_expire_minutes)
        return schemas.Token(access_token=create_access_token(subject=str(user.id), expires_delta=expires_delta))

    def verify_email(self, token: str) -> schemas.VerifyEmailResponse:
        user = self.email_verifications.verify(token)
        if not user:
            raise ApiError.bad_request("Token verifikasi tidak valid atau sudah kedaluwarsa")
        return schemas.VerifyEmailResponse(message="Email berhasil diverifikasi. Kamu sudah bisa login.", user=user)

    def resend_verification(self, payload: schemas.ResendVerificationRequest) -> schemas.RegisterResponse:
        user = self.users.get_by_email(str(payload.email))
        if not user:
            raise ApiError.not_found("User")
        if user.account_status == AccountStatus.ACTIVE.value:
            return schemas.RegisterResponse(user=user, message="Email sudah diverifikasi.", verification_url=None)
        if user.account_status == AccountStatus.BANNED.value:
            raise ApiError.forbidden(BLOCKED_USER_MESSAGE)
        try:
            verification_url = self.email_verifications.create_and_send(user)
        except EmailDeliveryError as error:
            raise ApiError.service_unavailable("Email verifikasi belum berhasil dikirim. Silakan coba lagi beberapa saat lagi.") from error
        return schemas.RegisterResponse(user=user, message="Link verifikasi baru sudah dikirim.", verification_url=verification_url)

    def forgot_password(self, payload: schemas.PasswordResetRequest) -> schemas.PasswordResetResponse:
        user = self.users.get_by_email(str(payload.email))
        try:
            reset_url = self.password_resets.create_and_send(user) if user else None
        except EmailDeliveryError:
            reset_url = None
        return schemas.PasswordResetResponse(message="Email link reset password telah dikirim ke email anda.", reset_url=reset_url)

    def reset_password(self, payload: schemas.PasswordResetConfirm) -> schemas.PasswordResetResponse:
        user = self.password_resets.reset_password(payload.token, payload.new_password)
        if not user:
            raise ApiError.bad_request("Link reset password tidak valid atau sudah kedaluwarsa.")
        return schemas.PasswordResetResponse(message="Password berhasil diubah. Silakan login dengan password baru.")

    def resolve_websocket_user(self, token: str | None, current_user_id: UUID | None) -> User | None:
        try:
            if token:
                return CoreAuthService(self.db).get_current_user(token)
        except Exception:
            return None
        if current_user_id is not None:
            return UserRepository(self.db).get(current_user_id)
        return None
