"""Google OAuth2 client (accounts.google.com / googleapis.com)."""

from __future__ import annotations

from urllib.parse import urlencode

import httpx

from infrastructure.config import Settings, get_settings
from shylock_trial.app.dtos.user_auth_dto import GoogleProfileDto
from shylock_trial.app.ports.output.google_oauth_port import GoogleOAuthPort

_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
_TIMEOUT_SECONDS = 10.0


class GoogleOAuthClient(GoogleOAuthPort):
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def is_configured(self) -> bool:
        return bool(
            self._settings.google_client_id.strip()
            and self._settings.google_client_secret.get_secret_value().strip()
        )

    def authorize_url(self, state: str) -> str:
        params = {
            "client_id": self._settings.google_client_id,
            "redirect_uri": self._settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": self._settings.google_client_id,
            "client_secret": self._settings.google_client_secret.get_secret_value(),
            "redirect_uri": self._settings.google_redirect_uri,
            "code": code,
        }
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.post(_TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()["access_token"]

    async def fetch_profile(self, access_token: str) -> GoogleProfileDto:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.get(
                _USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            body = response.json()

        email = body.get("email") if body.get("verified_email") else None
        return GoogleProfileDto(
            google_id=str(body["id"]),
            nickname=body.get("name"),
            email=email,
        )
