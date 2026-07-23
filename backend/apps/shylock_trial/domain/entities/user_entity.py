from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class User:
    user_id: UUID
    email: str | None
    nickname: str
    # None for social-only accounts (e.g. Google) that have no password.
    password_hash: str | None
    google_id: str | None = None
