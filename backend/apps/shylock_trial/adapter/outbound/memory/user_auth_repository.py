from uuid import UUID

from shylock_trial.app.ports.output.user_auth_port import UserAuthPort
from shylock_trial.domain.entities.user_entity import User


class InMemoryUserAuthRepository(UserAuthPort):
    _instance: "InMemoryUserAuthRepository | None" = None

    def __init__(self) -> None:
        self._by_id: dict[UUID, User] = {}

    @classmethod
    def get_instance(cls) -> "InMemoryUserAuthRepository":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def create_user(self, user: User) -> User:
        self._by_id[user.user_id] = user
        return user

    async def update_user(self, user: User) -> User:
        self._by_id[user.user_id] = user
        return user

    async def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._by_id.values() if u.email == email), None)

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self._by_id.get(user_id)

    async def find_by_google_id(self, google_id: str) -> User | None:
        return next((u for u in self._by_id.values() if u.google_id == google_id), None)
