from abc import ABC, abstractmethod

from shylock_trial.app.dtos.user_auth_dto import JwtIdentityDto, UserDto


class UserAuthUseCase(ABC):
    @abstractmethod
    async def get_or_create_user(self, identity: JwtIdentityDto) -> UserDto: ...
