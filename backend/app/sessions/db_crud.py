from typing import Any
from uuid import UUID

from sqlalchemy import insert, update, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.sessions.models import Session, SessionStatus


async def create_session(
    title: str,
    description: str,
    time_seconds: int,
    room_id: int,
    quiz_id: int,
    db_session: AsyncSession,
) -> Session:
    stmt = (
        insert(Session)
        .values(
            room_id=room_id,
            quiz_id=quiz_id,
            title=title,
            description=description,
            time_seconds=time_seconds,
        )
        .returning(Session)
    )
    result = await db_session.scalar(stmt)

    return result


async def get_sessions_total_count(
    room_id: int,
    db_session: AsyncSession,
) -> int:
    stmt = (
        select(func.count())
        .select_from(Session)
        .where(
            Session.room_id == room_id,
            Session.deleted_at.is_(None),
        )
    )
    result = await db_session.scalar(stmt)

    return result or 0


async def get_sessions_list(
    room_id: int,
    limit: int,
    offset: int,
    db_session: AsyncSession,
) -> list[Session]:
    stmt = (
        select(Session)
        .where(
            Session.room_id == room_id,
            Session.deleted_at.is_(None),
        )
        .order_by(Session.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db_session.scalars(stmt)

    return list(result.all())


async def update_session_by_uuid(
    uuid: UUID,
    room_id: int,
    update_session_data: dict[str, Any],
    db_session: AsyncSession,
) -> bool:
    stmt = (
        update(Session)
        .where(
            Session.uuid == uuid,
            Session.room_id == room_id,
            Session.deleted_at.is_(None),
            Session.status == SessionStatus.waiting,
        )
        .values(**update_session_data)
    )
    result = await db_session.execute(stmt)

    return result.rowcount == 1


async def soft_delete_session_by_uuid(
    uuid: UUID,
    room_id: int,
    db_session: AsyncSession,
) -> bool:
    stmt = (
        update(Session)
        .where(
            Session.uuid == uuid,
            Session.room_id == room_id,
            Session.deleted_at.is_(None),
            Session.status == SessionStatus.waiting,
        )
        .values(deleted_at=func.now())
    )
    result = await db_session.execute(stmt)

    return result.rowcount == 1
