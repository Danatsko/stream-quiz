import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.quizzes.db_crud import (
    create_quiz as db_crud_create_quiz,
    get_quizzes_total_count,
    get_available_quizzes_list,
    get_available_quiz_with_relations_by_uuid,
    get_quiz_by_uuid,
    update_quiz_by_uuid,
    delete_quiz_by_uuid,
    create_quiz_question as db_crud_create_quiz_question,
    get_quiz_question_with_relations_by_uuid,
    update_quiz_question_by_uuid,
    delete_quiz_question_by_uuid,
    create_quiz_question_option as db_crud_create_quiz_question_option,
    update_quiz_question_option_by_uuid,
)
from app.users.service import get_user_by_uuid, get_user_uuids_by_ids, get_user_by_id


async def create_quiz(
    title: str,
    description: str,
    user_uuid: uuid.UUID,
    session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    quiz_db = await db_crud_create_quiz(
        title=title,
        description=description,
        creator_id=user_db.id,
        session=session,
    )
    result = {"uuid": quiz_db.uuid}

    return result


async def get_quizzes(
    page: int,
    size: int,
    user_uuid: uuid.UUID,
    session: AsyncSession,
) -> dict[str, Any]:
    offset = (page - 1) * size
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    total_quizzes_db = await get_quizzes_total_count(
        user_id=user_db.id,
        session=session,
    )

    if total_quizzes_db == 0:
        result = {
            "quizzes": [],
            "total_quizzes": total_quizzes_db,
            "page": page,
            "size": size,
            "total_pages": 0,
        }

        return result

    quizzes_db = await get_available_quizzes_list(
        user_id=user_db.id,
        limit=size,
        offset=offset,
        session=session,
    )
    creator_ids = {quiz.creator_id for quiz, _ in quizzes_db}
    creators_mapping = await get_user_uuids_by_ids(
        ids=creator_ids,
        session=session,
    )

    total_pages = (total_quizzes_db + size - 1) // size
    quizzes = []

    for quiz, total_questions in quizzes_db:
        creator_uuid_mapped = creators_mapping.get(quiz.creator_id)

        quizzes.append(
            {
                "uuid": quiz.uuid,
                "title": quiz.title,
                "description": quiz.description,
                "is_public": quiz.is_public,
                "creator_uuid": creator_uuid_mapped,
                "total_questions": total_questions,
            }
        )

    result = {
        "quizzes": quizzes,
        "total_quizzes": total_quizzes_db,
        "page": page,
        "size": size,
        "total_pages": total_pages,
    }

    return result


async def get_quiz(
    quiz_uuid: uuid.UUID,
    user_uuid: uuid.UUID,
    session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    quiz_db = await get_available_quiz_with_relations_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        session=session,
    )

    if quiz_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    is_owner = quiz_db.creator_id == user_db.id

    if is_owner:
        creator_db = user_db
    else:
        creator_db = await get_user_by_id(
            id=quiz_db.creator_id,
            session=session,
        )

    questions_data = []

    for question in quiz_db.questions:
        options_data = []

        for option in question.options:
            options_data.append(
                {
                    "uuid": option.uuid,
                    "text": option.text,
                    "is_correct": option.is_correct if is_owner else None,
                }
            )

        questions_data.append(
            {
                "uuid": question.uuid,
                "text": question.text,
                "is_multiple_answers": question.is_multiple_answers,
                "options": options_data,
            }
        )

    result = {
        "uuid": quiz_db.uuid,
        "creator_uuid": creator_db.uuid if creator_db else None,
        "title": quiz_db.title,
        "description": quiz_db.description,
        "is_public": quiz_db.is_public,
        "questions": questions_data,
    }

    return result


async def update_quiz(
    quiz_uuid: uuid.UUID,
    user_uuid: uuid.UUID,
    update_quiz_data: dict[str, Any],
    session: AsyncSession,
) -> None:
    if not update_quiz_data:
        return

    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    is_updated = await update_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        update_quiz_data=update_quiz_data,
        session=session,
    )

    if not is_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to update it",
        )


async def delete_quiz(
    quiz_uuid: uuid.UUID,
    user_uuid: uuid.UUID,
    session: AsyncSession,
) -> None:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    is_deleted = await delete_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        session=session,
    )

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to delete it",
        )


async def create_quiz_question(
    quiz_uuid: uuid.UUID,
    user_uuid: uuid.UUID,
    text: str,
    is_multiple_answers: bool,
    options: list[dict[str, Any]],
    session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    quiz_db = await get_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        session=session,
    )

    if quiz_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to update it",
        )

    quiz_question_db = await db_crud_create_quiz_question(
        quiz_id=quiz_db.id,
        text=text,
        is_multiple_answers=is_multiple_answers,
        options=options,
        session=session,
    )
    result = {"uuid": quiz_question_db.uuid}

    return result


