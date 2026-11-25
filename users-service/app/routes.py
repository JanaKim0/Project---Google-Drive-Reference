import logging
import smtplib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.config import DEFAULT_STORAGE_QUOTA_BYTES, VERIFICATION_TOKEN_EXPIRE_MINUTES
from app.db import users_collection
from app.email_service import send_verification_email
from app.schemas import MessageResponse, RegisterRequest, UserResponse, VerifyRequest
from app.security import generate_token, hash_password, hash_token

logger = logging.getLogger(__name__)

router = APIRouter()

EMAIL_TAKEN_MESSAGE = "Imejl je već registrovan."
INVALID_TOKEN_MESSAGE = "Link za potvrdu nije ispravan ili je već iskorišćen."
EXPIRED_TOKEN_MESSAGE = "Link za potvrdu je istekao."


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    if users_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN_MESSAGE)

    now = datetime.now(timezone.utc)
    verification_token = generate_token()

    user = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "role": "user",
        "is_verified": False,
        "created_at": now,
        "password_changed_at": now,
        "verification_token_hash": hash_token(verification_token),
        "verification_token_expires_at": now + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES),
        "storage_quota_bytes": DEFAULT_STORAGE_QUOTA_BYTES,
        "storage_used_bytes": 0,
    }

    try:
        result = users_collection.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN_MESSAGE)

    try:
        send_verification_email(data.email, data.first_name, verification_token)
    except (smtplib.SMTPException, OSError):
        logger.warning("Slanje imejla za potvrdu nije uspelo za korisnika %s", result.inserted_id)

    return UserResponse(
        id=str(result.inserted_id),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
    )


@router.post("/verify", response_model=MessageResponse)
def verify_account(data: VerifyRequest):
    user = users_collection.find_one({"verification_token_hash": hash_token(data.token)})
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_TOKEN_MESSAGE)

    if user["verification_token_expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EXPIRED_TOKEN_MESSAGE)

    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"is_verified": True},
            "$unset": {"verification_token_hash": "", "verification_token_expires_at": ""},
        },
    )

    return MessageResponse(message="Nalog je uspešno potvrđen.")