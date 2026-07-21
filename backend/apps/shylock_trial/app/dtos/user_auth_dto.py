from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SignupInputDto:
    email: str
    password: str
    nickname: str


@dataclass(frozen=True, slots=True)
class LoginInputDto:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class UserDto:
    user_id: UUID
    email: str
    nickname: str


@dataclass(frozen=True, slots=True)
class AuthResultDto:
    success: bool
    user: UserDto | None = None
    session_token: str | None = None
    error: str | None = None
