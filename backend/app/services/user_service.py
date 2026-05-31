from pathlib import Path
from uuid import UUID, uuid4

from fastapi import Request, UploadFile
from sqlalchemy.orm import Session

from app import schemas
from app.core.security import PasswordService
from app.dependencies import ApiError
from app.models import AccountStatus, User
from app.repositories.users import UserRepository


class UserService:
    upload_dir = Path("app/static/uploads")
    allowed_image_types = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}

    def __init__(self, db: Session, password_service: PasswordService | None = None) -> None:
        self.users = UserRepository(db)
        self.password_service = password_service or PasswordService()

    def create(self, user_in: schemas.UserCreate) -> User:
        if self.users.get_by_email(user_in.email):
            raise ApiError.conflict("Email already registered")
        candidate_nim = user_in.nim or user_in.username
        if candidate_nim and self.users.get_by_nim(candidate_nim):
            raise ApiError.conflict("NIM already registered")
        if user_in.username and self.users.get_by_username(user_in.username):
            raise ApiError.conflict("Username already registered")
        return self.users.create(
            User(
                email=user_in.email,
                full_name=user_in.full_name,
                username=user_in.username,
                major=user_in.major,
                faculty=user_in.faculty,
                nim=user_in.nim,
                hashed_password=self.password_service.hash(user_in.password),
                account_status=AccountStatus.INACTIVE.value,
            )
        )

    def get(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.users.get_by_email(email)

    def list(self, skip: int = 0, limit: int = 20, include_blocked: bool = True) -> list[User]:
        return self.users.list(skip=skip, limit=limit, include_blocked=include_blocked)

    def update_profile(self, current_user: User, profile_in: schemas.UserProfileUpdate) -> User:
        if profile_in.nim and profile_in.nim != current_user.nim:
            existing_nim = self.users.get_by_nim(profile_in.nim)
            if existing_nim and existing_nim.id != current_user.id:
                raise ApiError.conflict("NIM already registered")
        if profile_in.username and profile_in.username != current_user.username:
            existing_username = self.users.get_by_username(profile_in.username)
            if existing_username and existing_username.id != current_user.id:
                raise ApiError.conflict("Username already registered")
        payload = profile_in.model_dump(exclude_unset=True)
        for field, value in payload.items():
            if field in {"full_name", "username", "nim"} and value is None:
                continue
            setattr(current_user, field, value)
        return self.users.save(current_user)

    async def upload_profile_photo(self, current_user: User, request: Request, file: UploadFile) -> User:
        extension = self.allowed_image_types.get(file.content_type or "")
        if not extension:
            raise ApiError.bad_request("File harus berupa gambar JPG, PNG, WEBP, atau GIF")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"profile-{current_user.id}-{uuid4()}{extension}"
        target = self.upload_dir / filename
        target.write_bytes(await file.read())
        current_user.profile_photo = str(request.base_url).rstrip("/") + f"/static/uploads/{filename}"
        return self.users.save(current_user)

    def set_blocked(self, user_id: UUID, is_blocked: bool) -> User:
        user = self.users.get(user_id)
        if not user:
            raise ApiError.not_found("User")
        user.account_status = AccountStatus.BANNED.value if is_blocked else AccountStatus.ACTIVE.value
        return self.users.save(user)


def conflict(detail: str) -> Exception:
    return ApiError.conflict(detail)
