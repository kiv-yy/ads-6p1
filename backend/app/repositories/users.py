from uuid import UUID

from app.models import AccountStatus, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def create(self, user: User) -> User:
        return self.save(user)

    def get(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_nim(self, nim: str) -> User | None:
        return self.db.query(User).filter(User.nim == nim).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def list(self, skip: int = 0, limit: int = 20, include_blocked: bool = True) -> list[User]:
        query = self.db.query(User)
        if not include_blocked:
            query = query.filter(User.account_status != AccountStatus.BANNED.value)
        return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
