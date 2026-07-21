from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class User:
    user_id: UUID
    email: str
    nickname: str
    password_hash: str
