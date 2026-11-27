import logging

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import USERS_SERVICE_TIMEOUT_SECONDS, USERS_SERVICE_URL

logger = logging.getLogger(__name__)

NOT_AUTHENTICATED_MESSAGE = "Niste prijavljeni ili je sesija istekla."
USERS_UNAVAILABLE_MESSAGE = "Servis za korisnike trenutno nije dostupan. Pokušajte kasnije."

bearer_scheme = HTTPBearer(auto_error=False)
users_client = httpx.Client(base_url=USERS_SERVICE_URL, timeout=USERS_SERVICE_TIMEOUT_SECONDS)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=NOT_AUTHENTICATED_MESSAGE,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise _unauthorized()

    try:
        response = users_client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {credentials.credentials}"},
        )
    except httpx.HTTPError:
        logger.warning("Users servis nije dostupan pri proveri tokena.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=USERS_UNAVAILABLE_MESSAGE)

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise _unauthorized()

    if response.status_code != status.HTTP_200_OK:
        logger.warning("Neočekivan odgovor Users servisa: %s", response.status_code)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=USERS_UNAVAILABLE_MESSAGE)

    user = response.json()
    return {"id": user["id"], "role": user["role"]}