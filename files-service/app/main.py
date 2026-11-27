from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import get_current_user
from app.config import FRONTEND_URL
from app.db import client, ensure_indexes
from app.routes import router

DEFAULT_MESSAGES = {
    "missing": "Polje je obavezno.",
    "extra_forbidden": "Polje nije dozvoljeno.",
    "string_type": "Polje mora biti tekst.",
    "string_too_long": "Vrednost je predugačka.",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_indexes()
    yield


app = FastAPI(title="Files Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        loc = error.get("loc", ())
        field = loc[1] if len(loc) > 1 and isinstance(loc[1], str) else "body"

        if error.get("type") == "value_error":
            message = str(error.get("ctx", {}).get("error", "Neispravna vrednost."))
        else:
            message = DEFAULT_MESSAGES.get(error.get("type"), "Neispravan zahtev.")

        errors.setdefault(field, message)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Podaci nisu ispravni.", "errors": errors},
    )


@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return {"status": "ok", "database": "ok"}
    except Exception:
        return {"status": "ok", "database": "unavailable"}


@app.get("/whoami")
def whoami(user: dict = Depends(get_current_user)):
    return {"user_id": user["id"], "role": user["role"]}