import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.quizzes.db_crud import (
    create_quiz as db_crud_create_quiz,
    get_quizzes_total_count,
    get_quizzes as db_crud_get_quizzes,
)
from app.users.service import get_user_by_uuid, get_user_uuids_by_ids


async def create_quiz(
    quiz_data: dict[str, Any], user_uuid: uuid.UUID, session: AsyncSession
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    quiz_db = await db_crud_create_quiz(
        quiz_data=quiz_data,
        creator_id=user_db.id,
        session=session,
    )
    result = {"uuid": quiz_db.uuid}

    return result


async def get_quizzes(
    page: int, size: int, user_uuid: uuid.UUID, session: AsyncSession
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

    quizzes_db = await db_crud_get_quizzes(
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
