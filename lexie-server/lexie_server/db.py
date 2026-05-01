from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from lexie_server.config import Settings, get_settings
from lexie_server.models_orm import AgeProfile, Base, utc_now_iso

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def reset_app_state() -> None:
    """Dispose the SQLAlchemy engine and clear session factory (tests / process reuse)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def init_engine(settings: Settings) -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(
            settings.effective_database_url,
            connect_args={"check_same_thread": False} if "sqlite" in settings.effective_database_url else {},
        )
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def create_tables(settings: Settings) -> None:
    e = init_engine(settings)
    Base.metadata.create_all(bind=e)


def get_db() -> Generator[Session, None, None]:
    s = get_settings()
    init_engine(s)
    assert _SessionLocal is not None
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_profile_if_empty(settings: Settings, db: Session) -> None:
    if db.get(AgeProfile, 1) is not None:
        return
    now = utc_now_iso()
    db.add(
        AgeProfile(
            id=1,
            child_name="Child",
            age_years=6,
            reading_level="grade-level",
            explanation_style=None,
            created_at=now,
            updated_at=now,
        )
    )
    db.commit()
