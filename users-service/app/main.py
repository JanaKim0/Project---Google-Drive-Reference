from fastapi import FastAPI
from app.db import client
from app.routes import router

app = FastAPI(title="Users Service")
app.include_router(router)


@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return {"status": "ok", "database": "ok"}
    except Exception:
        return {"status": "ok", "database": "unavailable"}