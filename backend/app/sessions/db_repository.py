from typing import Any, Literal
from uuid import UUID, uuid7

from sqlalchemy import insert, update, func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.sessions.models import (
    Session,
    SessionStatus,
    SessionQuestion,
    SessionMember,
    SessionQuestionOption,
    SessionMemberAnswer,
)


async def _sessions_status_filter(
    status: Literal["all", "waiting", "active", "completed"],
) -> list[Any]:
    conditions = []

    if status != "all":
        conditions.append(Session.status == SessionStatus(status))

    return conditions


async def _sessions_search_filter(q: str | None = None) -> list[Any]:
    conditions = []

    if q is not None:
        conditions.append(
            or_(
                Session.search_vector.ilike(f"%{q}%"),
                Session.search_vector.bool_op("%>")(q),
            )
        )

    return conditions


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


async def get_sessions_total_count_by_room_id(
    room_id: int,
    db_session: AsyncSession,
    status: Literal["all", "waiting", "active", "completed"] = "all",
    q: str | None = None,
) -> int:
    status_filter = await _sessions_status_filter(status=status)
    search_filter = await _sessions_search_filter(q=q)
    stmt = (
        select(func.count())
        .select_from(Session)
        .where(
            *status_filter,
            *search_filter,
            Session.room_id == room_id,
            Session.deleted_at.is_(None),
        )
    )
    result = await db_session.scalar(stmt)

    return result or 0


async def get_sessions_total_count_by_user_id(
    user_id: int,
    db_session: AsyncSession,
    status: Literal["all", "waiting", "active", "completed"] = "all",
    q: str | None = None,
) -> int:
    status_filter = await _sessions_status_filter(status=status)
    search_filter = await _sessions_search_filter(q=q)
    stmt = (
        select(func.count())
        .select_from(Session)
        .join(Session.members)
        .where(
            *status_filter,
            *search_filter,
            SessionMember.user_id == user_id,
            Session.deleted_at.is_(None),
        )
    )
    result = await db_session.scalar(stmt)

    return result or 0


