import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from lexie_server.config import get_settings
from lexie_server.db import create_tables, seed_profile_if_empty
from lexie_server.routers import admin, explain, health, profile, telemetry, usage


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    create_tables(s)
    from lexie_server.db import _SessionLocal  # noqa: SLF001

    assert _SessionLocal is not None
    db = _SessionLocal()
    try:
        seed_profile_if_empty(s, db)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title="Lexie", lifespan=lifespan)
    origins = [o.strip() for o in s.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = rid
        response: Response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        return response

    app.include_router(health.router)
    app.include_router(profile.router)
    app.include_router(explain.router)
    app.include_router(admin.router)
    app.include_router(usage.router)
    app.include_router(telemetry.router)
    app.mount(
        "/prototype",
        StaticFiles(
            directory=str(Path(__file__).resolve().parent / "static_prototype"),
            html=True,
        ),
        name="prototype",
    )
    return app


# Uvicorn:  uvicorn lexie_server.main:app
app = create_app()
