import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db import revoked_tokens_collection
from app.security import decode_access_token

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

    return payload