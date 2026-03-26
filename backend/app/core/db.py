from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from app.core.config import settings

_engine: AsyncEngine | None = None
_db_session_factory: async_sessionmaker | None = None


async def init_db() -> None:
    global _engine, _db_session_factory

    _engine = create_async_engine(
        url=settings.db.url,
        pool_pre_ping=True,
        echo=settings.app.debug,
    )
    _db_session_factory = async_sessionmaker(
        _engine,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_db_session_factory() -> async_sessionmaker:
    if _db_session_factory is None:
        raise RuntimeError("Database session factory is not initialized")

    return _db_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, Any]:
    if _db_session_factory is None:
        raise RuntimeError("Database session factory is not initialized")

    async with _db_session_factory.begin() as db_session:
        yield db_session


async def close_db_connection() -> None:
    global _engine

    if _engine:
        await _engine.dispose()

        _engine = None
