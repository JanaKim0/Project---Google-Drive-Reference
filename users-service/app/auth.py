import jwt
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db import revoked_tokens_collection, users_collection
from app.security import decode_access_token, is_password_expired

NOT_AUTHENTICATED_MESSAGE = "Niste prijavljeni ili je sesija istekla."

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=NOT_AUTHENTICATED_MESSAGE,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise _unauthorized()

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise _unauthorized()

    if revoked_tokens_collection.find_one({"jti": payload["jti"]}, {"_id": 1}):
        raise _unauthorized()

    try:
        user_id = ObjectId(payload["sub"])
    except (InvalidId, TypeError):
        raise _unauthorized()

    user = users_collection.find_one({"_id": user_id}, {"password_changed_at": 1})
    if not user:
        raise _unauthorized()

    password_changed_at = user.get("password_changed_at")
    if password_changed_at and payload["iat"] < password_changed_at.timestamp():
        raise _unauthorized()

    if is_password_expired(password_changed_at):
        raise _unauthorized()

    return payload