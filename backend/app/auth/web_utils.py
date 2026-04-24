from fastapi import Response

from app.core.config import settings


async def set_auth_cookies(
    response: Response,
    access_token: str | None = None,
    refresh_token: str | None = None,
) -> None:
    if access_token is not None:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=(not settings.app.debug),
            samesite="lax",
            max_age=settings.auth.access_token_expire_seconds,
        )

    if refresh_token is not None:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=(not settings.app.debug),
            samesite="lax",
            max_age=settings.auth.refresh_token_expire_seconds,
            path=settings.auth.refresh_token_cookie_path,
        )


async def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=(not settings.app.debug),
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=(not settings.app.debug),
        samesite="lax",
        path=settings.auth.refresh_token_cookie_path,
    )
