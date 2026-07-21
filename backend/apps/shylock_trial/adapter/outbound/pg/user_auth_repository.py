from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shylock_trial.adapter.outbound.orm.user_orm import UserOrm
from shylock_trial.app.ports.output.user_auth_port import UserAuthPort
from shylock_trial.domain.entities.user_entity import User


def _to_entity(orm: UserOrm) -> User:
    return User(
        user_id=orm.user_id,
        email=orm.email,
        nickname=orm.nickname,
        password_hash=orm.password_hash,
    )


class UserAuthPgRepository(UserAuthPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_user(self, user: User) -> User:
        orm = UserOrm(
            user_id=user.user_id,
            email=user.email,
            nickname=user.nickname,
            password_hash=user.password_hash,
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return _to_entity(orm)

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserOrm).where(UserOrm.email == email))
        orm = result.scalar_one_or_none()
        return _to_entity(orm) if orm else None

    async def find_by_id(self, user_id: UUID) -> User | None:
        orm = await self._session.get(UserOrm, user_id)
        return _to_entity(orm) if orm else None
