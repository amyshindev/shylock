from uuid import uuid4

from shylock_trial.app.constants.user_auth import (
    EMAIL_MAX_LENGTH,
    NICKNAME_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
)
from dataclasses import replace

from shylock_trial.app.dtos.user_auth_dto import (
    AuthResultDto,
    GoogleProfileDto,
    LoginInputDto,
    SignupInputDto,
    UserDto,
)
from shylock_trial.app.ports.input.user_auth_use_case import UserAuthUseCase
from shylock_trial.app.ports.output.user_auth_port import UserAuthPort
from shylock_trial.app.ports.output.user_session_port import UserSessionPort
from shylock_trial.app.utils.password_hash import hash_password, verify_password
from shylock_trial.domain.entities.user_entity import User

_LOGIN_FAILED = "이메일 또는 비밀번호가 올바르지 않습니다."


def _to_user_dto(user: User) -> UserDto:
    return UserDto(user_id=user.user_id, email=user.email, nickname=user.nickname)


class UserAuthInteractor(UserAuthUseCase):
    def __init__(self, port: UserAuthPort, session: UserSessionPort) -> None:
        self._port = port
        self._session = session

    async def signup(self, input_dto: SignupInputDto) -> AuthResultDto:
        email = input_dto.email.strip().lower()
        nickname = input_dto.nickname.strip()

        if not email or "@" not in email or len(email) > EMAIL_MAX_LENGTH:
            return AuthResultDto(success=False, error="올바른 이메일을 입력해 주세요.")
        if not nickname or len(nickname) > NICKNAME_MAX_LENGTH:
            return AuthResultDto(
                success=False,
                error=f"닉네임은 1~{NICKNAME_MAX_LENGTH}자로 입력해 주세요.",
            )
        if len(input_dto.password) < PASSWORD_MIN_LENGTH:
            return AuthResultDto(
                success=False,
                error=f"비밀번호는 {PASSWORD_MIN_LENGTH}자 이상이어야 합니다.",
            )
        if await self._port.find_by_email(email) is not None:
            return AuthResultDto(success=False, error="이미 사용 중인 이메일입니다.")

        user = await self._port.create_user(
            User(
                user_id=uuid4(),
                email=email,
                nickname=nickname,
                password_hash=hash_password(input_dto.password),
            )
        )
        return AuthResultDto(
            success=True,
            user=_to_user_dto(user),
            session_token=self._session.issue_token(user.user_id),
        )

    async def login(self, input_dto: LoginInputDto) -> AuthResultDto:
        email = input_dto.email.strip().lower()
        user = await self._port.find_by_email(email)
        if (
            user is None
            or user.password_hash is None  # social-only account
            or not verify_password(input_dto.password, user.password_hash)
        ):
            return AuthResultDto(success=False, error=_LOGIN_FAILED)

        return AuthResultDto(
            success=True,
            user=_to_user_dto(user),
            session_token=self._session.issue_token(user.user_id),
        )

    async def login_with_google(self, profile: GoogleProfileDto) -> AuthResultDto:
        user = await self._port.find_by_google_id(profile.google_id)

        if user is None and profile.email:
            # Same verified email already registered: link Google to that account.
            existing = await self._port.find_by_email(profile.email.lower())
            if existing is not None:
                user = await self._port.update_user(
                    replace(existing, google_id=profile.google_id)
                )

        if user is None:
            nickname = (profile.nickname or "").strip() or "베네치아의 이방인"
            user = await self._port.create_user(
                User(
                    user_id=uuid4(),
                    email=profile.email.lower() if profile.email else None,
                    nickname=nickname[:NICKNAME_MAX_LENGTH],
                    password_hash=None,
                    google_id=profile.google_id,
                )
            )

        return AuthResultDto(
            success=True,
            user=_to_user_dto(user),
            session_token=self._session.issue_token(user.user_id),
        )

    async def get_current_user(self, session_token: str | None) -> UserDto | None:
        if not session_token:
            return None
        user_id = self._session.verify_token(session_token)
        if user_id is None:
            return None
        user = await self._port.find_by_id(user_id)
        return _to_user_dto(user) if user else None
