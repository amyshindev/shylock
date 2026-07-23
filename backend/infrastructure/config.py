"""
Application settings — single source of truth for environment config.

Values are read from `.env` files (see `backend/.env.example` for keys and
dev templates). This module declares field names and types only — no
duplicate defaults for env-backed settings.

Load order (later overrides earlier):
  1. `<repo>/.env`
  2. `backend/.env`
  3. process environment variables
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            _PROJECT_ROOT / ".env",
            _BACKEND_DIR / ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(validation_alias="APP_ENV")
    log_level: str = Field(validation_alias="LOG_LEVEL")

    database_url: str = Field(validation_alias="DATABASE_URL")
    direct_url: str | None = Field(default=None, validation_alias="DIRECT_URL")
    redis_url: str = Field(validation_alias="REDIS_URL")
    use_memory_store: bool = Field(validation_alias="USE_MEMORY_STORE")
    cors_origins: str = Field(validation_alias="CORS_ORIGINS")

    anthropic_api_key: SecretStr = Field(
        validation_alias="ANTHROPIC_API_KEY",
        description="Anthropic API key (Claude).",
    )
    cohere_api_key: SecretStr = Field(
        validation_alias="COHERE_API_KEY",
        description="Cohere API key for evidence embeddings.",
    )

    # Cookie signing for /docs login gate (admin credential check comes later).
    docs_session_secret: SecretStr = Field(
        default=SecretStr("dev-only-change-me-docs-session-secret"),
        validation_alias="DOCS_SESSION_SECRET",
        description="HMAC secret for Swagger docs session cookie.",
    )
    docs_admin_username: str = Field(
        default="admin",
        validation_alias="DOCS_ADMIN_USERNAME",
        description="Admin username required to open /docs.",
    )
    docs_admin_password: SecretStr = Field(
        default=SecretStr("change-me-docs-admin-password"),
        validation_alias="DOCS_ADMIN_PASSWORD",
        description="Admin password required to open /docs.",
    )

    # Cookie signing for game user login sessions.
    auth_session_secret: SecretStr = Field(
        default=SecretStr("dev-only-change-me-auth-session-secret"),
        validation_alias="AUTH_SESSION_SECRET",
        description="HMAC secret for game user session cookies.",
    )

    # Google OAuth login (empty client id/secret disables the Google login route).
    google_client_id: str = Field(
        default="",
        validation_alias="GOOGLE_CLIENT_ID",
        description="Google Cloud OAuth 2.0 client ID.",
    )
    google_client_secret: SecretStr = Field(
        default=SecretStr(""),
        validation_alias="GOOGLE_CLIENT_SECRET",
        description="Google Cloud OAuth 2.0 client secret.",
    )
    google_redirect_uri: str = Field(
        default="http://localhost:8000/shylock-trial/auth/google/callback",
        validation_alias="GOOGLE_REDIRECT_URI",
        description="Registered Google OAuth redirect URI (backend callback).",
    )
    frontend_base_url: str = Field(
        default="http://localhost:3000",
        validation_alias="FRONTEND_BASE_URL",
        description="Frontend origin to return to after social login.",
    )

    def migration_database_url(self) -> str:
        """Direct DB URL for Alembic (bypasses pooler). Falls back to DATABASE_URL."""
        return self.direct_url or self.database_url

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def anthropic_api_key_plain(self) -> str:
        """Plain Anthropic key for outbound clients. Never log this value."""
        return self.anthropic_api_key.get_secret_value()

    def cohere_api_key_plain(self) -> str:
        """Plain Cohere key for outbound clients. Never log this value."""
        return self.cohere_api_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()
