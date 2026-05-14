from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas
from app.core.config import get_settings
from app.core.security import AuthService, create_access_token
from app.db.database import get_db
from app.dependencies import ApiError, get_dev_current_user
from app.models import User
from app.services.user_service import UserRepository


router = APIRouter(tags=["Users"])
settings = get_settings()


@router.post("/auth/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)) -> User:
    users = UserRepository(db)
    if users.get_by_email(user_in.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return users.create(user_in)


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
    if user.is_blocked:
        raise ApiError.forbidden("User is blocked")

    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(subject=str(user.id), expires_delta=expires_delta)
    return schemas.Token(access_token=access_token)


@router.get("/users/me", response_model=schemas.UserRead)
def read_me(current_user: User = Depends(get_dev_current_user)) -> User:
    return current_user
