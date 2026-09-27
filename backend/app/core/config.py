"""Application settings, loaded from the environment via pydantic-settings.

All non-secret fields ship with development-friendly defaults so the project
runs (and its tests pass) straight after ``git clone`` with no ``.env`` file.
Secrets such as ``SECRET_KEY`` must be overridden in production; ``get_settings``
enforces that.
"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from pydantic import AliasChoices, BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

_DEFAULT_SECRET_KEY = "change-me-in-production-use-a-long-random-string"


def _parse_cors(value: Any) -> Any:
    """Accept either a JSON list or a comma-separated string for CORS origins."""
    if isinstance(value, str) and not value.startswith("["):
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    if isinstance(value, (list, str)):
        return value
    raise ValueError(value)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "FastAPI Vue Starter"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    backend_cors_origins: Annotated[list[str] | str, BeforeValidator(_parse_cors)] = [
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    # --- Database ---
    # The runtime (async) and Alembic (sync) URLs are derived from these fields.
    # Under Docker Compose, POSTGRES_SERVER is overridden to the ``db`` service.
    postgres_server: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "backend_db"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    # Optional escape hatch: set DATABASE_URL to override the derived URL entirely
    # (useful on hosts such as Render/Railway/Heroku that inject a single URL).
    database_url_override: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "database_url_override"),
    )

    # --- Cache / broker (optional) ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Security / JWT ---
    secret_key: str = _DEFAULT_SECRET_KEY
    access_token_expire_minutes: int = 30
    jwt_algorithm: str = "HS256"

    # --- Email (optional) ---
    email_from: str = "noreply@example.com"
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None

    @property
    def database_url(self) -> str:
        """Synchronous (psycopg2) URL — used by Alembic migrations."""
        if self.database_url_override:
            return self.database_url_override
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def async_database_url(self) -> str:
        """Async (asyncpg) URL — used by the application at runtime."""
        return get_async_database_url(self.database_url)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


def get_async_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql+psycopg2"):
        return database_url.replace("psycopg2", "asyncpg", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and settings.secret_key == _DEFAULT_SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY must be set to a strong, unique value when "
            "ENVIRONMENT=production."
        )
    return settings
