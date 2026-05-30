from datetime import timedelta

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
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
BLOCKED_USER_MESSAGE = "Mohon maaf anda telah diblokir karena telah melakukan pelanggaran"
UPLOAD_DIR = Path("app/static/uploads")
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}


@router.post("/auth/register", response_model=schemas.RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.RegisterResponse:
    users = UserRepository(db)
    if users.get_by_email(user_in.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    candidate_nim = user_in.nim or user_in.username
    if candidate_nim and users.get_by_nim(candidate_nim):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="NIM already registered")
    if user_in.username and users.get_by_username(user_in.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
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
        raise ApiError.forbidden(BLOCKED_USER_MESSAGE)
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
        raise ApiError.forbidden(BLOCKED_USER_MESSAGE)
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


@router.patch("/users/me", response_model=schemas.UserRead)
def update_me(
    profile_in: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> User:
    users = UserRepository(db)
    if profile_in.nim and profile_in.nim != current_user.nim:
        existing_nim = users.get_by_nim(profile_in.nim)
        if existing_nim and existing_nim.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="NIM already registered")
    if profile_in.username and profile_in.username != current_user.username:
        existing_username = users.get_by_username(profile_in.username)
        if existing_username and existing_username.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    return users.update_profile(current_user, profile_in)


@router.post("/users/me/profile-photo", response_model=schemas.UserRead)
async def upload_profile_photo(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> User:
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if not extension:
        raise ApiError.bad_request("File harus berupa gambar JPG, PNG, WEBP, atau GIF")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"profile-{current_user.id}-{uuid4()}{extension}"
    target = UPLOAD_DIR / filename
    target.write_bytes(await file.read())

    current_user.profile_photo = str(request.base_url).rstrip("/") + f"/static/uploads/{filename}"
    return UserRepository(db).save(current_user)
