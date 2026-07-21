import pytest
from pydantic import SecretStr

from infrastructure.config import Settings
from shylock_trial.adapter.outbound.env.docs_admin_auth_repository import (
    EnvDocsAdminAuthRepository,
)


def _settings() -> Settings:
    return Settings.model_construct(
        app_env="development",
        log_level="INFO",
        database_url="postgresql://unused",
        direct_url=None,
        redis_url="redis://unused",
        use_memory_store=True,
        cors_origins="http://localhost:3000",
        anthropic_api_key=SecretStr("x"),
        cohere_api_key=SecretStr("x"),
        docs_session_secret=SecretStr("test-docs-session-secret"),
        docs_admin_username="admin",
        docs_admin_password=SecretStr("correct-horse"),
    )


@pytest.mark.asyncio
async def test_env_repo_accepts_matching_credentials() -> None:
    repo = EnvDocsAdminAuthRepository(settings=_settings())
    assert await repo.verify_credentials("admin", "correct-horse") is True
    assert await repo.verify_credentials("admin", "wrong") is False
    assert await repo.verify_credentials("nope", "correct-horse") is False


def test_env_repo_session_roundtrip() -> None:
    repo = EnvDocsAdminAuthRepository(settings=_settings())
    token = repo.issue_session_token()
    assert repo.verify_session_token(token) is True
    assert repo.verify_session_token("deadbeef") is False
