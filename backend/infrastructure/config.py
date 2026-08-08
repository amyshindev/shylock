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

    # Model IDs — the single place to look up (or bump) which model each
    # Claude/Cohere adapter/outbound/client/*.py calls, instead of a
    # `MODEL_ID = "..."` constant buried inside each file.
    claude_model_id: str = Field(
        default="claude-sonnet-5",
        validation_alias="CLAUDE_MODEL_ID",
        description=(
            "Narrative/agentic Claude calls: portia_response_client, "
            "portia_agent_client, tubal_agent_client, tubal_enhancement_client."
        ),
    )
    lore_chat_model_id: str = Field(
        default="claude-haiku-4-5-20251001",
        validation_alias="LORE_CHAT_MODEL_ID",
        description=(
            "Deliberately a lighter/cheaper model than claude_model_id — "
            "lore_chat is a high-volume player-facing Q&A widget, not a "
            "trial-critical narrative beat."
        ),
    )
    cohere_embed_model: str = Field(
        default="embed-v4.0",
        validation_alias="COHERE_EMBED_MODEL",
        description=(
            "Cohere embedding model for evidence_embedding_client. Changing "
            "this must stay in sync with the pgvector column width "
            "(EMBED_DIMENSION) and existing corpus embeddings — not a "
            "no-op swap."
        ),
    )

    # Portia response generation provider. "claude" (default) uses
    # PortiaResponseClient only — this is the instant-revert path if "local"
    # misbehaves, just unset/reset this var. "local" wraps an Ollama client
    # with a Claude fallback (see dependencies/portia_response_provider.py) —
    # Ollama can't be relied on to always be up, so "local" never runs
    # without that fallback.
    llm_provider: str = Field(default="claude", validation_alias="LLM_PROVIDER")
    ollama_base_url: str = Field(
        default="https://ollama.shylock-trial.xyz",
        validation_alias="OLLAMA_BASE_URL",
        description=(
            "Ollama server address — defaults to the home-Mac Cloudflare "
            "Tunnel so deploys work out of the box without an OLLAMA_BASE_URL "
            "override (no .env.backend* file in this repo sets one). Override "
            "to http://localhost:11434 for local dev against a local Ollama."
        ),
    )
    ollama_model: str = Field(default="gemma4:26b-mlx", validation_alias="OLLAMA_MODEL")
    ollama_timeout_seconds: float = Field(
        default=15.0,
        validation_alias="OLLAMA_TIMEOUT_SECONDS",
        description="Per-request timeout before falling back to Claude.",
    )
    # Cloudflare Access Service Token — only needed once OLLAMA_BASE_URL points
    # at a public Cloudflare Tunnel hostname (e.g. the home Mac) gated by an
    # Access policy. Empty/unset in local dev, where Ollama is plain
    # localhost with no tunnel in front of it.
    cf_access_client_id: str = Field(default="", validation_alias="CF_ACCESS_CLIENT_ID")
    cf_access_client_secret: str = Field(default="", validation_alias="CF_ACCESS_CLIENT_SECRET")

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

    def migration_database_url(self) -> str:
        """Direct DB URL for Alembic (bypasses pooler). Falls back to DATABASE_URL."""
        return self.direct_url or self.database_url

    @property
    def cors_origin_list(self) -> list[str]:
        configured = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        # Always allow the public frontend hosts (tunnel / Cloudflare), even if
        # a host's .env.backend still only lists localhost from a local template.
        required = (
            "https://shylock-trial.xyz",
            "https://www.shylock-trial.xyz",
        )
        return list(dict.fromkeys([*configured, *required]))

    def anthropic_api_key_plain(self) -> str:
        """Plain Anthropic key for outbound clients. Never log this value."""
        return self.anthropic_api_key.get_secret_value()

    def cohere_api_key_plain(self) -> str:
        """Plain Cohere key for outbound clients. Never log this value."""
        return self.cohere_api_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()
