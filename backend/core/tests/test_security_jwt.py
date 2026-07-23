"""JWT RS256 verify / issue acceptance tests (harness §3)."""

from __future__ import annotations

import base64
import json

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from core.security import create_access_token, verify_token


@pytest.fixture
def rsa_keys(monkeypatch: pytest.MonkeyPatch) -> tuple[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    monkeypatch.setenv("JWT_PRIVATE_KEY", base64.b64encode(private_pem.encode()).decode())
    monkeypatch.setenv("JWT_PUBLIC_KEY", base64.b64encode(public_pem.encode()).decode())
    return private_pem, public_pem


def test_roundtrip_verify_with_public_only(
    rsa_keys: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    token = create_access_token(sub="google:1", roles=["user"], aud="shylock-api", expires_min=5)
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    payload = verify_token(token, aud="shylock-api")
    assert payload.sub == "google:1"
    assert "user" in payload.roles


def test_wrong_audience_rejected(rsa_keys: tuple[str, str]) -> None:
    token = create_access_token(sub="google:1", roles=["user"], aud="shylock-api")
    with pytest.raises(jwt.InvalidAudienceError):
        verify_token(token, aud="other-api")


def test_tampered_token_rejected(rsa_keys: tuple[str, str]) -> None:
    token = create_access_token(sub="google:1", roles=["user"], aud="shylock-api")
    parts = token.split(".")
    parts[1] = parts[1] + "x"
    with pytest.raises(jwt.PyJWTError):
        verify_token(".".join(parts), aud="shylock-api")


def test_alg_none_rejected(rsa_keys: tuple[str, str]) -> None:
    header = (
        base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode())
        .rstrip(b"=")
        .decode()
    )
    payload = (
        base64.urlsafe_b64encode(
            json.dumps(
                {
                    "sub": "x",
                    "roles": ["user"],
                    "aud": "shylock-api",
                    "exp": 9999999999,
                    "iat": 1,
                    "jti": "j",
                }
            ).encode()
        )
        .rstrip(b"=")
        .decode()
    )
    with pytest.raises(jwt.PyJWTError):
        verify_token(f"{header}.{payload}.", aud="shylock-api")


def test_hs256_forced_rejected(rsa_keys: tuple[str, str]) -> None:
    token = jwt.encode(
        {
            "sub": "x",
            "roles": ["user"],
            "aud": "shylock-api",
            "exp": 9999999999,
            "iat": 1,
            "jti": "j",
        },
        "not-the-private-key",
        algorithm="HS256",
    )
    with pytest.raises(jwt.PyJWTError):
        verify_token(token, aud="shylock-api")


def test_create_access_token_requires_private_key(
    monkeypatch: pytest.MonkeyPatch, rsa_keys: tuple[str, str]
) -> None:
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    with pytest.raises(RuntimeError, match="JWT_PRIVATE_KEY"):
        create_access_token(sub="x", roles=["user"], aud="shylock-api")
