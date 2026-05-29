from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas
from app.core.config import get_settings
from app.core.security import AuthService, create_access_token
from app.db.database import get_db
from app.dependencies import ApiError, get_dev_current_user
from app.models import AccountStatus, User
from app.services.email_verification import EmailDeliveryError, EmailVerificationRepository
from app.services.password_reset import PasswordResetRepository
from app.services.user_service import UserRepository


router = APIRouter(tags=["Users"])
settings = get_settings()


@router.post("/auth/register", response_model=schemas.RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.RegisterResponse:
    users = UserRepository(db)
    if users.get_by_email(user_in.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if users.get_by_nim(user_in.nim):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="NIM already registered")
    user = users.create(user_in)
    try:
        verification_url = EmailVerificationRepository(db).create_and_send(user)
    except EmailDeliveryError:
        verification_url = None
    message = "Pendaftaran berhasil. Silakan verifikasi email @apps.ipb.ac.id sebelum login."
    return schemas.RegisterResponse(
        user=user,
        message=message,
        verification_url=verification_url,
    )


@router.post("/auth/login", response_model=schemas.Token, tags=["Auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> schemas.Token:
    user = AuthService(db).authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.account_status == AccountStatus.BANNED.value:
        raise ApiError.forbidden("User is blocked")
    if user.account_status != AccountStatus.ACTIVE.value:
        raise ApiError.forbidden("Email belum diverifikasi. Silakan cek email IPB kamu.")

    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(subject=str(user.id), expires_delta=expires_delta)
    return schemas.Token(access_token=access_token)


@router.get("/auth/verify-email", response_model=schemas.VerifyEmailResponse, tags=["Auth"])
def verify_email(token: str, db: Session = Depends(get_db)) -> schemas.VerifyEmailResponse:
    user = EmailVerificationRepository(db).verify(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token verifikasi tidak valid atau sudah kedaluwarsa")
    return schemas.VerifyEmailResponse(message="Email berhasil diverifikasi. Kamu sudah bisa login.", user=user)


@router.post("/auth/resend-verification", response_model=schemas.RegisterResponse, tags=["Auth"])
def resend_verification(
    payload: schemas.ResendVerificationRequest,
    db: Session = Depends(get_db),
) -> schemas.RegisterResponse:
    user = UserRepository(db).get_by_email(str(payload.email))
    if not user:
        raise ApiError.not_found("User")
    if user.account_status == AccountStatus.ACTIVE.value:
        return schemas.RegisterResponse(user=user, message="Email sudah diverifikasi.", verification_url=None)
    if user.account_status == AccountStatus.BANNED.value:
        raise ApiError.forbidden("User is blocked")
    try:
        verification_url = EmailVerificationRepository(db).create_and_send(user)
    except EmailDeliveryError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email verifikasi belum berhasil dikirim. Silakan coba lagi beberapa saat lagi.",
        ) from error
    return schemas.RegisterResponse(
        user=user,
        message="Link verifikasi baru sudah dikirim.",
        verification_url=verification_url,
    )


@router.post("/auth/forgot-password", response_model=schemas.PasswordResetResponse, tags=["Auth"])
def forgot_password(
    payload: schemas.PasswordResetRequest,
    db: Session = Depends(get_db),
) -> schemas.PasswordResetResponse:
    user = UserRepository(db).get_by_email(str(payload.email))
    try:
        reset_url = PasswordResetRepository(db).create_and_send(user) if user else None
    except EmailDeliveryError:
        reset_url = None
    return schemas.PasswordResetResponse(
        message="Jika email terdaftar, link reset password telah dikirim ke email IPB kamu.",
        reset_url=reset_url,
    )


@router.post("/auth/reset-password", response_model=schemas.PasswordResetResponse, tags=["Auth"])
def reset_password(
    payload: schemas.PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> schemas.PasswordResetResponse:
    user = PasswordResetRepository(db).reset_password(payload.token, payload.new_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link reset password tidak valid atau sudah kedaluwarsa.")
    return schemas.PasswordResetResponse(message="Password berhasil diubah. Silakan login dengan password baru.")
@router.get("/users/me", response_model=schemas.UserRead)
def read_me(current_user: User = Depends(get_dev_current_user)) -> User:
    return current_user
