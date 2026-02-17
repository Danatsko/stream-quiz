from typing import Any

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
