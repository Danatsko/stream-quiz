from typing import Any

import resend

from app.core.config import settings

resend.api_key = settings.resend.api_key


async def send_email(
    to: list[str] | str,
    subject: str,
    html_content: str,
) -> dict[str, Any]:
    recipient = [to] if isinstance(to, str) else to
    params = {
        "from": settings.resend.from_email,
        "to": recipient,
        "subject": subject,
        "html": html_content,
    }
    response = await resend.Emails.send_async(params)

    return response
