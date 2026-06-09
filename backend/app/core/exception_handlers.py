from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    DomainException,
    NotFoundError,
    ConflictError,
    ValidationError,
    AuthError,
    UnprocessableEntityError,
)


async def not_found_handler(
    request: Request,
    exc: NotFoundError,
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def conflict_handler(
    request: Request,
    exc: ConflictError,
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def validation_handler(
    request: Request,
    exc: ValidationError,
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


async def unprocessable_entity_handler(
    request: Request,
    exc: UnprocessableEntityError,
):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def unauthorized_handler(
    request: Request,
    exc: AuthError,
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
    )


async def forbidden_handler(
    request: Request,
    exc: AuthError,
):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message},
    )


async def domain_fallback_handler(
    request: Request,
    exc: DomainException,
):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message},
    )
