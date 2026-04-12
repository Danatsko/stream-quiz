from uuid import UUID, uuid7
from typing import Any

from sqlalchemy import or_, select, func, update, delete, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.quizzes.models import Quiz, QuizQuestion, QuizQuestionOption


async def create_quiz(
    title: str,
    description: str,
    creator_id: int,
    db_session: AsyncSession,
) -> Quiz:
    stmt = (
        insert(Quiz)
        .values(
            creator_id=creator_id,
            title=title,
            description=description,
        )
        .returning(Quiz)
    )
    result = await db_session.scalar(stmt)

    return result


async def get_available_quizzes_total_count(
    user_id: int,
    db_session: AsyncSession,
) -> int:
    stmt = (
        select(func.count())
        .select_from(Quiz)
        .where(
            or_(
                Quiz.is_public.is_(True),
                Quiz.creator_id == user_id,
            ),
            Quiz.deleted_at.is_(None),
        )
    )
    result = await db_session.scalar(stmt)

    return result or 0


async def get_available_quizzes_list(
    user_id: int,
    limit: int,
    offset: int,
    db_session: AsyncSession,
) -> list[tuple[Quiz, int]]:
    stmt = (
        select(
            Quiz,
            func.count(QuizQuestion.id).label("total_questions"),
        )
        .outerjoin(QuizQuestion, QuizQuestion.quiz_id == Quiz.id)
        .where(
            or_(
                Quiz.is_public.is_(True),
                Quiz.creator_id == user_id,
            ),
            Quiz.deleted_at.is_(None),
        )
        .group_by(Quiz.id)
        .order_by(Quiz.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db_session.execute(stmt)

    return [(quiz, total) for quiz, total in result.all()]


async def get_available_quiz_by_uuid(
    uuid: UUID,
    user_id: int,
    db_session: AsyncSession,
) -> Quiz | None:
    stmt = select(Quiz).where(
        Quiz.uuid == uuid,
        or_(
            Quiz.is_public.is_(True),
            Quiz.creator_id == user_id,
        ),
        Quiz.deleted_at.is_(None),
    )
    result = await db_session.scalar(stmt)

    return result


async def get_available_quiz_by_id(
    id: int,
    user_id: int,
    db_session: AsyncSession,
) -> Quiz | None:
    stmt = select(Quiz).where(
        Quiz.id == id,
        or_(
            Quiz.is_public.is_(True),
            Quiz.creator_id == user_id,
        ),
        Quiz.deleted_at.is_(None),
    )
    result = await db_session.scalar(stmt)

    return result


async def get_available_quiz_with_relations_by_uuid(
    uuid: UUID,
    user_id: int,
    db_session: AsyncSession,
) -> Quiz | None:
    stmt = (
        select(Quiz)
        .where(
            Quiz.uuid == uuid,
            or_(
                Quiz.is_public.is_(True),
                Quiz.creator_id == user_id,
            ),
            Quiz.deleted_at.is_(None),
        )
        .options(selectinload(Quiz.questions).selectinload(QuizQuestion.options))
    )
    result = await db_session.scalar(stmt)

    return result


async def get_available_quiz_with_relations_by_id(
    id: int,
    user_id: int,
    db_session: AsyncSession,
) -> Quiz | None:
    stmt = (
        select(Quiz)
        .where(
            Quiz.id == id,
            or_(
                Quiz.is_public.is_(True),
                Quiz.creator_id == user_id,
            ),
            Quiz.deleted_at.is_(None),
        )
        .options(selectinload(Quiz.questions).selectinload(QuizQuestion.options))
    )
    result = await db_session.scalar(stmt)

    return result


async def get_available_quiz_uuids_by_ids(
    ids: set[int],
    user_id: int,
    db_session: AsyncSession,
) -> dict[int, UUID]:
    if not ids:
        return {}

    stmt = select(Quiz.id, Quiz.uuid).where(
        Quiz.id.in_(ids),
        or_(
            Quiz.is_public.is_(True),
            Quiz.creator_id == user_id,
        ),
        Quiz.deleted_at.is_(None),
    )
    result = await db_session.execute(stmt)
    result = dict(result.all())

    return result


async def get_quiz_with_relations_by_uuid(
    uuid: UUID,
    user_id: int,
    db_session: AsyncSession,
) -> Quiz | None:
    stmt = (
        select(Quiz)
        .where(
            Quiz.uuid == uuid,
            Quiz.creator_id == user_id,
            Quiz.deleted_at.is_(None),
        )
        .options(selectinload(Quiz.questions).selectinload(QuizQuestion.options))
    )
    result = await db_session.scalar(stmt)

    return result


async def update_quiz_by_uuid(
    uuid: UUID,
    user_id: int,
    update_quiz_data: dict[str, Any],
    db_session: AsyncSession,
) -> bool:
    if not update_quiz_data:
        return False

    stmt = (
        update(Quiz)
        .where(
            Quiz.uuid == uuid,
            Quiz.creator_id == user_id,
            Quiz.deleted_at.is_(None),
        )
        .values(**update_quiz_data)
    )
    result = await db_session.execute(stmt)

    return result.rowcount == 1


async def soft_delete_quiz_by_uuid(
    uuid: UUID,
    user_id: int,
    db_session: AsyncSession,
) -> bool:
    stmt = (
        update(Quiz)
        .where(
            Quiz.uuid == uuid,
            Quiz.creator_id == user_id,
            Quiz.deleted_at.is_(None),
        )
        .values(deleted_at=func.now())
    )
    result = await db_session.execute(stmt)

    return result.rowcount == 1


async def bulk_create_quiz_questions(
    quiz_id: int,
    create_quiz_questions_data: list[dict[str, Any]],
    db_session: AsyncSession,
) -> None:
    if not create_quiz_questions_data:
        return

    question_rows = []
    options_mapping = {}

    for question_data in create_quiz_questions_data:
        question_uuid = uuid7()

        question_rows.append(
            {
                "quiz_id": quiz_id,
                "text": question_data["text"],
                "is_multiple_answers": question_data["is_multiple_answers"],
                "uuid": question_uuid,
            }
        )

        options_mapping[question_uuid] = question_data["options"]

    if not question_rows:
        return

    stmt = insert(QuizQuestion).values(question_rows).returning(QuizQuestion)
    created_questions = list(await db_session.scalars(stmt))
    option_rows = []

    for question_db in created_questions:
        mapped_options = options_mapping.get(question_db.uuid, [])

        for option in mapped_options:
            option_rows.append(
                {
                    "quiz_question_id": question_db.id,
                    "text": option["text"],
                    "is_correct": option["is_correct"],
                }
            )

    if not option_rows:
        return

    stmt = insert(QuizQuestionOption).values(option_rows)

    await db_session.execute(stmt)


async def bulk_update_quiz_questions(
    update_quiz_questions_data: list[dict[str, Any]],
    db_session: AsyncSession,
) -> None:
    if not update_quiz_questions_data:
        return

    await db_session.execute(
        update(QuizQuestion),
        update_quiz_questions_data,
    )


async def bulk_delete_quiz_questions_by_ids(
    quiz_questions_ids: list[int],
    db_session: AsyncSession,
) -> None:
    if not quiz_questions_ids:
        return

    stmt = delete(QuizQuestion).where(QuizQuestion.id.in_(quiz_questions_ids))

    await db_session.execute(stmt)


async def bulk_create_quiz_question_options(
    quiz_question_id: int,
    options: list[dict[str, Any]],
    db_session: AsyncSession,
) -> None:
    if not options:
        return

    option_rows = [
        {
            "quiz_question_id": quiz_question_id,
            "text": option["text"],
            "is_correct": option["is_correct"],
        }
        for option in options
    ]

    if not option_rows:
        return

    stmt = insert(QuizQuestionOption).values(option_rows)

    await db_session.execute(stmt)


async def bulk_update_quiz_question_options(
    update_quiz_question_options_data: list[dict[str, Any]],
    db_session: AsyncSession,
) -> None:
    if not update_quiz_question_options_data:
        return

    await db_session.execute(
        update(QuizQuestionOption),
        update_quiz_question_options_data,
    )


async def bulk_delete_quiz_question_options_by_ids(
    quiz_question_option_ids: list[int],
    db_session: AsyncSession,
) -> None:
    if not quiz_question_option_ids:
        return

    stmt = delete(QuizQuestionOption).where(
        QuizQuestionOption.id.in_(quiz_question_option_ids)
    )

    await db_session.execute(stmt)
