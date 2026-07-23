from uuid import uuid4

from shylock_trial.app.constants.user_auth import NICKNAME_MAX_LENGTH
from shylock_trial.app.dtos.user_auth_dto import JwtIdentityDto, UserDto
from shylock_trial.app.ports.input.user_auth_use_case import UserAuthUseCase
from shylock_trial.app.ports.output.user_auth_port import UserAuthPort
from shylock_trial.domain.entities.user_entity import User

_DEFAULT_NICKNAME = "베네치아의 이방인"


def _to_user_dto(user: User) -> UserDto:
    return UserDto(user_id=user.user_id, email=user.email, nickname=user.nickname)


class UserAuthInteractor(UserAuthUseCase):
    def __init__(self, port: UserAuthPort) -> None:
        self._port = port

    async def get_or_create_user(self, identity: JwtIdentityDto) -> UserDto:
        # Gateway JWT sub is "google:<id>"; the profile store keys on the bare id.
        google_id = identity.sub.removeprefix("google:")
        user = await self._port.find_by_google_id(google_id)
        if user is None:
            nickname = (identity.nickname or "").strip() or _DEFAULT_NICKNAME
            user = await self._port.create_user(
                User(
                    user_id=uuid4(),
                    email=identity.email.lower() if identity.email else None,
                    nickname=nickname[:NICKNAME_MAX_LENGTH],
                    password_hash=None,
                    google_id=google_id,
                )
            )
        return _to_user_dto(user)
