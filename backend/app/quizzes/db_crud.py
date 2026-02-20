import uuid
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
    uuid: uuid.UUID,
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


async def update_quiz_by_uuid(
    uuid: uuid.UUID,
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
    uuid: uuid.UUID,
    user_id: int,
    session: AsyncSession,
) -> bool:
    stmt = delete(Quiz).where(
        Quiz.uuid == uuid,
        Quiz.creator_id == user_id,
    )
    result = await session.execute(stmt)

    return result.rowcount == 1


async def create_quiz_question(
    quiz_id: int,
    text: str,
    is_multiple_answers: bool,
    options: list[dict[str, Any]],
    session: AsyncSession,
) -> QuizQuestion:
    stmt_question = (
        insert(QuizQuestion)
        .values(
            quiz_id=quiz_id,
            text=text,
            is_multiple_answers=is_multiple_answers,
        )
        .returning(QuizQuestion)
    )
    result_question = await session.scalar(stmt_question)

    for option in options:
        option.update({"quiz_question_id": result_question.id})

    stmt_options = insert(QuizQuestionOption).values(options)

    await session.execute(stmt_options)

    return result_question


async def get_quiz_question_with_relations_by_uuid(
    uuid: uuid.UUID,
    quiz_id: int,
    session: AsyncSession,
) -> QuizQuestion | None:
    stmt = (
        select(QuizQuestion)
        .where(
            QuizQuestion.uuid == uuid,
            QuizQuestion.quiz_id == quiz_id,
        )
        .options(selectinload(QuizQuestion.options))
    )
    result = await session.scalar(stmt)

    return result


async def update_quiz_question_by_uuid(
    uuid: uuid.UUID,
    quiz_id: int,
    update_quiz_question_data: dict[str, Any],
    session: AsyncSession,
) -> bool:
    stmt = (
        update(QuizQuestion)
        .where(
            QuizQuestion.uuid == uuid,
            QuizQuestion.quiz_id == quiz_id,
        )
        .values(**update_quiz_question_data)
    )
    result = await session.execute(stmt)

    return result.rowcount == 1


async def delete_quiz_question_by_uuid(
    uuid: uuid.UUID,
    quiz_id: int,
    session: AsyncSession,
) -> bool:
    stmt = delete(QuizQuestion).where(
        QuizQuestion.uuid == uuid,
        QuizQuestion.quiz_id == quiz_id,
    )
    result = await session.execute(stmt)

    return result.rowcount == 1
