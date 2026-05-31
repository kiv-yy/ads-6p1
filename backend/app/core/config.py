from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./database/ads_lost_found.db"
    secret_key: str = "change-this-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    frontend_url: str = "http://127.0.0.1:3000"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    email_verification_expire_minutes: int = 60
    password_reset_expire_minutes: int = 30
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str = "noreply@apps.ipb.ac.id"
    smtp_use_tls: bool = True
    smtp_timeout_seconds: int = 15
    resend_api_key: str | None = None
    resend_from_email: str = "IPB Lost & Found <noreply@lostfoundipb.my.id>"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def allowed_origins(self) -> list[str]:
        origins = [self.frontend_url, *self.cors_origins.split(",")]
        return list(dict.fromkeys(origin.strip().rstrip("/") for origin in origins if origin.strip()))


@lru_cache
def get_settings() -> Settings:
    return Settings()
