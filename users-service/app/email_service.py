import smtplib
from email.message import EmailMessage

from app.config import FRONTEND_URL, SMTP_FROM, SMTP_HOST, SMTP_PORT


def send_verification_email(to_email: str, first_name: str, token: str) -> None:
    link = f"{FRONTEND_URL}/verify?token={token}"

    message = EmailMessage()
    message["Subject"] = "Potvrda registracije"
    message["From"] = SMTP_FROM
    message["To"] = to_email
    message.set_content(
        f"Zdravo {first_name},\n\n"
        f"Hvala na registraciji. Potvrdite svoj nalog klikom na link:\n{link}\n\n"
        "Link važi ograničeno vreme. Ako se niste registrovali, ignorišite ovu poruku."
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
        smtp.send_message(message)