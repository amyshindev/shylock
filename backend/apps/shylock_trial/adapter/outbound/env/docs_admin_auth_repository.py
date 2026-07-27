"""Env-backed admin credentials + HMAC session tokens for /docs gate."""

from __future__ import annotations

import hashlib
import hmac

from infrastructure.config import Settings, get_settings
from shylock_trial.app.ports.output.docs_admin_auth_port import DocsAdminAuthPort

_SESSION_PAYLOAD = b"docs-authenticated"


class EnvDocsAdminAuthRepository(DocsAdminAuthPort):
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def verify_credentials(self, username: str, password: str) -> bool:
        expected_user = self._settings.docs_admin_username
        expected_password = self._settings.docs_admin_password.get_secret_value()
        # Hash first so unequal lengths stay constant-time (compare_digest requires equal length).
        user_ok = hmac.compare_digest(
            hashlib.sha256(username.encode("utf-8")).digest(),
            hashlib.sha256(expected_user.encode("utf-8")).digest(),
        )
        password_ok = hmac.compare_digest(
            hashlib.sha256(password.encode("utf-8")).digest(),
            hashlib.sha256(expected_password.encode("utf-8")).digest(),
        )
        return user_ok and password_ok

    def issue_session_token(self) -> str:
        return hmac.new(
            self._settings.docs_session_secret.get_secret_value().encode("utf-8"),
            _SESSION_PAYLOAD,
            hashlib.sha256,
        ).hexdigest()

    def verify_session_token(self, token: str) -> bool:
        expected = self.issue_session_token()
        return hmac.compare_digest(token, expected)

    def cookie_secure(self) -> bool:
        return self._settings.app_env != "development"
