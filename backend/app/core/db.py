from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

_engine = create_async_engine(
    url=settings.db.url,
    pool_pre_ping=True,
)
_session_factory = async_sessionmaker(
    _engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, Any]:
    async with _session_factory.begin() as session:
        yield session


async def close_db_connection() -> None:
    await _engine.dispose()
