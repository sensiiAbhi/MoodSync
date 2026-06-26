"""
MoodSync - App Config
Pydantic-based settings management with .env file support.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "MoodSync"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "change-me-in-production-minimum-32-characters-long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database — accepts both postgresql:// and postgresql+asyncpg://
    DATABASE_URL: str = "postgresql+asyncpg://moodsync_user:moodsync_secret@localhost:5432/moodsync"

    # Redis (optional)
    REDIS_URL: Optional[str] = None

    # Spotify
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/spotify/callback"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Gemini
    GEMINI_API_KEY: Optional[str] = None

    @property
    def async_database_url(self) -> str:
        """
        Render provides postgresql:// — SQLAlchemy asyncpg needs postgresql+asyncpg://
        This auto-converts so both local and Render environments work.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            # Heroku/Render legacy format
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
