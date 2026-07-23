"""Refresh-token rotation / reuse detection (harness §3)."""

from __future__ import annotations

import base64
import json
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from auth import services


class _FakePipeline:
    def __init__(self, store: dict[str, Any], sets: dict[str, set[str]]) -> None:
        self._store = store
        self._sets = sets
        self._ops: list[tuple] = []

    def setex(self, key: str, ttl: int, value: str) -> "_FakePipeline":
        self._ops.append(("setex", key, value))
        return self

    def delete(self, *keys: str) -> "_FakePipeline":
        self._ops.append(("delete", keys))
        return self

    def sadd(self, key: str, value: str) -> "_FakePipeline":
        self._ops.append(("sadd", key, value))
        return self

    def srem(self, key: str, value: str) -> "_FakePipeline":
        self._ops.append(("srem", key, value))
        return self

    def expire(self, key: str, ttl: int) -> "_FakePipeline":
        return self

    async def execute(self) -> list[Any]:
        for op in self._ops:
            kind = op[0]
            if kind == "setex":
                self._store[op[1]] = op[2]
            elif kind == "delete":
                for k in op[1]:
                    self._store.pop(k, None)
                    self._sets.pop(k, None)
            elif kind == "sadd":
                self._sets.setdefault(op[1], set()).add(op[2])
            elif kind == "srem":
                self._sets.get(op[1], set()).discard(op[2])
        self._ops.clear()
        return []


class _FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.sets: dict[str, set[str]] = {}

    def pipeline(self) -> _FakePipeline:
        return _FakePipeline(self.store, self.sets)

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self.store[key] = value

    async def delete(self, *keys: str) -> None:
        for k in keys:
            self.store.pop(k, None)
            self.sets.pop(k, None)

    async def smembers(self, key: str) -> set[str]:
        return set(self.sets.get(key, set()))

    async def sadd(self, key: str, value: str) -> None:
        self.sets.setdefault(key, set()).add(value)

    async def srem(self, key: str, value: str) -> None:
        self.sets.get(key, set()).discard(value)

    async def aclose(self) -> None:
        return None


@pytest.fixture
def rsa_env(monkeypatch: pytest.MonkeyPatch) -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    monkeypatch.setenv("JWT_PRIVATE_KEY", base64.b64encode(private_pem).decode())
    monkeypatch.setenv("JWT_PUBLIC_KEY", base64.b64encode(public_pem).decode())
    monkeypatch.setenv("REDIS_URL", "redis://fake")
    monkeypatch.setenv("SERVICE_AUD", "shylock-api")


@pytest.fixture
def fake_redis(monkeypatch: pytest.MonkeyPatch) -> _FakeRedis:
    client = _FakeRedis()
    monkeypatch.setattr(services, "_redis", lambda: client)
    return client


@pytest.mark.asyncio
async def test_refresh_rotation_and_reuse_wipes_sessions(
    rsa_env: None, fake_redis: _FakeRedis
) -> None:
    first = await services.issue_session("google:42")
    old_refresh = first.refresh_token
    assert await fake_redis.get(f"auth:refresh:{old_refresh}")

    second = await services.rotate_refresh_token(old_refresh)
    assert second.refresh_token != old_refresh
    assert await fake_redis.get(f"auth:refresh:{old_refresh}") is None
    assert await fake_redis.get(f"auth:refresh_used:{old_refresh}")

    # Reuse of rotated token → all sessions for user wiped
    with pytest.raises(PermissionError, match="reuse"):
        await services.rotate_refresh_token(old_refresh)

    assert await fake_redis.get(f"auth:refresh:{second.refresh_token}") is None
    assert fake_redis.sets.get("auth:user:google:42:refresh", set()) == set()
