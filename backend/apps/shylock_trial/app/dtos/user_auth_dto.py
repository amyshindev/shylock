from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserDto:
    user_id: UUID
    email: str | None
    nickname: str


@dataclass(frozen=True, slots=True)
class JwtIdentityDto:
    """Identity resolved from a gateway-issued access token (core.security.TokenPayload)."""

    sub: str
    nickname: str | None = None
    email: str | None = None
