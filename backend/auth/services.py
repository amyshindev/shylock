"""Auth gateway orchestration: Google OAuth + RS256 tokens + Redis refresh rotation."""

from __future__ import annotations

import json
import logging
import os
import secrets
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

import httpx
from redis.asyncio import Redis

from auth.rbac import Role
from core.security import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)

ACCESS_COOKIE = "shylock_access_token"
REFRESH_COOKIE = "shylock_refresh_token"
OAUTH_STATE_COOKIE = "shylock_oauth_state"

ACCESS_TTL_MIN = int(os.getenv("ACCESS_TOKEN_TTL_MIN", "10"))
REFRESH_TTL_SEC = int(os.getenv("REFRESH_TOKEN_TTL_SEC", str(60 * 60 * 24 * 14)))
SERVICE_AUD = os.getenv("SERVICE_AUD", "shylock-api")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "https://shylock-trial.xyz").rstrip("/")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "https://auth.shylock-trial.xyz/auth/callback/google",
)


@dataclass(frozen=True, slots=True)
class IssuedTokens:
    access_token: str
    refresh_token: str
    expires_in: int
    sub: str


def _redis() -> Redis:
    url = os.getenv("REDIS_URL", "").strip()
    if not url:
        raise RuntimeError("REDIS_URL is required for the auth gateway")
    return Redis.from_url(url, decode_responses=True)


async def google_authorize_url(state: str) -> str:
    if not GOOGLE_CLIENT_ID:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


async def _google_profile(code: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "authorization_code",
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "code": code,
            },
        )
        token_res.raise_for_status()
        access = token_res.json()["access_token"]
        profile_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access}"},
        )
        profile_res.raise_for_status()
        return profile_res.json()


def _subject_from_google(profile: dict[str, Any]) -> str:
    google_id = str(profile["id"])
    return f"google:{google_id}"


async def issue_session(sub: str, roles: list[str] | None = None) -> IssuedTokens:
    roles = roles or [Role.USER.value]
    access = create_access_token(sub=sub, roles=roles, aud=SERVICE_AUD, expires_min=ACCESS_TTL_MIN)
    refresh = create_refresh_token(sub)
    family_id = str(uuid4())
    client = _redis()
    try:
        pipe = client.pipeline()
        pipe.setex(
            f"auth:refresh:{refresh}",
            REFRESH_TTL_SEC,
            json.dumps({"sub": sub, "family_id": family_id}),
        )
        pipe.sadd(f"auth:user:{sub}:refresh", refresh)
        pipe.expire(f"auth:user:{sub}:refresh", REFRESH_TTL_SEC)
        await pipe.execute()
    finally:
        await client.aclose()
    return IssuedTokens(
        access_token=access,
        refresh_token=refresh,
        expires_in=ACCESS_TTL_MIN * 60,
        sub=sub,
    )


async def login_with_google_code(code: str) -> IssuedTokens:
    profile = await _google_profile(code)
    sub = _subject_from_google(profile)
    return await issue_session(sub)


async def revoke_user_sessions(sub: str) -> None:
    client = _redis()
    try:
        tokens = await client.smembers(f"auth:user:{sub}:refresh")
        pipe = client.pipeline()
        for token in tokens:
            pipe.delete(f"auth:refresh:{token}")
        pipe.delete(f"auth:user:{sub}:refresh")
        await pipe.execute()
    finally:
        await client.aclose()


async def rotate_refresh_token(refresh_token: str) -> IssuedTokens:
    """Rotate refresh token; reuse of an old token revokes the whole user session family."""
    client = _redis()
    try:
        raw = await client.get(f"auth:refresh:{refresh_token}")
        if raw is None:
            # Possible reuse: token was rotated away. If we can still find a tombstone, wipe user.
            tomb = await client.get(f"auth:refresh_used:{refresh_token}")
            if tomb:
                data = json.loads(tomb)
                await revoke_user_sessions(data["sub"])
                raise PermissionError("Refresh token reuse detected")
            raise PermissionError("Invalid refresh token")

        data = json.loads(raw)
        sub = data["sub"]
        family_id = data["family_id"]

        # Mark old token as used (tombstone) then delete active key.
        pipe = client.pipeline()
        pipe.setex(
            f"auth:refresh_used:{refresh_token}",
            REFRESH_TTL_SEC,
            json.dumps({"sub": sub, "family_id": family_id}),
        )
        pipe.delete(f"auth:refresh:{refresh_token}")
        pipe.srem(f"auth:user:{sub}:refresh", refresh_token)
        await pipe.execute()

        return await issue_session(sub)
    finally:
        await client.aclose()


async def logout(refresh_token: str | None, access_jti: str | None, access_exp: int | None) -> None:
    client = _redis()
    try:
        if refresh_token:
            raw = await client.get(f"auth:refresh:{refresh_token}")
            if raw:
                sub = json.loads(raw)["sub"]
                await client.delete(f"auth:refresh:{refresh_token}")
                await client.srem(f"auth:user:{sub}:refresh", refresh_token)
        if access_jti and access_exp:
            ttl = max(access_exp - int(__import__("time").time()), 1)
            await client.setex(f"auth:blacklist:jti:{access_jti}", ttl, "1")
    finally:
        await client.aclose()


def new_oauth_state() -> str:
    return secrets.token_urlsafe(16)
