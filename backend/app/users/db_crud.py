from uuid import UUID

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User


async def create_user(
    username: str,
    email: str,
    password: str,
    db_session: AsyncSession,
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
    result = await db_session.scalar(stmt)

    return result


async def get_user_by_email(
    email: str,
    db_session: AsyncSession,
) -> User | None:
    stmt = select(User).where(
        User.email == email,
        User.deleted_at.is_(None),
    )
    result = await db_session.scalar(stmt)

    return result


async def get_user_by_id(
    id: int,
    db_session: AsyncSession,
) -> User | None:
    stmt = select(User).where(
        User.id == id,
        User.deleted_at.is_(None),
    )
    result = await db_session.scalar(stmt)

    return result


async def get_user_by_uuid(
    uuid: UUID,
    db_session: AsyncSession,
) -> User | None:
    stmt = select(User).where(
        User.uuid == uuid,
        User.deleted_at.is_(None),
    )
    result = await db_session.scalar(stmt)

    return result


async def get_user_uuids_by_ids(
    ids: set[int],
    db_session: AsyncSession,
) -> dict[int, UUID]:
    stmt = select(User.id, User.uuid).where(
        User.id.in_(ids),
        User.deleted_at.is_(None),
    )
    result = await db_session.execute(stmt)
    result = dict(result.all())

    return result


async def get_user_ids_by_uuids(
    uuids: set[UUID],
    db_session: AsyncSession,
) -> dict[UUID, int]:
    stmt = select(User.uuid, User.id).where(
        User.uuid.in_(uuids),
        User.deleted_at.is_(None),
    )
    result = await db_session.execute(stmt)
    result = dict(result.all())

    return result


async def get_users_by_ids(
    ids: set[int],
    db_session: AsyncSession,
) -> dict[int, User]:
    stmt = select(User.id, User).where(
        User.id.in_(ids),
        User.deleted_at.is_(None),
    )
    result = await db_session.execute(stmt)
    result = dict(result.all())

    return result
