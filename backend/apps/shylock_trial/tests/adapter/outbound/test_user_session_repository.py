from uuid import uuid4

from pydantic import SecretStr

from infrastructure.config import Settings
from shylock_trial.adapter.outbound.env.user_session_repository import EnvUserSessionRepository


def _settings(secret: str = "test-secret") -> Settings:
    return Settings.model_construct(
        app_env="development",
        auth_session_secret=SecretStr(secret),
    )


def test_token_roundtrip() -> None:
    repo = EnvUserSessionRepository(settings=_settings())
    user_id = uuid4()
    token = repo.issue_token(user_id)
    assert repo.verify_token(token) == user_id


def test_tampered_token_rejected() -> None:
    repo = EnvUserSessionRepository(settings=_settings())
    token = repo.issue_token(uuid4())
    assert repo.verify_token(token + "0") is None
    assert repo.verify_token("garbage") is None


def test_token_signed_with_other_secret_rejected() -> None:
    token = EnvUserSessionRepository(settings=_settings("secret-a")).issue_token(uuid4())
    assert EnvUserSessionRepository(settings=_settings("secret-b")).verify_token(token) is None
