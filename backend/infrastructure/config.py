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
    local_embedding_model: str = Field(
        default="intfloat/multilingual-e5-large-instruct",
        validation_alias="LOCAL_EMBEDDING_MODEL",
        description=(
            "sentence-transformers model — read by embed_main.py "
            "(the home-Mac process that actually loads it) and by "
            "backfill_local_embeddings.py; NOT read by local_embedding_client.py, "
            "which is just an HTTP client and doesn't need to know the model "
            "the server on the other end is running. Same caveat as "
            "cohere_embed_model: the play_lines/play_chunks.embedding_e5_1024 "
            "column name, LOCAL_EMBED_DIMENSION (play_line_orm.py), and the "
            "data written by backfill_local_embeddings.py all assume this "
            "exact model — swapping it needs a new migration + full "
            "re-backfill, not just an env var change."
        ),
    )
    local_embedding_base_url: str = Field(
        default="https://embed.shylock-trial.xyz",
        validation_alias="LOCAL_EMBEDDING_BASE_URL",
        description=(
            "embed_main.py address (home Mac, via Cloudflare "
            "Tunnel) — same pattern as ollama_base_url. This hostname is a "
            "suggestion, not yet a real route; the tunnel has to actually be "
            "created before EMBEDDING_PROVIDER=local can work in production. "
            "Override to e.g. http://localhost:8001 for local dev against a "
            "directly-run server on the same machine as the backend."
        ),
    )
    local_embedding_timeout_seconds: float = Field(
        default=10.0,
        validation_alias="LOCAL_EMBEDDING_TIMEOUT_SECONDS",
        description="Per-request timeout before falling back to Cohere.",
    )

    # Portia response generation provider. "claude" (default) uses
    # PortiaResponseClient only — this is the instant-revert path if "local"
    # misbehaves, just unset/reset this var. "local" wraps an Ollama client
    # with a Claude fallback (see dependencies/portia_response_provider.py) —
    # Ollama can't be relied on to always be up, so "local" never runs
    # without that fallback.
    llm_provider: str = Field(default="claude", validation_alias="LLM_PROVIDER")
    # Which backend turns text into an evidence-search query vector. "cohere"
    # (default) uses EvidenceSearchPgRepository only — the instant-revert
    # path if "local" misbehaves, just unset/reset this var. "local" wraps a
    # local sentence-transformers embedder with a Cohere fallback (see
    # dependencies/evidence_search_provider.py) — the local model isn't
    # guaranteed to always behave, so "local" never runs without that
    # fallback (which itself still falls back further, to curated evidence).
    # Named after the swapped technology (embedding), not the consuming
    # stem (evidence_search) — same convention as LLM_PROVIDER above.
    embedding_provider: str = Field(default="cohere", validation_alias="EMBEDDING_PROVIDER")
    # Separate from LLM_PROVIDER on purpose, even though both switch the same
    # underlying Ollama server on/off — lore_chat is a high-volume
    # player-facing Q&A widget, not trial-critical (see lore_chat_model_id's
    # description above), so it should be revertible independently of
    # portia_response without one bad rollout taking the other down with it.
    # "claude" (default) uses LoreChatClient only. "local" wraps
    # OllamaLoreChatClient with a Claude fallback (see
    # dependencies/lore_chat_provider.py), same never-runs-bare reasoning as
    # LLM_PROVIDER/EMBEDDING_PROVIDER.
    lore_chat_provider: str = Field(default="claude", validation_alias="LORE_CHAT_PROVIDER")
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
    # Separate Service Token for LOCAL_EMBEDDING_BASE_URL's Access Application
    # (deliberately not shared with cf_access_client_id/secret above, even
    # though it's the same home Mac + same tunnel process — a leaked/rotated
    # token then only affects one of the two tunneled services, not both).
    # Same empty-in-local-dev default as the Ollama pair.
    local_embedding_cf_access_client_id: str = Field(
        default="", validation_alias="LOCAL_EMBEDDING_CF_ACCESS_CLIENT_ID"
    )
    local_embedding_cf_access_client_secret: str = Field(
        default="", validation_alias="LOCAL_EMBEDDING_CF_ACCESS_CLIENT_SECRET"
    )

    # character_relation 그래프의 백엔드 선택 — LLM_PROVIDER/EMBEDDING_PROVIDER와
    # 같은 독립 스위치 패턴(infrastructure/config.py의 다른 *_provider 필드들
    # 참고). "pg"(기본값)는 지금 프로덕션이 쓰는 Postgres + recursive CTE
    # (character_relation_repository.py); "neo4j"는 포트폴리오용으로 추가한
    # 대체 게이트웨이(character_relation_neo4j_repository.py) — 노드 7개/엣지
    # 15개 규모에선 실질적으로 필요하진 않지만(recursive CTE로 이미 충분),
    # 그래프 네이티브 질의(Cypher)와 매니지드 그래프 DB 경험을 보여주기 위해
    # 의도적으로 추가함.
    character_relation_backend: str = Field(default="pg", validation_alias="CHARACTER_RELATION_BACKEND")
    neo4j_uri: str = Field(default="bolt://localhost:7687", validation_alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", validation_alias="NEO4J_USER")
    neo4j_password: SecretStr = Field(
        default=SecretStr(""),
        validation_alias="NEO4J_PASSWORD",
        description="로컬 Neo4j 인스턴스 초기 비밀번호 변경 후 여기에 설정.",
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

    def neo4j_password_plain(self) -> str:
        return self.neo4j_password.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()
