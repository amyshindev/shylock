from abc import ABC, abstractmethod

from shylock_trial.domain.entities.user_entity import User


class UserAuthPort(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> User: ...

    @abstractmethod
    async def find_by_google_id(self, google_id: str) -> User | None: ...
