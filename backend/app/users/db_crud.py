from uuid import UUID

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User


async def create_user(
    username: str,
    email: str,
    password: str,
    session: AsyncSession,
) -> User:
    stmt = (
        insert(User)
        .values(
            username=username,
            email=email,
            password=password,
        )
        .returning(User)
    )
    result = await session.scalar(stmt)

    return result


async def get_user_by_email(
    email: str,
    session: AsyncSession,
) -> User | None:
    stmt = select(User).where(
        User.email == email,
        User.deleted_at.is_(None),
    )
    result = await session.scalar(stmt)

    return result


async def get_user_by_id(
    id: int,
    session: AsyncSession,
) -> User | None:
    stmt = select(User).where(
        User.id == id,
        User.deleted_at.is_(None),
    )
    result = await session.scalar(stmt)

    return result


async def get_user_by_uuid(
    uuid: UUID,
    session: AsyncSession,
) -> User | None:
    stmt = select(User).where(
        User.uuid == uuid,
        User.deleted_at.is_(None),
    )
    result = await session.scalar(stmt)

    return result


async def get_user_uuids_by_ids(
    ids: set[int],
    session: AsyncSession,
) -> dict[int, UUID]:
    stmt = select(User.id, User.uuid).where(
        User.id.in_(ids),
        User.deleted_at.is_(None),
    )
    result = await session.execute(stmt)
    result = dict(result.all())

    return result
