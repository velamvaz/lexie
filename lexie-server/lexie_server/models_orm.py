import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class AgeProfile(Base):
    __tablename__ = "age_profile"
    # Single-row profile: id is always 1 (data-model option B)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    child_name: Mapped[str] = mapped_column(String(200), nullable=False)
    age_years: Mapped[int] = mapped_column(Integer, nullable=False)
    reading_level: Mapped[str] = mapped_column(String(300), nullable=False)
    explanation_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)


class ExplainRequest(Base):
    __tablename__ = "explain_request"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("age_profile.id", ondelete="CASCADE"), nullable=False
    )
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_transcript: Mapped[str] = mapped_column(Text, nullable=False)
    word_or_phrase: Mapped[str] = mapped_column(Text, nullable=False)
    context_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
