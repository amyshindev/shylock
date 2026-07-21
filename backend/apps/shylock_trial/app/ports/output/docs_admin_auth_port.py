from abc import ABC, abstractmethod


class DocsAdminAuthPort(ABC):
    @abstractmethod
    async def verify_credentials(self, username: str, password: str) -> bool: ...

    @abstractmethod
    def issue_session_token(self) -> str: ...

    @abstractmethod
    def verify_session_token(self, token: str) -> bool: ...

    @abstractmethod
    def cookie_secure(self) -> bool: ...
