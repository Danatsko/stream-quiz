from uuid import UUID
from typing import Any

from sqlalchemy import or_, select, func, update, delete, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.quizzes.models import Quiz, QuizQuestion, QuizQuestionOption


async def create_quiz(
    title: str,
    description: str,
    creator_id: int,
    session: AsyncSession,
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
    result = await session.scalar(stmt)

    return result


async def get_quizzes_total_count(
    user_id: int,
    session: AsyncSession,
) -> int:
    stmt = (
        select(func.count())
        .select_from(Quiz)
        .where(
            or_(
                Quiz.is_public.is_(True),
                Quiz.creator_id == user_id,
            )
        )
    )
    result = await session.scalar(stmt)

    return result or 0


async def get_available_quizzes_list(
    user_id: int,
    limit: int,
    offset: int,
    session: AsyncSession,
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
            )
        )
        .group_by(Quiz.id)
        .order_by(Quiz.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    result = result.all()

    return result


async def get_available_quiz_with_relations_by_uuid(
    uuid: UUID,
    user_id: int,
    session: AsyncSession,
) -> Quiz | None:
    stmt = (
        select(Quiz)
        .where(
            Quiz.uuid == uuid,
            or_(
                Quiz.is_public.is_(True),
                Quiz.creator_id == user_id,
            ),
        )
        .options(selectinload(Quiz.questions).selectinload(QuizQuestion.options))
    )
    result = await session.scalar(stmt)

    return result


async def get_quiz_with_relations_by_uuid(
    uuid: UUID,
    user_id: int,
    session: AsyncSession,
) -> Quiz | None:
    stmt = (
        select(Quiz)
        .where(
            Quiz.uuid == uuid,
            Quiz.creator_id == user_id,
        )
        .options(selectinload(Quiz.questions).selectinload(QuizQuestion.options))
    )
    result = await session.scalar(stmt)

    return result


async def update_quiz_by_uuid(
    uuid: UUID,
    user_id: int,
    update_quiz_data: dict[str, Any],
    session: AsyncSession,
) -> bool:
    stmt = (
        update(Quiz)
        .where(
            Quiz.uuid == uuid,
            Quiz.creator_id == user_id,
        )
        .values(**update_quiz_data)
    )
    result = await session.execute(stmt)

    return result.rowcount == 1


async def delete_quiz_by_uuid(
    uuid: UUID,
    user_id: int,
    session: AsyncSession,
) -> bool:
    stmt = delete(Quiz).where(
        Quiz.uuid == uuid,
        Quiz.creator_id == user_id,
    )
    result = await session.execute(stmt)

    return result.rowcount == 1


async def bulk_create_quiz_questions(
    quiz_id: int,
    create_quiz_questions_data: list[dict[str, Any]],
    session: AsyncSession,
) -> None:
    question_rows = [
        {
            "quiz_id": quiz_id,
            "text": question["text"],
            "is_multiple_answers": question["is_multiple_answers"],
        }
        for question in create_quiz_questions_data
    ]
    stmt = insert(QuizQuestion).values(question_rows).returning(QuizQuestion)
    created_questions = list(await session.scalars(stmt))
    option_rows = []

    for question_db, question_data in zip(
        created_questions, create_quiz_questions_data
    ):
        for option in question_data["options"]:
            option_rows.append(
                {
                    "quiz_question_id": question_db.id,
                    "text": option["text"],
                    "is_correct": option["is_correct"],
                }
            )

    stmt = insert(QuizQuestionOption).values(option_rows)

    await session.execute(stmt)


async def bulk_update_quiz_questions(
    update_quiz_questions_data: list[dict[str, Any]],
    session: AsyncSession,
) -> None:
    await session.execute(update(QuizQuestion), update_quiz_questions_data)


async def bulk_delete_quiz_questions_by_ids(
    quiz_questions_ids: list[int],
    session: AsyncSession,
) -> None:
    stmt = delete(QuizQuestion).where(QuizQuestion.id.in_(quiz_questions_ids))

    await session.execute(stmt)


async def bulk_create_quiz_question_options(
    quiz_question_id: int,
    options: list[dict[str, Any]],
    session: AsyncSession,
) -> None:
    option_rows = [
        {
            "quiz_question_id": quiz_question_id,
            "text": option["text"],
            "is_correct": option["is_correct"],
        }
        for option in options
    ]
    stmt = insert(QuizQuestionOption).values(option_rows)

    await session.execute(stmt)


async def bulk_update_quiz_question_options(
    update_quiz_question_options_data: list[dict[str, Any]],
    session: AsyncSession,
) -> None:
    await session.execute(update(QuizQuestionOption), update_quiz_question_options_data)


async def bulk_delete_quiz_question_options_by_ids(
    quiz_question_option_ids: list[int],
    session: AsyncSession,
) -> None:
    stmt = delete(QuizQuestionOption).where(
        QuizQuestionOption.id.in_(quiz_question_option_ids)
    )

    await session.execute(stmt)
