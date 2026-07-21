from abc import ABC, abstractmethod

from shylock_trial.app.dtos.docs_admin_auth_dto import (
    DocsAdminLoginInputDto,
    DocsAdminLoginResultDto,
)


class DocsAdminAuthUseCase(ABC):
    @abstractmethod
    async def login(self, input_dto: DocsAdminLoginInputDto) -> DocsAdminLoginResultDto: ...

    @abstractmethod
    def is_session_valid(self, session_token: str | None) -> bool: ...
