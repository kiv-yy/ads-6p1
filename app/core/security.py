from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db
from app.models import AccountStatus, User, UserRole
from app.schemas import TokenData


settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class PasswordService:
    def __init__(self, context: CryptContext = pwd_context) -> None:
        self.context = context

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.context.verify(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        return self.context.hash(password)


class TokenService:
    def __init__(
        self,
        secret_key: str = settings.secret_key,
        algorithm: str = settings.algorithm,
        expires_minutes: int = settings.access_token_expire_minutes,
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expires_minutes = expires_minutes

    def create_access_token(self, subject: str, expires_delta: timedelta | None = None) -> str:
        expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=self.expires_minutes))
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_subject(self, token: str) -> UUID:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Missing token subject")
        return UUID(str(user_id))


class AuthService:
    def __init__(
        self,
        db: Session,
        password_service: PasswordService | None = None,
        token_service: TokenService | None = None,
    ) -> None:
        self.db = db
        self.password_service = password_service or PasswordService()
        self.token_service = token_service or TokenService()

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.db.query(User).filter(User.email == email.lower()).first()
        if not user or not self.password_service.verify(password, user.hashed_password):
            return None
        return user

    def get_current_user(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            token_data = TokenData(user_id=self.token_service.decode_subject(token))
        except (JWTError, ValueError):
            raise credentials_exception

        if token_data.user_id is None:
            raise credentials_exception

        user = self.db.get(User, token_data.user_id)
        if user is None:
            raise credentials_exception
        if user.account_status != AccountStatus.ACTIVE.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or blocked")
        return user


password_service = PasswordService()
token_service = TokenService()


def get_password_hash(password: str) -> str:
    return password_service.hash(password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    return token_service.create_access_token(subject, expires_delta)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    return AuthService(db).get_current_user(token)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
