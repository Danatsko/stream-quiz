from uuid import UUID
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.quizzes.db_crud import (
    create_quiz as db_crud_create_quiz,
    get_available_quizzes_total_count,
    get_available_quizzes_list,
    get_available_quiz_with_relations_by_uuid,
    get_available_quiz_by_uuid as db_crud_get_available_quiz_by_uuid,
    get_available_quiz_uuids_by_ids as db_crud_get_available_quiz_uuids_by_ids,
    get_quiz_with_relations_by_uuid,
    update_quiz_by_uuid,
    delete_quiz_by_uuid,
    bulk_create_quiz_questions,
    bulk_update_quiz_questions,
    bulk_delete_quiz_questions_by_ids,
    bulk_create_quiz_question_options,
    bulk_update_quiz_question_options,
    bulk_delete_quiz_question_options_by_ids,
)
from app.quizzes.models import Quiz
from app.users.service import get_user_by_uuid, get_user_uuids_by_ids, get_user_by_id


async def get_available_quiz_by_uuid(
    uuid: UUID,
    user_id: int,
    db_session: AsyncSession,
) -> Quiz | None:
    quiz_db = await db_crud_get_available_quiz_by_uuid(
        uuid=uuid,
        user_id=user_id,
        db_session=db_session,
    )

    return quiz_db


async def get_available_quiz_uuids_by_ids(
    ids: set[int],
    user_id: int,
    db_session: AsyncSession,
) -> dict[int, UUID]:
    uuids_mapping = await db_crud_get_available_quiz_uuids_by_ids(
        ids=ids,
        user_id=user_id,
        db_session=db_session,
    )

    return uuids_mapping


