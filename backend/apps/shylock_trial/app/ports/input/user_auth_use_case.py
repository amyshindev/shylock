from abc import ABC, abstractmethod

from shylock_trial.app.dtos.user_auth_dto import (
    AuthResultDto,
    GoogleProfileDto,
    LoginInputDto,
    SignupInputDto,
    UserDto,
)


class UserAuthUseCase(ABC):
    @abstractmethod
    async def signup(self, input_dto: SignupInputDto) -> AuthResultDto: ...

    @abstractmethod
    async def login(self, input_dto: LoginInputDto) -> AuthResultDto: ...

    @abstractmethod
    async def login_with_google(self, profile: GoogleProfileDto) -> AuthResultDto: ...

    @abstractmethod
    async def get_current_user(self, session_token: str | None) -> UserDto | None: ...
