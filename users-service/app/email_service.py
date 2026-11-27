import smtplib
from email.message import EmailMessage

from app.config import (
    FRONTEND_URL,
    OTP_EXPIRE_MINUTES,
    PASSWORD_RESET_EXPIRE_MINUTES,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PORT,
)


def _send_email(to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = to_email
    message.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
        smtp.send_message(message)


def send_verification_email(to_email: str, first_name: str, token: str) -> None:
    link = f"{FRONTEND_URL}/verify?token={token}"
    _send_email(
        to_email,
        "Potvrda registracije",
        f"Zdravo {first_name},\n\n"
        f"Hvala na registraciji. Potvrdite svoj nalog klikom na link:\n{link}\n\n"
        "Link važi ograničeno vreme. Ako se niste registrovali, ignorišite ovu poruku.",
    )


def send_otp_email(to_email: str, first_name: str, otp: str) -> None:
    _send_email(
        to_email,
        "Kod za prijavu",
        f"Zdravo {first_name},\n\n"
        f"Vaš jednokratni kod za prijavu je: {otp}\n\n"
        f"Kod važi {OTP_EXPIRE_MINUTES} minuta. Ako niste pokušali da se prijavite, "
        "promenite lozinku.",
    )


def send_password_reset_email(to_email: str, first_name: str, token: str) -> None:
    link = f"{FRONTEND_URL}/reset-password?token={token}"
    _send_email(
        to_email,
        "Resetovanje lozinke",
        f"Zdravo {first_name},\n\n"
        f"Primili smo zahtev za resetovanje lozinke. Novu lozinku možete postaviti klikom na link:\n{link}\n\n"
        f"Link važi {PASSWORD_RESET_EXPIRE_MINUTES} minuta i može se iskoristiti samo jednom. "
        "Ako niste zatražili resetovanje lozinke, ignorišite ovu poruku.",
    )