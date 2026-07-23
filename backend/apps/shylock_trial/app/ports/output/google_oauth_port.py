from abc import ABC, abstractmethod

from shylock_trial.app.dtos.user_auth_dto import GoogleProfileDto


class GoogleOAuthPort(ABC):
    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    def authorize_url(self, state: str) -> str:
        """Google consent page URL the browser should be redirected to."""

    @abstractmethod
    async def exchange_code(self, code: str) -> str:
        """Exchange the authorization code for an access token."""

    @abstractmethod
    async def fetch_profile(self, access_token: str) -> GoogleProfileDto: ...
