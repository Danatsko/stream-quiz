from typing import Any

from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.quizzes.models import Quiz, QuizQuestion, QuizQuestionOption


async def create_quiz(
    quiz_data: dict[str, Any], creator_id: int, session: AsyncSession
) -> Quiz:
    quiz = Quiz(
        creator_id=creator_id,
        title=quiz_data["title"],
        description=quiz_data["description"],
        is_public=quiz_data["is_public"],
    )

    for question_data in quiz_data["questions"]:
        question = QuizQuestion(
            text=question_data["text"],
            is_multiple_answers=question_data["is_multiple_answers"],
        )

        for option_data in question_data["options"]:
            option = QuizQuestionOption(
                text=option_data["text"],
                is_correct=option_data["is_correct"],
            )

            question.options.append(option)

        quiz.questions.append(question)

    session.add(quiz)
    await session.flush()
    await session.refresh(
        instance=quiz,
        attribute_names=[
            "id",
            "uuid",
        ],
    )

    return quiz


async def get_quizzes_total_count(user_id: int, session: AsyncSession) -> int:
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


async def get_quizzes(
    user_id: int, limit: int, offset: int, session: AsyncSession
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
