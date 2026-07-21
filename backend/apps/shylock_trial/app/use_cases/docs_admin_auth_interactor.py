from shylock_trial.app.dtos.docs_admin_auth_dto import (
    DocsAdminLoginInputDto,
    DocsAdminLoginResultDto,
)
from shylock_trial.app.ports.input.docs_admin_auth_use_case import DocsAdminAuthUseCase
from shylock_trial.app.ports.output.docs_admin_auth_port import DocsAdminAuthPort


class DocsAdminAuthInteractor(DocsAdminAuthUseCase):
    def __init__(self, port: DocsAdminAuthPort) -> None:
        self._port = port

    async def login(self, input_dto: DocsAdminLoginInputDto) -> DocsAdminLoginResultDto:
        username = input_dto.username.strip()
        if not username or not input_dto.password:
            return DocsAdminLoginResultDto(success=False)

        ok = await self._port.verify_credentials(username, input_dto.password)
        if not ok:
            return DocsAdminLoginResultDto(success=False)

        return DocsAdminLoginResultDto(
            success=True,
            session_token=self._port.issue_session_token(),
        )

    def is_session_valid(self, session_token: str | None) -> bool:
        if not session_token:
            return False
        return self._port.verify_session_token(session_token)
