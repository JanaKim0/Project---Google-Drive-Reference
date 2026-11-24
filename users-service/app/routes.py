from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.config import VERIFICATION_TOKEN_EXPIRE_MINUTES
from app.db import users_collection
from app.schemas import RegisterRequest, UserResponse
from app.security import generate_token, hash_password, hash_token

router = APIRouter()

EMAIL_TAKEN_MESSAGE = "Imejl je već registrovan."


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
    }

    try:
        result = users_collection.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN_MESSAGE)

    return UserResponse(
        id=str(result.inserted_id),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
    )