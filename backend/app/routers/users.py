from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import get_dev_current_user
from app.models import User
from app.services.auth import AuthFlowService
from app.services.user_service import UserService


router = APIRouter(tags=["Users"])


@router.post("/auth/register", response_model=schemas.RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.RegisterResponse:
    return AuthFlowService(db).register(user_in)


@router.post("/auth/login", response_model=schemas.Token, tags=["Auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> schemas.Token:
    return AuthFlowService(db).login(form_data.username, form_data.password)


@router.get("/auth/verify-email", response_model=schemas.VerifyEmailResponse, tags=["Auth"])
def verify_email(token: str, db: Session = Depends(get_db)) -> schemas.VerifyEmailResponse:
    return AuthFlowService(db).verify_email(token)


@router.post("/auth/resend-verification", response_model=schemas.RegisterResponse, tags=["Auth"])
def resend_verification(
    payload: schemas.ResendVerificationRequest,
    db: Session = Depends(get_db),
) -> schemas.RegisterResponse:
    return AuthFlowService(db).resend_verification(payload)


@router.post("/auth/forgot-password", response_model=schemas.PasswordResetResponse, tags=["Auth"])
def forgot_password(
    payload: schemas.PasswordResetRequest,
    db: Session = Depends(get_db),
) -> schemas.PasswordResetResponse:
    return AuthFlowService(db).forgot_password(payload)


@router.post("/auth/reset-password", response_model=schemas.PasswordResetResponse, tags=["Auth"])
def reset_password(
    payload: schemas.PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> schemas.PasswordResetResponse:
    return AuthFlowService(db).reset_password(payload)


@router.get("/users/me", response_model=schemas.UserRead)
def read_me(current_user: User = Depends(get_dev_current_user)) -> User:
    return current_user


@router.patch("/users/me", response_model=schemas.UserRead)
def update_me(
    profile_in: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> User:
    return UserService(db).update_profile(current_user, profile_in)


@router.post("/users/me/profile-photo", response_model=schemas.UserRead)
async def upload_profile_photo(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> User:
    return await UserService(db).upload_profile_photo(current_user, request, file)
