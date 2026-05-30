from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app import schemas
from app.core.security import PasswordService
from app.models import AccountStatus, User


class BaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, entity: Any) -> Any:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: Any) -> None:
        self.db.delete(entity)
        self.db.commit()


class UserRepository(BaseRepository):
    def __init__(self, db: Session, password_service: PasswordService | None = None) -> None:
        super().__init__(db)
        self.password_service = password_service or PasswordService()

    def create(self, user_in: schemas.UserCreate) -> User:
        username = user_in.username or user_in.nim
        nim = user_in.nim or username
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            username=username,
            faculty=user_in.faculty,
            nim=nim,
            hashed_password=self.password_service.hash(user_in.password),
            account_status=AccountStatus.INACTIVE.value,
        )
        return self.save(user)

    def get(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_nim(self, nim: str) -> User | None:
        return self.db.query(User).filter(User.nim == nim).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def update_profile(self, user: User, profile_in: schemas.UserProfileUpdate) -> User:
        payload = profile_in.model_dump(exclude_unset=True)
        for field, value in payload.items():
            if field in {"full_name", "username", "nim"} and value is None:
                continue
            setattr(user, field, value)
        return self.save(user)

    def list(self, skip: int = 0, limit: int = 20, include_blocked: bool = True) -> list[User]:
        query = self.db.query(User)
        if not include_blocked:
            query = query.filter(User.account_status != AccountStatus.BANNED.value)
        return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    def set_blocked(self, user: User, is_blocked: bool) -> User:
        user.account_status = AccountStatus.BANNED.value if is_blocked else AccountStatus.ACTIVE.value
        return self.save(user)

    def activate(self, user: User) -> User:
        user.account_status = AccountStatus.ACTIVE.value
        return self.save(user)

    def block(self, user: User) -> User:
        return self.set_blocked(user, True)
