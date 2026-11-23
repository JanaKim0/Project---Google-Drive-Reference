from datetime import datetime, timezone

from fastapi import APIRouter, status

from app.db import users_collection
from app.schemas import RegisterRequest, UserResponse
from app.security import hash_password

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    now = datetime.now(timezone.utc)

    user = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "role": "user",
        "is_verified": False,
        "created_at": now,
        "password_changed_at": now,
    }

    result = users_collection.insert_one(user)

    return UserResponse(
        id=str(result.inserted_id),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
    )