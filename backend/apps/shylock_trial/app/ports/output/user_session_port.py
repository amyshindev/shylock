from abc import ABC, abstractmethod
from uuid import UUID


class UserSessionPort(ABC):
    @abstractmethod
    def issue_token(self, user_id: UUID) -> str: ...

    @abstractmethod
    def verify_token(self, token: str) -> UUID | None:
        """Return the user_id if the token is valid and unexpired, else None."""

    @abstractmethod
    def cookie_secure(self) -> bool: ...
