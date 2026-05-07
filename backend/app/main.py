import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import (
    admin,
    auth,
    data,
    export,
    history,
    logs,
    public_admission,
    query,
    settings,
    users,
)
from app.db.base import Base
from app.db.migrations import ensure_user_columns
from app.db.postgres import engine
from app.models import (
    academic_data,
    log,
    query_history,
    settings as settings_model,
    user,
)

app = FastAPI(title="NEU Data Query System")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3004",
        "http://127.0.0.1:3004",
        "http://0.0.0.0:3004",
        "http://aimsb.ddnsfree.com:3004",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_user_columns(engine)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(logs.router)
app.include_router(settings.router)
app.include_router(admin.router)
app.include_router(data.router)
app.include_router(query.router)
app.include_router(history.router)
app.include_router(export.router)
app.include_router(public_admission.router)
