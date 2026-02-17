import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.quizzes.db_crud import create_quiz as db_crud_create_quiz
from app.users.service import get_user_by_uuid


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
