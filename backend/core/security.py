"""JWT RS256 issue/verify helpers for the auth gateway.

Issuance (private key) is auth-container only and is read lazily at call time.
Verification uses the public key only — safe to import from the API container.
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from jwt.algorithms import RSAAlgorithm

# Absolute rule: verification algorithms are a hard-coded literal — never from env.
_VERIFY_ALGORITHMS = ["RS256"]

COOKIE_KWARGS: dict[str, Any] = {
    "domain": os.getenv("COOKIE_DOMAIN", ".shylock-trial.xyz"),
    "secure": os.getenv("APP_ENV", "production") != "development",
    "httponly": True,
    "samesite": "lax",
}


@dataclass(frozen=True, slots=True)
class TokenPayload:
    sub: str
    roles: list[str]
    aud: str
    exp: int
    iat: int
    jti: str
    raw: dict[str, Any]


def _pem_from_env(name: str) -> str:
    """Read a PEM from env; supports raw PEM or base64-encoded PEM."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not set")
    if "BEGIN" in value:
        return value.replace("\\n", "\n")
    try:
        decoded = base64.b64decode(value).decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"{name} is not valid PEM or base64 PEM") from exc
    if "BEGIN" not in decoded:
        raise RuntimeError(f"{name} decoded value is not a PEM")
    return decoded


def _kid_from_public_pem(public_pem: str) -> str:
    digest = hashlib.sha256(public_pem.encode("utf-8")).hexdigest()
    return digest[:16]


def create_access_token(
    sub: str,
    roles: list[str],
    aud: str,
    expires_min: int = 10,
    extra: dict[str, Any] | None = None,
) -> str:
    """Sign an access JWT with the private key (auth container only).

    ``extra`` carries optional profile claims (e.g. nickname, email) captured
    at login time so downstream services can bootstrap a user record without
    calling back out to the identity provider.
    """
    private_pem = _pem_from_env("JWT_PRIVATE_KEY")
    public_pem = _pem_from_env("JWT_PUBLIC_KEY")
    now = datetime.now(timezone.utc)
    kid = os.getenv("JWT_KID") or _kid_from_public_pem(public_pem)
    payload = {
        "sub": sub,
        "roles": roles,
        "aud": aud,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_min)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(
        payload,
        private_pem,
        algorithm="RS256",
        headers={"kid": kid},
    )


def create_refresh_token(sub: str) -> str:
    """Opaque refresh token (stored in Redis by the auth service)."""
    # sub is unused in the token body; kept for API compatibility with the harness.
    _ = sub
    return secrets.token_urlsafe(48)


def verify_token(token: str, aud: str) -> TokenPayload:
    """Verify an access JWT with the public key only (all containers)."""
    public_pem = _pem_from_env("JWT_PUBLIC_KEY")
    raw = jwt.decode(
        token,
        public_pem,
        algorithms=_VERIFY_ALGORITHMS,
        audience=aud,
        options={"require": ["exp", "iat", "sub", "aud", "jti"]},
    )
    roles = raw.get("roles") or []
    if not isinstance(roles, list):
        roles = []
    return TokenPayload(
        sub=str(raw["sub"]),
        roles=[str(r) for r in roles],
        aud=str(raw["aud"]),
        exp=int(raw["exp"]),
        iat=int(raw["iat"]),
        jti=str(raw["jti"]),
        raw=raw,
    )


def public_jwk() -> dict[str, Any]:
    """Return the public key as a JWK dict (for JWKS endpoint)."""
    import json

    from cryptography.hazmat.primitives import serialization

    public_pem = _pem_from_env("JWT_PUBLIC_KEY")
    pub = serialization.load_pem_public_key(public_pem.encode("utf-8"))
    jwk = json.loads(RSAAlgorithm.to_jwk(pub))
    jwk["kid"] = os.getenv("JWT_KID") or _kid_from_public_pem(public_pem)
    jwk["alg"] = "RS256"
    jwk["use"] = "sig"
    return jwk


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def is_expired(exp: int) -> bool:
    return int(time.time()) >= exp
