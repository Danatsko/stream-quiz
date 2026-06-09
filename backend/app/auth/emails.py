from app.core.config import settings
from app.core.resend import send_email


async def process_verification_email(email: str, token: str) -> None:
    base_url = str(settings.app.frontend_url).rstrip("/")
    path = settings.auth.verification_path.lstrip("/")
    verification_link = f"{base_url}/{path}?token={token}"
    html_content = f"""
        <h1>Confirmation of registration</h1>
        <p>Click on the link below to verify your email:</p>
        <a href="{verification_link}">Confirm account</a>
    """

    await send_email(
        to=email,
        subject="Confirmation of registration",
        html_content=html_content,
    )