async def get_sessions_list_by_room_id(
    room_id: int,
    limit: int,
    offset: int,
    db_session: AsyncSession,
    status: Literal["all", "waiting", "active", "completed"] = "all",
    q: str | None = None,
) -> list[Session]:
    status_filter = await _sessions_status_filter(status=status)
    search_filter = await _sessions_search_filter(q=q)
    stmt = (
        select(Session)
        .where(
            *status_filter,
            *search_filter,
            Session.room_id == room_id,
            Session.deleted_at.is_(None),
        )
        .order_by(Session.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db_session.scalars(stmt)

    return list(result.all())


async def get_sessions_list_by_user_id(
    user_id: int,
    limit: int,
    offset: int,
    db_session: AsyncSession,
    status: Literal["all", "waiting", "active", "completed"] = "all",
    q: str | None = None,
) -> list[Session]:
    status_filter = await _sessions_status_filter(status=status)
    search_filter = await _sessions_search_filter(q=q)
    stmt = (
        select(Session)
        .join(Session.members)
        .where(
            *status_filter,
            *search_filter,
            SessionMember.user_id == user_id,
            Session.deleted_at.is_(None),
        )
        .order_by(Session.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db_session.scalars(stmt)

    return list(result.all())


async def get_session_with_relations_by_uuid(
    uuid: UUID,
    room_id: int,
    db_session: AsyncSession,
) -> Session | None:
    stmt = (
        select(Session)
        .where(
            Session.uuid == uuid,
            Session.room_id == room_id,
            Session.deleted_at.is_(None),
        )
        .options(selectinload(Session.questions).selectinload(SessionQuestion.options))
        .options(selectinload(Session.members).selectinload(SessionMember.answers))
    )
    result = await db_session.scalar(stmt)

    return result


async def get_session_with_relations_by_user_id(
    uuid: UUID,
    user_id: int,
    db_session: AsyncSession,
) -> Session | None:
    stmt = (
        select(Session)
        .join(Session.members)
        .where(
            SessionMember.user_id == user_id,
            Session.uuid == uuid,
            Session.deleted_at.is_(None),
        )
        .options(selectinload(Session.questions).selectinload(SessionQuestion.options))
        .options(selectinload(Session.members).selectinload(SessionMember.answers))
    )
    result = await db_session.scalar(stmt)

    return result


async def get_unscoped_session_by_uuid(
    uuid: UUID,
    db_session: AsyncSession,
) -> Session | None:
    stmt = select(Session).where(
        Session.uuid == uuid,
        Session.deleted_at.is_(None),
    )
    result = await db_session.scalar(stmt)

    return result


async def update_session_by_uuid(
    uuid: UUID,
    room_id: int,
    update_session_data: dict[str, Any],
    db_session: AsyncSession,
) -> bool:
    if not update_session_data:
        return False

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


async def activate_session_by_id(
    id: int,
    room_id: int,
    db_session: AsyncSession,
) -> bool:
    stmt = (
        update(Session)
        .where(
            Session.id == id,
            Session.room_id == room_id,
            Session.deleted_at.is_(None),
            Session.status == SessionStatus.waiting,
        )
        .values(status=SessionStatus.active)
    )
    result = await db_session.execute(stmt)

    return result.rowcount == 1


async def complete_session_by_id(
    id: int,
    room_id: int,
    db_session: AsyncSession,
) -> bool:
    stmt = (
        update(Session)
        .where(
            Session.id == id,
            Session.room_id == room_id,
            Session.deleted_at.is_(None),
            Session.status == SessionStatus.active,
        )
        .values(status=SessionStatus.completed)
    )
    result = await db_session.execute(stmt)

    return result.rowcount == 1


async def bulk_create_and_return_session_questions(
    session_id: int,
    create_session_questions_data: list[dict[str, Any]],
    db_session: AsyncSession,
    mode: Literal["python", "json"] = "python",
) -> list[dict[str, Any]]:
    if not create_session_questions_data:
        return []

    question_rows = []
    options_mapping = {}

    for question in create_session_questions_data:
        question_uuid = uuid7()

        question_rows.append(
            {
                "session_id": session_id,
                "text": question["text"],
                "is_multiple_answers": question["is_multiple_answers"],
                "uuid": question_uuid,
            }
        )

        options_mapping[question_uuid] = question["options"]

    if not question_rows:
        return []

    stmt = insert(SessionQuestion).values(question_rows).returning(SessionQuestion)
    created_questions = list(await db_session.scalars(stmt))
    option_rows = []

    for question_db in created_questions:
        mapped_options = options_mapping.get(question_db.uuid, [])

        for option_db_data in mapped_options:
            option_rows.append(
                {
                    "session_question_id": question_db.id,
                    "text": option_db_data["text"],
                    "is_correct": option_db_data["is_correct"],
                }
            )

    options_by_question_id = {}

    if option_rows:
        stmt = (
            insert(SessionQuestionOption)
            .values(option_rows)
            .returning(SessionQuestionOption)
        )
        created_options = list(await db_session.scalars(stmt))

        for option_db in created_options:
            option_uuid = str(option_db.uuid) if mode == "json" else option_db.uuid

            options_by_question_id.setdefault(option_db.session_question_id, []).append(
                {
                    "uuid": option_uuid,
                    "text": option_db.text,
                    "is_correct": option_db.is_correct,
                }
            )

    result = [
        {
            "uuid": str(question_db.uuid) if mode == "json" else question_db.uuid,
            "text": question_db.text,
            "is_multiple_answers": question_db.is_multiple_answers,
            "options": options_by_question_id.get(question_db.id, []),
        }
        for question_db in created_questions
    ]

    return result


async def bulk_create_session_members(
    session_id: int,
    create_session_members_data: list[dict[str, Any]],
    db_session: AsyncSession,
) -> None:
    if not create_session_members_data:
        return

    member_rows = [
        {
            "session_id": session_id,
            "user_id": member["user_id"],
        }
        for member in create_session_members_data
    ]

    if not member_rows:
        return

    stmt = insert(SessionMember).values(member_rows).returning(SessionMember)
    created_members = list(await db_session.scalars(stmt))
    member_mapping = {member_db.user_id: member_db.id for member_db in created_members}
    answer_rows = []

    for member_data in create_session_members_data:
        member_id = member_mapping.get(member_data["user_id"])

        if not member_id or not member_data.get("answers"):
            continue

        for answer in member_data["answers"]:
            answer_rows.append(
                {
                    "session_question_id": answer["session_question_id"],
                    "session_question_option_id": answer["session_question_option_id"],
                    "session_member_id": member_id,
                }
            )

    if not answer_rows:
        return

    stmt = insert(SessionMemberAnswer).values(answer_rows)

    await db_session.execute(stmt)
