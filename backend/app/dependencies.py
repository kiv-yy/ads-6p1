from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.security import oauth2_scheme, AuthService
from app.db.database import get_db
from app.models import AccountStatus, User, UserRole
from app.repositories.users import UserRepository


BLOCKED_USER_MESSAGE = "Mohon maaf anda telah diblokir karena telah melakukan pelanggaran"


class ApiError:
    @staticmethod
    def not_found(resource: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")

    @staticmethod
    def forbidden(detail: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    @staticmethod
    def bad_request(detail: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    @staticmethod
    def conflict(detail: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    @staticmethod
    def unauthorized(detail: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def service_unavailable(detail: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


def get_current_or_dev_user(
    token: str | None = Depends(oauth2_scheme),
    current_user_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> User:
    if token:
        return AuthService(db).get_current_user(token)
    if current_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user = UserRepository(db).get(current_user_id)
    if not user:
        raise ApiError.not_found("User")
    if user.account_status != AccountStatus.ACTIVE.value:
        raise ApiError.forbidden(BLOCKED_USER_MESSAGE)
    return user


def get_optional_current_user(
    token: str | None = Depends(oauth2_scheme),
    current_user_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    try:
        if token:
            return AuthService(db).get_current_user(token)
        if current_user_id is not None:
            user = db.get(User, current_user_id)
            if user and user.account_status == AccountStatus.ACTIVE.value:
                return user
    except Exception:
        pass
    return None


def get_dev_current_user(current_user: User = Depends(get_current_or_dev_user)) -> User:
    return current_user


def get_dev_admin_user(current_user: User = Depends(get_current_or_dev_user)) -> User:
    if current_user.role != UserRole.ADMIN.value:
        raise ApiError.forbidden("Admin access required")
    return current_user
