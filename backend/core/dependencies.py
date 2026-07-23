"""Shared FastAPI dependencies for JWT-protected business APIs."""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from core.rbac import Role
from core.security import TokenPayload, verify_token

ACCESS_COOKIE = "shylock_access_token"
SERVICE_AUD = os.getenv("SERVICE_AUD", "shylock-api")


def _extract_bearer(request: Request) -> str | None:
    header = request.headers.get("Authorization")
    if not header:
        return None
    scheme, _, value = header.partition(" ")
    if scheme.lower() != "bearer" or not value:
        return None
    return value.strip()


async def _is_jti_blacklisted(jti: str) -> bool:
    """Optional Redis blacklist check (jti). Missing Redis → treat as not blocked."""
    redis_url = os.getenv("REDIS_URL", "").strip()
    if not redis_url:
        return False
    try:
        from redis.asyncio import Redis

        client = Redis.from_url(redis_url, decode_responses=True)
        try:
            return bool(await client.exists(f"auth:blacklist:jti:{jti}"))
        finally:
            await client.aclose()
    except Exception:  # noqa: BLE001
        return False


async def get_current_user(request: Request) -> TokenPayload:
    token = request.cookies.get(ACCESS_COOKIE) or _extract_bearer(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    try:
        payload = verify_token(token, aud=SERVICE_AUD)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    if await _is_jti_blacklisted(payload.jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
        )
    return payload


class RoleChecker:
    def __init__(self, *allowed: Role) -> None:
        self._allowed = {role.value if isinstance(role, Role) else str(role) for role in allowed}

    def __call__(
        self,
        user: Annotated[TokenPayload, Depends(get_current_user)],
    ) -> TokenPayload:
        if not self._allowed.intersection(user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return user
