from typing import Any
from uuid import UUID

from arq import ArqRedis
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.quizzes.service import get_available_quiz_with_relations_by_id
from app.sessions.db_crud import (
    create_session as db_crud_create_session,
    get_sessions_total_count as db_crud_get_sessions_total_count,
    get_sessions_list as db_crud_get_sessions_list,
    get_session_with_relations_by_uuid as db_crud_get_session_with_relations_by_uuid,
    update_session_by_uuid as db_crud_update_session_by_uuid,
    soft_delete_session_by_uuid as db_crud_soft_delete_session_by_uuid,
    activate_session_by_id,
    bulk_create_and_return_session_questions,
)
from app.sessions.models import Session, SessionStatus
from app.sessions.redis_crud import set_session_info


async def create_session(
    title: str,
    description: str,
    time_seconds: int,
    room_id: int,
    quiz_id: int,
    db_session: AsyncSession,
) -> Session:
    session_db = await db_crud_create_session(
        title=title,
        description=description,
        time_seconds=time_seconds,
        room_id=room_id,
        quiz_id=quiz_id,
        db_session=db_session,
    )

    return session_db


async def get_sessions_total_count(
    room_id: int,
    db_session: AsyncSession,
) -> int:
    sessions_total_count = await db_crud_get_sessions_total_count(
        room_id=room_id,
        db_session=db_session,
    )

    return sessions_total_count


async def get_sessions_list(
    room_id: int,
    limit: int,
    offset: int,
    db_session: AsyncSession,
) -> list[Session]:
    sessions_db = await db_crud_get_sessions_list(
        room_id=room_id,
        limit=limit,
        offset=offset,
        db_session=db_session,
    )

    return sessions_db


async def get_session_with_relations_by_uuid(
    uuid: UUID,
    room_id: int,
    db_session: AsyncSession,
) -> Session:
    session_db = await db_crud_get_session_with_relations_by_uuid(
        uuid=uuid,
        room_id=room_id,
        db_session=db_session,
    )

    return session_db


async def update_session_by_uuid(
    uuid: UUID,
    room_id: int,
    update_session_data: dict[str, Any],
    db_session: AsyncSession,
) -> bool:
    is_updated = await db_crud_update_session_by_uuid(
        uuid=uuid,
        room_id=room_id,
        update_session_data=update_session_data,
        db_session=db_session,
    )

    return is_updated


async def soft_delete_session_by_uuid(
    uuid: UUID,
    room_id: int,
    db_session: AsyncSession,
) -> bool:
    is_deleted = await db_crud_soft_delete_session_by_uuid(
        uuid=uuid,
        room_id=room_id,
        db_session=db_session,
    )

    return is_deleted


async def start_session(
    room_id: int,
    user_id: int,
    room_uuid: UUID,
    session_uuid: UUID,
    db_session: AsyncSession,
    redis_client: Redis,
    arq_pool: ArqRedis,
) -> None:
    session_db = await get_session_with_relations_by_uuid(
        uuid=session_uuid,
        room_id=room_id,
        db_session=db_session,
    )

    if session_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session_db.status != SessionStatus.waiting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot start a session that is already active or completed",
        )

    quiz_db = await get_available_quiz_with_relations_by_id(
        id=session_db.quiz_id,
        user_id=user_id,
        db_session=db_session,
    )

    if quiz_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    questions_to_create = [
        {
            "text": question_db.text,
            "is_multiple_answers": question_db.is_multiple_answers,
            "options": [
                {
                    "text": option_db.text,
                    "is_correct": option_db.is_correct,
                }
                for option_db in question_db.options
            ],
        }
        for question_db in quiz_db.questions
    ]

    if questions_to_create:
        questions_db = await bulk_create_and_return_session_questions(
            session_id=session_db.id,
            create_session_questions_data=questions_to_create,
            db_session=db_session,
            mode="json",
        )
    else:
        questions_db = []

    await activate_session_by_id(
        id=session_db.id,
        room_id=room_id,
        db_session=db_session,
    )

    await set_session_info(
        room_uuid=room_uuid,
        session_uuid=session_db.uuid,
        time_seconds=session_db.time_seconds,
        questions_data=questions_db,
        redis_client=redis_client,
    )

    await arq_pool.enqueue_job(
        "auto_close_session",
        session_id=session_db.id,
        room_id=room_id,
        _defer_by=session_db.time_seconds,
    )