async def create_quiz(
    title: str,
    description: str,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    quiz_db = await db_crud_create_quiz(
        title=title,
        description=description,
        creator_id=user_db.id,
        db_session=db_session,
    )
    result = {"uuid": quiz_db.uuid}

    return result


async def get_quizzes(
    page: int,
    size: int,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    offset = (page - 1) * size
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    total_quizzes_db = await get_available_quizzes_total_count(
        user_id=user_db.id,
        db_session=db_session,
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
        db_session=db_session,
    )
    creator_ids = {quiz_db.creator_id for quiz_db, _ in quizzes_db}
    creators_mapping = await get_user_uuids_by_ids(
        ids=creator_ids,
        db_session=db_session,
    )
    total_pages = (total_quizzes_db + size - 1) // size
    quizzes = []

    for quiz_db, total_questions in quizzes_db:
        creator_uuid_mapped = creators_mapping.get(quiz_db.creator_id)

        quizzes.append(
            {
                "uuid": quiz_db.uuid,
                "title": quiz_db.title,
                "description": quiz_db.description,
                "is_public": quiz_db.is_public,
                "creator_uuid": creator_uuid_mapped,
                "total_questions": total_questions,
                "created_at": quiz_db.created_at,
                "updated_at": quiz_db.updated_at,
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
    quiz_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    quiz_db = await get_available_quiz_with_relations_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        db_session=db_session,
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
            db_session=db_session,
        )

    questions_data = []

    for question_db in quiz_db.questions:
        options_data = []

        for option_db in question_db.options:
            options_data.append(
                {
                    "uuid": option_db.uuid,
                    "text": option_db.text,
                    "is_correct": option_db.is_correct if is_owner else None,
                }
            )

        questions_data.append(
            {
                "uuid": question_db.uuid,
                "text": question_db.text,
                "is_multiple_answers": question_db.is_multiple_answers,
                "options": options_data,
            }
        )

    total_questions = len(questions_data)

    result = {
        "uuid": quiz_db.uuid,
        "creator_uuid": creator_db.uuid if creator_db else None,
        "title": quiz_db.title,
        "description": quiz_db.description,
        "is_public": quiz_db.is_public,
        "questions": questions_data,
        "total_questions": total_questions,
        "created_at": quiz_db.created_at,
        "updated_at": quiz_db.updated_at,
    }

    return result


async def update_quiz(
    quiz_uuid: UUID,
    user_uuid: UUID,
    update_quiz_data: dict[str, Any],
    db_session: AsyncSession,
) -> None:
    if not update_quiz_data:
        return

    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    is_updated = await update_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        update_quiz_data=update_quiz_data,
        db_session=db_session,
    )

    if not is_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to update it",
        )


async def full_update_quiz(
    quiz_uuid: UUID,
    user_uuid: UUID,
    full_update_quiz_data: dict[str, Any],
    db_session: AsyncSession,
) -> None:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    quiz_db = await get_quiz_with_relations_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if quiz_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to update it",
        )

    existing_questions_db_by_uuid = {
        question_db.uuid: question_db for question_db in quiz_db.questions
    }
    incoming_question_uuids = set()

    for question in full_update_quiz_data["questions"]:
        if question["uuid"] is None:
            continue

        if question["uuid"] not in existing_questions_db_by_uuid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Quiz question {question['uuid']} does not belong to this quiz",
            )

        incoming_question_uuids.add(question["uuid"])

        existing_options_db_by_uuid = {
            option_db.uuid: option_db
            for option_db in existing_questions_db_by_uuid[question["uuid"]].options
        }

        for option in question["options"]:
            if option["uuid"] is not None:
                if option["uuid"] not in existing_options_db_by_uuid:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=(
                            f"Quiz question option {option['uuid']} does not belong to quiz question {question['uuid']}"
                        ),
                    )

    update_quiz_data = {}

    if quiz_db.title != full_update_quiz_data["title"]:
        update_quiz_data["title"] = full_update_quiz_data["title"]
    if quiz_db.description != full_update_quiz_data["description"]:
        update_quiz_data["description"] = full_update_quiz_data["description"]
    if quiz_db.is_public != full_update_quiz_data["is_public"]:
        update_quiz_data["is_public"] = full_update_quiz_data["is_public"]

    questions_to_create = [
        {
            "text": question["text"],
            "is_multiple_answers": question["is_multiple_answers"],
            "options": [
                {"text": option["text"], "is_correct": option["is_correct"]}
                for option in question["options"]
            ],
        }
        for question in full_update_quiz_data["questions"]
        if question["uuid"] is None
    ]
    questions_to_update = []

    for question in full_update_quiz_data["questions"]:
        if question["uuid"] is None:
            continue

        update_question_data = {}
        question_db = existing_questions_db_by_uuid[question["uuid"]]

        if question_db.text != question["text"]:
            update_question_data["text"] = question["text"]
        if question_db.is_multiple_answers != question["is_multiple_answers"]:
            update_question_data["is_multiple_answers"] = question[
                "is_multiple_answers"
            ]

        if update_question_data:
            update_question_data["id"] = question_db.id

            questions_to_update.append(update_question_data)

    questions_to_delete_ids = [
        question_db.id
        for question_db_uuid, question_db in existing_questions_db_by_uuid.items()
        if question_db_uuid not in incoming_question_uuids
    ]
    options_to_create_by_question = {}
    options_to_update = []
    options_to_delete_ids = []

    for question in full_update_quiz_data["questions"]:
        if question["uuid"] is None:
            continue

        question_db = existing_questions_db_by_uuid[question["uuid"]]
        existing_options_db_by_uuid = {
            option_db.uuid: option_db for option_db in question_db.options
        }
        incoming_option_uuids = {
            option["uuid"]
            for option in question["options"]
            if option["uuid"] is not None
        }
        options_to_create = [
            {"text": option["text"], "is_correct": option["is_correct"]}
            for option in question["options"]
            if option["uuid"] is None
        ]

        if options_to_create:
            options_to_create_by_question[question_db.id] = options_to_create

        for option in question["options"]:
            if option["uuid"] is None:
                continue

            update_option_data = {}
            option_db = existing_options_db_by_uuid[option["uuid"]]

            if option_db.text != option["text"]:
                update_option_data["text"] = option["text"]
            if option_db.is_correct != option["is_correct"]:
                update_option_data["is_correct"] = option["is_correct"]

            if update_option_data:
                update_option_data["id"] = option_db.id

                options_to_update.append(update_option_data)

        options_to_delete_ids.extend(
            option_db.id
            for option_db_uuid, option_db in existing_options_db_by_uuid.items()
            if option_db_uuid not in incoming_option_uuids
        )

    if update_quiz_data:
        await update_quiz_by_uuid(
            uuid=quiz_uuid,
            user_id=user_db.id,
            update_quiz_data=update_quiz_data,
            db_session=db_session,
        )
    if questions_to_create:
        await bulk_create_quiz_questions(
            quiz_id=quiz_db.id,
            create_quiz_questions_data=questions_to_create,
            db_session=db_session,
        )
    if questions_to_update:
        await bulk_update_quiz_questions(
            update_quiz_questions_data=questions_to_update,
            db_session=db_session,
        )
    if questions_to_delete_ids:
        await bulk_delete_quiz_questions_by_ids(
            quiz_questions_ids=questions_to_delete_ids,
            db_session=db_session,
        )
    if options_to_create_by_question:
        for question_id, options in options_to_create_by_question.items():
            await bulk_create_quiz_question_options(
                quiz_question_id=question_id,
                options=options,
                db_session=db_session,
            )
    if options_to_update:
        await bulk_update_quiz_question_options(
            update_quiz_question_options_data=options_to_update,
            db_session=db_session,
        )
    if options_to_delete_ids:
        await bulk_delete_quiz_question_options_by_ids(
            quiz_question_option_ids=options_to_delete_ids,
            db_session=db_session,
        )


async def delete_quiz(
    quiz_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> None:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    is_deleted = await delete_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found, or you do not have permission to delete it",
        )
