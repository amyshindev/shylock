from uuid import UUID

import pytest

from shylock_trial.app.dtos.user_auth_dto import JwtIdentityDto
from shylock_trial.app.ports.output.user_auth_port import UserAuthPort
from shylock_trial.app.use_cases.user_auth_interactor import UserAuthInteractor
from shylock_trial.domain.entities.user_entity import User


class _FakeUserRepo(UserAuthPort):
    def __init__(self) -> None:
        self._by_id: dict[UUID, User] = {}

    async def create_user(self, user: User) -> User:
        self._by_id[user.user_id] = user
        return user

    async def find_by_google_id(self, google_id: str) -> User | None:
        return next((u for u in self._by_id.values() if u.google_id == google_id), None)


@pytest.fixture
def interactor() -> UserAuthInteractor:
    return UserAuthInteractor(port=_FakeUserRepo())


@pytest.mark.asyncio
async def test_creates_user_on_first_login(interactor: UserAuthInteractor) -> None:
    user = await interactor.get_or_create_user(
        JwtIdentityDto(sub="google:12345", nickname="샤일록", email="shylock@venice.it")
    )
    assert user.nickname == "샤일록"
    assert user.email == "shylock@venice.it"


@pytest.mark.asyncio
async def test_reuses_existing_user_for_same_sub(interactor: UserAuthInteractor) -> None:
    first = await interactor.get_or_create_user(
        JwtIdentityDto(sub="google:12345", nickname="a")
    )
    second = await interactor.get_or_create_user(
        JwtIdentityDto(sub="google:12345", nickname="b")
    )
    assert first.user_id == second.user_id
    assert second.nickname == "a"  # nickname set once, at first login


@pytest.mark.asyncio
async def test_falls_back_to_default_nickname(interactor: UserAuthInteractor) -> None:
    user = await interactor.get_or_create_user(JwtIdentityDto(sub="google:999"))
    assert user.nickname == "베네치아의 이방인"
    assert user.email is None
