from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_current_user
from app.config import FRONTEND_URL
from app.db import client, ensure_indexes


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