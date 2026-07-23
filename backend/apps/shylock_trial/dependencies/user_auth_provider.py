from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import ACCESS_COOKIE, SERVICE_AUD
from core.security import verify_token
from infrastructure.config import get_settings
from infrastructure.database import get_optional_db_session
from shylock_trial.adapter.outbound.memory.user_auth_repository import InMemoryUserAuthRepository
from shylock_trial.adapter.outbound.pg.user_auth_repository import UserAuthPgRepository
from shylock_trial.app.dtos.user_auth_dto import JwtIdentityDto, UserDto
from shylock_trial.app.ports.input.user_auth_use_case import UserAuthUseCase
from shylock_trial.app.ports.output.user_auth_port import UserAuthPort
from shylock_trial.app.use_cases.user_auth_interactor import UserAuthInteractor


def get_user_auth_repository(
    session: Annotated[AsyncSession | None, Depends(get_optional_db_session)],
) -> UserAuthPort:
    if get_settings().use_memory_store:
        return InMemoryUserAuthRepository.get_instance()
    if session is None:
        raise RuntimeError("Database session required when USE_MEMORY_STORE is disabled")
    return UserAuthPgRepository(session=session)


def get_user_auth_use_case(
    port: UserAuthPort = Depends(get_user_auth_repository),
) -> UserAuthUseCase:
    return UserAuthInteractor(port=port)


def _bearer_token(request: Request) -> str | None:
    scheme, _, value = request.headers.get("Authorization", "").partition(" ")
    return value.strip() if scheme.lower() == "bearer" and value else None


async def get_current_user_optional(
    request: Request,
    use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
) -> UserDto | None:
    """Resolve the logged-in user from the auth gateway's JWT; None for guests."""
    token = request.cookies.get(ACCESS_COOKIE) or _bearer_token(request)
    if not token:
        return None
    try:
        payload = verify_token(token, aud=SERVICE_AUD)
    except Exception:  # noqa: BLE001
        return None
    identity = JwtIdentityDto(
        sub=payload.sub,
        nickname=payload.raw.get("nickname"),
        email=payload.raw.get("email"),
    )
    return await use_case.get_or_create_user(identity)
