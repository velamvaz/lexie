import json
import uuid
from functools import lru_cache

from fastapi import APIRouter, Depends, File, Request, Response, UploadFile
from openai import OpenAI
from sqlalchemy.orm import Session

from lexie_server.config import get_settings
from lexie_server.db import get_db
from lexie_server.deps import require_device_key
from lexie_server.models_orm import AgeProfile, ExplainRequest, ExplainTelemetry, utc_now_iso
from lexie_server.services import pipeline
from lexie_server.services.pipeline import OpenAIUnavailable, PipelineTimings

MAX_BYTES = 2 * 1024 * 1024
router = APIRouter(tags=["explain"])


@lru_cache(maxsize=8)
def _openai_client_for_key(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)


def _client() -> OpenAI:
    s = get_settings()
    if not s.openai_api_key:
        raise ValueError("missing_openai_key")
    return _openai_client_for_key(s.openai_api_key)


def _err(err: str, **extra: object) -> bytes:
    d: dict = {"error": err}
    d.update({k: v for k, v in extra.items()})
    return json.dumps(d, separators=(",", ":")).encode()


def _upload_bucket(n: int) -> str:
    if n <= 8192:
        return "le_8k"
    if n <= 65536:
        return "8k_64k"
    if n <= 524288:
        return "64k_512k"
    return "gt_512k"


def _audio_class(content_type: str | None) -> str:
    if not content_type:
        return "unknown"
    c = content_type.lower()
    if "webm" in c:
        return "webm"
    if "wav" in c:
        return "wav"
    if "mpeg" in c or "mp3" in c:
        return "mp3"
    return "other"


def _stage_for_value_error(code: str) -> str | None:
    if code in {"audio_too_short", "audio_too_long", "unintelligible_audio"}:
        return "duration"
    if code == "transcription_empty":
        return "stt"
    if code == "explanation_invalid":
        return "llm"
    return None


def _persist_explain_telemetry(
    db: Session,
    *,
    profile_id: int,
    request_id: str,
    http_status: int,
    outcome: str,
    failed_stage: str | None,
    timings: PipelineTimings | None,
    total_ms: int | None,
    upload_len: int,
    content_type: str | None,
) -> None:
    s = get_settings()
    if not s.store_telemetry:
        return
    row = ExplainTelemetry(
        id=str(uuid.uuid4()),
        profile_id=profile_id,
        request_id=request_id,
        created_at=utc_now_iso(),
        http_status=http_status,
        outcome=outcome,
        failed_stage=failed_stage,
        total_ms=total_ms,
        duration_check_ms=timings.duration_check_ms if timings else None,
        whisper_ms=timings.whisper_ms if timings else None,
        chat_ms=timings.chat_ms if timings else None,
        tts_ms=timings.tts_ms if timings else None,
        headword_ms=timings.headword_ms if timings else None,
        concat_ms=timings.concat_ms if timings else None,
        upload_bytes_bucket=_upload_bucket(upload_len),
        audio_content_class=_audio_class(content_type),
    )
    db.add(row)
    db.commit()


@router.post(
    "/explain",
    dependencies=[Depends(require_device_key)],
)
def post_explain(
    request: Request,
    db: Session = Depends(get_db),
    audio: UploadFile = File(..., description="Audio field name: audio"),
) -> Response:
    s = get_settings()
    rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    ct: str | None = audio.content_type

    def persist(
        http_status: int,
        outcome: str,
        *,
        failed_stage: str | None = None,
        timings: PipelineTimings | None = None,
        total_ms: int | None = None,
        upload_len: int = 0,
    ) -> None:
        _persist_explain_telemetry(
            db,
            profile_id=1,
            request_id=rid,
            http_status=http_status,
            outcome=outcome,
            failed_stage=failed_stage,
            timings=timings,
            total_ms=total_ms,
            upload_len=upload_len,
            content_type=ct,
        )

    if not s.openai_api_key:
        persist(500, "err_internal", upload_len=0)
        return Response(
            status_code=500, media_type="application/json", content=_err("internal")
        )
    try:
        data = audio.file.read()
    except Exception:  # noqa: BLE001
        persist(500, "err_internal", upload_len=0)
        return Response(
            status_code=500, media_type="application/json", content=_err("internal")
        )
    upload_len = len(data)
    if not data:
        persist(400, "transcription_empty", failed_stage="upload", upload_len=0)
        return Response(
            status_code=400, media_type="application/json", content=_err("transcription_empty")
        )
    if upload_len > MAX_BYTES:
        persist(413, "payload_too_large", failed_stage="upload", upload_len=upload_len)
        return Response(
            status_code=413, media_type="application/json", content=_err("payload_too_large")
        )
    p = db.get(AgeProfile, 1)
    if not p:
        persist(500, "err_internal", upload_len=upload_len)
        return Response(
            status_code=500, media_type="application/json", content=_err("internal")
        )
    try:
        client = _client()
        result = pipeline.run_explain_for_profile(
            client, s, age_profile=p, audio=data, content_type=ct
        )
    except ValueError as e:
        err = str(e)
        stage = _stage_for_value_error(err)
        if err == "audio_too_long":
            persist(
                400,
                "audio_too_long",
                failed_stage=stage,
                upload_len=upload_len,
            )
            return Response(
                status_code=400,
                media_type="application/json",
                content=_err("audio_too_long", max_seconds=30),
            )
        if err in {
            "audio_too_short",
            "transcription_empty",
            "unintelligible_audio",
            "explanation_invalid",
        }:
            persist(400, err, failed_stage=stage, upload_len=upload_len)
            return Response(
                status_code=400,
                media_type="application/json",
                content=_err(err),
            )
        persist(400, err or "err_internal", failed_stage=stage, upload_len=upload_len)
        return Response(
            status_code=400,
            media_type="application/json",
            content=_err(err or "internal"),
        )
    except OpenAIUnavailable as e:
        persist(
            502,
            "openai_unavailable",
            failed_stage=e.stage,
            upload_len=upload_len,
        )
        return Response(
            status_code=502,
            media_type="application/json",
            content=_err("openai_unavailable"),
        )
    except RuntimeError:
        persist(500, "err_internal", upload_len=upload_len)
        return Response(
            status_code=500,
            media_type="application/json",
            content=_err("internal"),
        )

    mp3 = result.mp3
    rtext = result.response_log_text
    elapsed = result.latency_ms
    raw = result.raw_transcript
    wop = result.word_or_phrase
    timings = result.timings

    persist(
        200,
        "ok",
        failed_stage=None,
        timings=timings,
        total_ms=elapsed,
        upload_len=upload_len,
    )

    if s.log_requests:
        er = ExplainRequest(
            id=str(uuid.uuid4()),
            profile_id=1,
            request_id=rid,
            raw_transcript=raw,
            word_or_phrase=wop,
            context_text=None,
            response_text=rtext,
            latency_ms=elapsed,
            created_at=utc_now_iso(),
        )
        db.add(er)
        db.commit()

    h = {"X-Explain-Latency-Ms": str(elapsed), "X-Request-Id": rid}
    return Response(content=mp3, media_type="audio/mpeg", status_code=200, headers=h)
