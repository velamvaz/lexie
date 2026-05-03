"""Admin-only aggregates for explain_telemetry (WX-021)."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from lexie_server.db import get_db
from lexie_server.deps import require_admin
from lexie_server.models_orm import ExplainTelemetry

router = APIRouter(prefix="/admin", tags=["admin"])


def _percentile_nearest_rank(values: list[int], p: float) -> int | None:
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    idx = min(len(s) - 1, max(0, int(round((p / 100.0) * (len(s) - 1)))))
    return s[idx]


def _range_start_end(
    date_from: str | None, date_to: str | None
) -> tuple[date, date, str, str]:
    """Return (start_date, end_date_inclusive, start_key, end_exclusive_key) for string filters."""
    today = datetime.now(timezone.utc).date()
    end_d = date.fromisoformat(date_to) if date_to else today
    start_d = date.fromisoformat(date_from) if date_from else (today - timedelta(days=30))
    if start_d > end_d:
        start_d = end_d
    end_excl = end_d + timedelta(days=1)
    # ISO date prefix compare works with utc_now_iso() values
    start_key = start_d.isoformat()
    end_excl_key = end_excl.isoformat()
    return start_d, end_d, start_key, end_excl_key


@router.get("/telemetry/summary", dependencies=[Depends(require_admin)])
def telemetry_summary(
    db: Session = Depends(get_db),
    date_from: str | None = Query(None, alias="from"),
    date_to: str | None = Query(None, alias="to"),
) -> dict:
    start_d, end_d, start_key, end_excl_key = _range_start_end(date_from, date_to)
    stmt = select(ExplainTelemetry).where(
        ExplainTelemetry.created_at >= start_key,
        ExplainTelemetry.created_at < end_excl_key,
    )
    rows = list(db.execute(stmt).scalars().all())

    by_outcome = dict(Counter(r.outcome for r in rows))
    total = len(rows)

    totals = [r.total_ms for r in rows if r.total_ms is not None]
    ok_rows = [r for r in rows if r.outcome == "ok" and r.total_ms is not None]
    wh = [r.whisper_ms for r in ok_rows if r.whisper_ms is not None]
    ch = [r.chat_ms for r in ok_rows if r.chat_ms is not None]
    tt = [r.tts_ms for r in ok_rows if r.tts_ms is not None]

    daily: Counter[str] = Counter()
    for r in rows:
        day = r.created_at[:10] if len(r.created_at) >= 10 else "unknown"
        daily[day] += 1

    return {
        "period": {
            "from": start_d.isoformat(),
            "to": end_d.isoformat(),
        },
        "total_rows": total,
        "by_outcome": by_outcome,
        "by_day": dict(sorted(daily.items())),
        "latency_ms": {
            "n": len(totals),
            "min": min(totals) if totals else None,
            "max": max(totals) if totals else None,
            "p50": _percentile_nearest_rank(totals, 50),
            "p95": _percentile_nearest_rank(totals, 95),
        },
        "stage_ms_p95_ok": {
            "whisper_ms": _percentile_nearest_rank(wh, 95),
            "chat_ms": _percentile_nearest_rank(ch, 95),
            "tts_ms": _percentile_nearest_rank(tt, 95),
        },
    }


@router.get("/telemetry/recent", dependencies=[Depends(require_admin)])
def telemetry_recent(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    stmt = (
        select(ExplainTelemetry)
        .order_by(ExplainTelemetry.created_at.desc())
        .limit(limit)
    )
    rows = list(db.execute(stmt).scalars().all())

    def row_dict(r: ExplainTelemetry) -> dict:
        return {
            "id": r.id,
            "request_id": r.request_id,
            "created_at": r.created_at,
            "http_status": r.http_status,
            "outcome": r.outcome,
            "failed_stage": r.failed_stage,
            "total_ms": r.total_ms,
            "duration_check_ms": r.duration_check_ms,
            "whisper_ms": r.whisper_ms,
            "chat_ms": r.chat_ms,
            "tts_ms": r.tts_ms,
            "headword_ms": r.headword_ms,
            "concat_ms": r.concat_ms,
            "upload_bytes_bucket": r.upload_bytes_bucket,
            "audio_content_class": r.audio_content_class,
        }

    return {"rows": [row_dict(r) for r in rows]}


@router.get("/telemetry/count", dependencies=[Depends(require_admin)])
def telemetry_count(db: Session = Depends(get_db)) -> dict:
    n = db.execute(select(func.count()).select_from(ExplainTelemetry)).scalar()
    return {"explain_telemetry_rows": int(n or 0)}
