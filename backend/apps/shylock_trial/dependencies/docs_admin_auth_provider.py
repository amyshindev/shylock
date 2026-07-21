from fastapi import Depends

from shylock_trial.adapter.outbound.env.docs_admin_auth_repository import (
    EnvDocsAdminAuthRepository,
)
from shylock_trial.app.ports.input.docs_admin_auth_use_case import DocsAdminAuthUseCase
from shylock_trial.app.ports.output.docs_admin_auth_port import DocsAdminAuthPort
from shylock_trial.app.use_cases.docs_admin_auth_interactor import DocsAdminAuthInteractor


def get_docs_admin_auth_repository() -> DocsAdminAuthPort:
    return EnvDocsAdminAuthRepository()


def get_docs_admin_auth_use_case(
    port: DocsAdminAuthPort = Depends(get_docs_admin_auth_repository),
) -> DocsAdminAuthUseCase:
    return DocsAdminAuthInteractor(port=port)
