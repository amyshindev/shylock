from uuid import UUID, uuid4

import pytest

from shylock_trial.app.dtos.user_auth_dto import LoginInputDto, SignupInputDto
from shylock_trial.app.ports.output.user_auth_port import UserAuthPort
from shylock_trial.app.ports.output.user_session_port import UserSessionPort
from shylock_trial.app.use_cases.user_auth_interactor import UserAuthInteractor
from shylock_trial.domain.entities.user_entity import User


class _FakeUserRepo(UserAuthPort):
    def __init__(self) -> None:
        self._by_id: dict[UUID, User] = {}

    async def create_user(self, user: User) -> User:
        self._by_id[user.user_id] = user
        return user

    async def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._by_id.values() if u.email == email), None)

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self._by_id.get(user_id)


class _FakeSession(UserSessionPort):
    def issue_token(self, user_id: UUID) -> str:
        return f"token-{user_id}"

    def verify_token(self, token: str) -> UUID | None:
        if token.startswith("token-"):
            return UUID(token.removeprefix("token-"))
        return None

    def cookie_secure(self) -> bool:
        return False


@pytest.fixture
def interactor() -> UserAuthInteractor:
    return UserAuthInteractor(port=_FakeUserRepo(), session=_FakeSession())


@pytest.mark.asyncio
async def test_signup_and_login(interactor: UserAuthInteractor) -> None:
    signup = await interactor.signup(
        SignupInputDto(email="Shylock@Venice.IT", password="pound-of-flesh", nickname="샤일록")
    )
    assert signup.success is True
    assert signup.user is not None
    assert signup.user.email == "shylock@venice.it"  # normalized
    assert signup.session_token is not None

    login = await interactor.login(
        LoginInputDto(email="shylock@venice.it", password="pound-of-flesh")
    )
    assert login.success is True
    assert login.user is not None
    assert login.user.nickname == "샤일록"


@pytest.mark.asyncio
async def test_signup_rejects_duplicate_email(interactor: UserAuthInteractor) -> None:
    first = await interactor.signup(
        SignupInputDto(email="a@b.co", password="password123", nickname="one")
    )
    assert first.success is True
    dup = await interactor.signup(
        SignupInputDto(email="a@b.co", password="password456", nickname="two")
    )
    assert dup.success is False
    assert dup.error == "이미 사용 중인 이메일입니다."


@pytest.mark.asyncio
async def test_signup_validates_inputs(interactor: UserAuthInteractor) -> None:
    bad_email = await interactor.signup(
        SignupInputDto(email="not-an-email", password="password123", nickname="x")
    )
    assert bad_email.success is False

    short_pw = await interactor.signup(
        SignupInputDto(email="a@b.co", password="short", nickname="x")
    )
    assert short_pw.success is False


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(interactor: UserAuthInteractor) -> None:
    await interactor.signup(
        SignupInputDto(email="a@b.co", password="password123", nickname="x")
    )
    result = await interactor.login(LoginInputDto(email="a@b.co", password="wrong-password"))
    assert result.success is False
    assert result.user is None


@pytest.mark.asyncio
async def test_get_current_user(interactor: UserAuthInteractor) -> None:
    signup = await interactor.signup(
        SignupInputDto(email="a@b.co", password="password123", nickname="x")
    )
    assert signup.session_token is not None

    user = await interactor.get_current_user(signup.session_token)
    assert user is not None and user.email == "a@b.co"

    assert await interactor.get_current_user(None) is None
    assert await interactor.get_current_user(f"token-{uuid4()}") is None
