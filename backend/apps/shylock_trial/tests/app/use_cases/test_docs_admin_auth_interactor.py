import pytest

from shylock_trial.app.dtos.docs_admin_auth_dto import DocsAdminLoginInputDto
from shylock_trial.app.ports.output.docs_admin_auth_port import DocsAdminAuthPort
from shylock_trial.app.use_cases.docs_admin_auth_interactor import DocsAdminAuthInteractor


class _FakeDocsAdminAuthPort(DocsAdminAuthPort):
    def __init__(self) -> None:
        self.username = "admin"
        self.password = "secret"
        self.token = "session-token"

    async def verify_credentials(self, username: str, password: str) -> bool:
        return username == self.username and password == self.password

    def issue_session_token(self) -> str:
        return self.token

    def verify_session_token(self, token: str) -> bool:
        return token == self.token

    def cookie_secure(self) -> bool:
        return False


@pytest.fixture
def use_case() -> DocsAdminAuthInteractor:
    return DocsAdminAuthInteractor(port=_FakeDocsAdminAuthPort())


@pytest.mark.asyncio
async def test_login_success(use_case: DocsAdminAuthInteractor) -> None:
    result = await use_case.login(
        DocsAdminLoginInputDto(username="admin", password="secret"),
    )
    assert result.success is True
    assert result.session_token == "session-token"


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(use_case: DocsAdminAuthInteractor) -> None:
    result = await use_case.login(
        DocsAdminLoginInputDto(username="admin", password="wrong"),
    )
    assert result.success is False
    assert result.session_token is None


@pytest.mark.asyncio
async def test_login_rejects_blank_username(use_case: DocsAdminAuthInteractor) -> None:
    result = await use_case.login(
        DocsAdminLoginInputDto(username="   ", password="secret"),
    )
    assert result.success is False


def test_session_validation(use_case: DocsAdminAuthInteractor) -> None:
    assert use_case.is_session_valid("session-token") is True
    assert use_case.is_session_valid("other") is False
    assert use_case.is_session_valid(None) is False