async def update_quiz_question(
    quiz_uuid: uuid.UUID,
    quiz_question_uuid: uuid.UUID,
    user_uuid: uuid.UUID,
    update_quiz_question_data: dict[str, Any],
    session: AsyncSession,
) -> None:
    if not update_quiz_question_data:
        return

    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    quiz_db = await get_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        session=session,
    )

    if quiz_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to update it",
        )

    quiz_question_db = await get_quiz_question_with_relations_by_uuid(
        uuid=quiz_question_uuid,
        quiz_id=quiz_db.id,
        session=session,
    )

    if quiz_question_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz question not found",
        )

    new_is_multiple_answers = update_quiz_question_data.get("is_multiple_answers")

    if new_is_multiple_answers is False:
        correct_count = sum(
            1 for option in quiz_question_db.options if option.is_correct
        )

        if correct_count > 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot change to single-choice question because multiple correct options exist",
            )

    is_updated = await update_quiz_question_by_uuid(
        uuid=quiz_question_uuid,
        quiz_id=quiz_db.id,
        update_quiz_question_data=update_quiz_question_data,
        session=session,
    )

    if not is_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz question not found",
        )


async def delete_quiz_question(
    quiz_uuid: uuid.UUID,
    quiz_question_uuid: uuid.UUID,
    user_uuid: uuid.UUID,
    session: AsyncSession,
) -> None:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    quiz_db = await get_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        session=session,
    )

    if quiz_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to delete it",
        )

    is_deleted = await delete_quiz_question_by_uuid(
        uuid=quiz_question_uuid,
        quiz_id=quiz_db.id,
        session=session,
    )

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz question not found",
        )


async def create_quiz_question_option(
    quiz_uuid: uuid.UUID,
    quiz_question_uuid: uuid.UUID,
    user_uuid: uuid.UUID,
    text: str,
    is_correct: bool,
    session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    quiz_db = await get_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        session=session,
    )

    if quiz_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to update it",
        )

    quiz_question_db = await get_quiz_question_with_relations_by_uuid(
        uuid=quiz_question_uuid,
        quiz_id=quiz_db.id,
        session=session,
    )

    if quiz_question_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz question not found",
        )

    if is_correct and not quiz_question_db.is_multiple_answers:
        correct_count = sum(
            1 for option in quiz_question_db.options if option.is_correct
        )

        if correct_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Single-choice questions must have exactly one correct option",
            )

    quiz_question_option_db = await db_crud_create_quiz_question_option(
        quiz_question_id=quiz_question_db.id,
        text=text,
        is_correct=is_correct,
        session=session,
    )

    result = {"uuid": quiz_question_option_db.uuid}

    return result


async def update_quiz_question_option(
    quiz_uuid: uuid.UUID,
    quiz_question_uuid: uuid.UUID,
    quiz_question_option_uuid: uuid.UUID,
    user_uuid: uuid.UUID,
    update_quiz_question_option_data: dict[str, Any],
    session: AsyncSession,
) -> None:
    if not update_quiz_question_option_data:
        return

    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    quiz_db = await get_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        session=session,
    )

    if quiz_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to update it",
        )

    quiz_question_db = await get_quiz_question_with_relations_by_uuid(
        uuid=quiz_question_uuid,
        quiz_id=quiz_db.id,
        session=session,
    )

    if quiz_question_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz question not found",
        )

    quiz_question_option_db = next(
        (
            option
            for option in quiz_question_db.options
            if option.uuid == quiz_question_option_uuid
        ),
        None,
    )

    if quiz_question_option_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz question option not found",
        )

    if "is_correct" in update_quiz_question_option_data:
        new_is_correct = update_quiz_question_option_data.get("is_correct")

        if not quiz_question_db.is_multiple_answers:
            if new_is_correct is True:
                other_correct_exists = any(
                    option.is_correct
                    for option in quiz_question_db.options
                    if option.uuid != quiz_question_option_uuid
                )

                if other_correct_exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Single-choice questions must have exactly one correct option",
                    )

        if new_is_correct is False:
            if quiz_question_option_db.is_correct:
                correct_count = sum(
                    1 for option in quiz_question_db.options if option.is_correct
                )

                if correct_count <= 1:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Cannot unset the only correct option",
                    )

    is_updated = await update_quiz_question_option_by_uuid(
        uuid=quiz_question_option_uuid,
        quiz_question_id=quiz_question_db.id,
        update_quiz_question_option_data=update_quiz_question_option_data,
        session=session,
    )

    if not is_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz question option not found",
        )
