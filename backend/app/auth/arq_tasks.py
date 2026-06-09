from typing import Any
from app.auth.emails import process_verification_email


async def send_verification_email(
    ctx: dict[str, Any],
    email: str,
    token: str,
) -> None:
    await process_verification_email(
        email=email,
        token=token,
    )
