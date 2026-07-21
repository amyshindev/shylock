from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config import get_settings
from infrastructure.database import get_optional_db_session
from shylock_trial.adapter.outbound.env.user_session_repository import EnvUserSessionRepository
from shylock_trial.adapter.outbound.memory.user_auth_repository import InMemoryUserAuthRepository
from shylock_trial.adapter.outbound.pg.user_auth_repository import UserAuthPgRepository
from shylock_trial.app.constants.user_auth import USER_SESSION_COOKIE
from shylock_trial.app.dtos.user_auth_dto import UserDto
from shylock_trial.app.ports.input.user_auth_use_case import UserAuthUseCase
from shylock_trial.app.ports.output.user_auth_port import UserAuthPort
from shylock_trial.app.ports.output.user_session_port import UserSessionPort
from shylock_trial.app.use_cases.user_auth_interactor import UserAuthInteractor


def get_user_auth_repository(
    session: Annotated[AsyncSession | None, Depends(get_optional_db_session)],
) -> UserAuthPort:
    if get_settings().use_memory_store:
        return InMemoryUserAuthRepository.get_instance()
    if session is None:
        raise RuntimeError("Database session required when USE_MEMORY_STORE is disabled")
    return UserAuthPgRepository(session=session)


def get_user_session_repository() -> UserSessionPort:
    return EnvUserSessionRepository()


def get_user_auth_use_case(
    port: UserAuthPort = Depends(get_user_auth_repository),
    session: UserSessionPort = Depends(get_user_session_repository),
) -> UserAuthUseCase:
    return UserAuthInteractor(port=port, session=session)


async def get_current_user_optional(
    request: Request,
    use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
) -> UserDto | None:
    """Resolve the logged-in user from the session cookie; None for guests."""
    return await use_case.get_current_user(request.cookies.get(USER_SESSION_COOKIE))
