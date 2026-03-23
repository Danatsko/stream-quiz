from uuid import UUID
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.quizzes.service import (
    get_available_quiz_by_uuid,
    get_available_quiz_uuids_by_ids,
    get_available_quiz_by_id,
)
from app.rooms.db_crud import (
    create_room as db_crud_create_room,
    get_rooms_total_count,
    get_rooms_list,
    update_room_by_uuid,
    soft_delete_room_by_uuid,
    get_room_by_uuid,
)
from app.sessions.models import SessionStatus
from app.sessions.service import (
    create_session as session_service_create_session,
    update_session_by_uuid,
    soft_delete_session_by_uuid,
    get_sessions_total_count,
    get_sessions_list,
    get_session_with_relations_by_uuid,
)
from app.users.service import get_user_by_uuid, get_user_uuids_by_ids


async def create_room(
    title: str,
    description: str,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await db_crud_create_room(
        title=title,
        description=description,
        creator_id=user_db.id,
        db_session=db_session,
    )
    result = {"uuid": room_db.uuid}

    return result


async def get_rooms(
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
    total_rooms_db = await get_rooms_total_count(
        user_id=user_db.id,
        db_session=db_session,
    )

    if total_rooms_db == 0:
        result = {
            "rooms": [],
            "total_rooms": total_rooms_db,
            "page": page,
            "size": size,
            "total_pages": 0,
        }

        return result

    rooms_db = await get_rooms_list(
        user_id=user_db.id,
        limit=size,
        offset=offset,
        db_session=db_session,
    )
    total_pages = (total_rooms_db + size - 1) // size
    rooms = []

    for room_db in rooms_db:
        rooms.append(
            {
                "uuid": room_db.uuid,
                "title": room_db.title,
                "description": room_db.description,
                "creator_uuid": user_db.uuid,
                "created_at": room_db.created_at,
                "updated_at": room_db.updated_at,
            }
        )

    result = {
        "rooms": rooms,
        "total_rooms": total_rooms_db,
        "page": page,
        "size": size,
        "total_pages": total_pages,
    }

    return result


async def get_room(
    room_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    result = {
        "creator_uuid": user_db.uuid,
        "uuid": room_db.uuid,
        "title": room_db.title,
        "description": room_db.description,
        "created_at": room_db.created_at,
        "updated_at": room_db.updated_at,
    }

    return result


async def update_room(
    room_uuid: UUID,
    user_uuid: UUID,
    update_room_data: dict[str, Any],
    db_session: AsyncSession,
) -> None:
    if not update_room_data:
        return

    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    is_updated = await update_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        update_room_data=update_room_data,
        db_session=db_session,
    )

    if not is_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )


async def delete_room(
    room_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> None:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    is_deleted = await soft_delete_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )


async def create_session(
    title: str,
    description: str,
    time_seconds: int,
    quiz_uuid: UUID,
    room_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    quiz_db = await get_available_quiz_by_uuid(
        uuid=quiz_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if quiz_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    session_db = await session_service_create_session(
        title=title,
        description=description,
        time_seconds=time_seconds,
        room_id=room_db.id,
        quiz_id=quiz_db.id,
        db_session=db_session,
    )

    result = {
        "uuid": session_db.uuid,
    }

    return result


async def get_sessions(
    page: int,
    size: int,
    room_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    offset = (page - 1) * size
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    total_sessions_db = await get_sessions_total_count(
        room_id=room_db.id,
        db_session=db_session,
    )

    if total_sessions_db == 0:
        result = {
            "sessions": [],
            "total_sessions": total_sessions_db,
            "page": page,
            "size": size,
            "total_pages": 0,
        }

        return result

    sessions_db = await get_sessions_list(
        room_id=room_db.id,
        limit=size,
        offset=offset,
        db_session=db_session,
    )
    quizzes_ids = {session_db.quiz_id for session_db in sessions_db}
    quizzes_mapping = await get_available_quiz_uuids_by_ids(
        ids=quizzes_ids,
        user_id=user_db.id,
        db_session=db_session,
    )
    total_pages = (total_sessions_db + size - 1) // size
    sessions = []

    for session_db in sessions_db:
        quiz_uuid_mapped = quizzes_mapping.get(session_db.quiz_id)

        sessions.append(
            {
                "uuid": session_db.uuid,
                "room_uuid": room_db.uuid,
                "quiz_uuid": quiz_uuid_mapped,
                "title": session_db.title,
                "description": session_db.description,
                "time_seconds": session_db.time_seconds,
                "status": session_db.status,
                "created_at": session_db.created_at,
                "updated_at": session_db.updated_at,
            }
        )

    result = {
        "sessions": sessions,
        "total_sessions": total_sessions_db,
        "page": page,
        "size": size,
        "total_pages": total_pages,
    }

    return result


async def get_session(
    room_uuid: UUID,
    session_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    session_db = await get_session_with_relations_by_uuid(
        uuid=session_uuid,
        room_id=room_db.id,
        db_session=db_session,
    )

    if session_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    quiz_db = await get_available_quiz_by_id(
        id=session_db.quiz_id,
        user_id=user_db.id,
        db_session=db_session,
    )
    quiz_uuid = quiz_db.uuid if quiz_db else None

    if session_db.status == SessionStatus.waiting:
        result = {
            "uuid": session_db.uuid,
            "room_uuid": room_db.uuid,
            "quiz_uuid": quiz_uuid,
            "title": session_db.title,
            "description": session_db.description,
            "time_seconds": session_db.time_seconds,
            "status": session_db.status,
            "members": [],
            "total_members": 0,
            "questions": [],
            "total_questions": 0,
            "total_score": 0,
            "created_at": session_db.created_at,
            "updated_at": session_db.updated_at,
        }

        return result

    questions = []
    scoring_map = {}
    option_id_to_uuid_map = {}

    for question_db in session_db.questions:
        options_data = []
        correct_options = set()
        wrong_options = set()

        for option_db in question_db.options:
            option_id_to_uuid_map[option_db.id] = option_db.uuid
            options_data.append(
                {
                    "uuid": option_db.uuid,
                    "text": option_db.text,
                    "is_correct": option_db.is_correct,
                }
            )

            if option_db.is_correct:
                correct_options.add(option_db.id)
            else:
                wrong_options.add(option_db.id)

        scoring_map[question_db.id] = {
            "question_uuid": question_db.uuid,
            "correct_opts": correct_options,
            "wrong_opts": wrong_options,
        }

        questions.append(
            {
                "uuid": question_db.uuid,
                "text": question_db.text,
                "is_multiple_answers": question_db.is_multiple_answers,
                "options": options_data,
            }
        )

    total_questions = len(questions)
    total_score = float(total_questions)

    if session_db.status == SessionStatus.active:
        result = {
            "uuid": session_db.uuid,
            "room_uuid": room_db.uuid,
            "quiz_uuid": quiz_uuid,
            "title": session_db.title,
            "description": session_db.description,
            "time_seconds": session_db.time_seconds,
            "status": session_db.status,
            "members": [],
            "total_members": 0,
            "questions": questions,
            "total_questions": total_questions,
            "total_score": total_score,
            "created_at": session_db.created_at,
            "updated_at": session_db.updated_at,
        }

        return result

    members = []
    member_user_ids = {member_db.user_id for member_db in session_db.members}
    user_uuids_mapping = {}

    if member_user_ids:
        user_uuids_mapping = await get_user_uuids_by_ids(
            ids=member_user_ids, db_session=db_session
        )

    for member_db in session_db.members:
        member_answers_data = []
        member_total_score = 0.0
        member_total_answers = 0
        grouped_answers = {}

        for answer_db in member_db.answers:
            question_db_id = answer_db.session_question_id

            if question_db_id not in grouped_answers:
                grouped_answers[question_db_id] = []

            grouped_answers[question_db_id].append(answer_db.session_question_option_id)

        for question_id, question_scoring in scoring_map.items():
            selected_opt_ids = set(grouped_answers.get(question_id, []))

            if not selected_opt_ids:
                member_answers_data.append(
                    {
                        "question_uuid": question_scoring["question_uuid"],
                        "selected_option_uuids": [],
                        "score": 0.00,
                    }
                )
                continue

            member_total_answers += 1

            correct_selected = selected_opt_ids.intersection(
                question_scoring["correct_opts"]
            )
            wrong_selected = selected_opt_ids.intersection(
                question_scoring["wrong_opts"]
            )
            total_correct = len(question_scoring["correct_opts"])
            total_wrong = len(question_scoring["wrong_opts"])
            correct_ratio = (
                len(correct_selected) / total_correct if total_correct > 0 else 0.0
            )
            wrong_ratio = len(wrong_selected) / total_wrong if total_wrong > 0 else 0.0
            question_score = correct_ratio - wrong_ratio

            if question_score < 0:
                question_score = 0.0

            member_total_score += question_score

            selected_uuids = [
                option_id_to_uuid_map[option_id]
                for option_id in selected_opt_ids
                if option_id in option_id_to_uuid_map
            ]

            member_answers_data.append(
                {
                    "question_uuid": question_scoring["question_uuid"],
                    "selected_option_uuids": selected_uuids,
                    "score": round(question_score, 2),
                }
            )

        members.append(
            {
                "user_uuid": user_uuids_mapping.get(member_db.user_id),
                "answers": member_answers_data,
                "total_answers": member_total_answers,
                "score": round(member_total_score, 2),
            }
        )

    total_members = len(members)
    result = {
        "uuid": session_db.uuid,
        "room_uuid": room_db.uuid,
        "quiz_uuid": quiz_uuid,
        "title": session_db.title,
        "description": session_db.description,
        "time_seconds": session_db.time_seconds,
        "status": session_db.status,
        "members": members,
        "total_members": total_members,
        "questions": questions,
        "total_questions": total_questions,
        "total_score": total_score,
        "created_at": session_db.created_at,
        "updated_at": session_db.updated_at,
    }

    return result


async def update_session(
    room_uuid: UUID,
    session_uuid: UUID,
    user_uuid: UUID,
    update_session_data: dict[str, Any],
    db_session: AsyncSession,
) -> None:
    if not update_session_data:
        return

    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    if "quiz_uuid" in update_session_data:
        quiz_uuid = update_session_data.pop("quiz_uuid")
        quiz_db = await get_available_quiz_by_uuid(
            uuid=quiz_uuid,
            user_id=user_db.id,
            db_session=db_session,
        )

        if quiz_db is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found",
            )

        update_session_data["quiz_id"] = quiz_db.id

    session_db = await get_session_with_relations_by_uuid(
        uuid=session_uuid,
        room_id=room_db.id,
        db_session=db_session,
    )

    if session_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session_db.status != SessionStatus.waiting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a session that is already active or completed",
        )

    is_updated = await update_session_by_uuid(
        uuid=session_uuid,
        room_id=room_db.id,
        update_session_data=update_session_data,
        db_session=db_session,
    )

    if not is_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )


async def delete_session(
    room_uuid: UUID,
    session_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> None:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    session_db = await get_session_with_relations_by_uuid(
        uuid=session_uuid,
        room_id=room_db.id,
        db_session=db_session,
    )

    if session_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session_db.status != SessionStatus.waiting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a session that is already active or completed",
        )

    is_deleted = await soft_delete_session_by_uuid(
        uuid=session_uuid,
        room_id=room_db.id,
        db_session=db_session,
    )

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
