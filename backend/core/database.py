from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.app_env == "development",
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    if get_settings().use_memory_store:
        raise RuntimeError("DB session requested while USE_MEMORY_STORE is enabled")
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


async def get_optional_db_session() -> AsyncGenerator[AsyncSession | None, None]:
    if get_settings().use_memory_store:
        yield None
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
