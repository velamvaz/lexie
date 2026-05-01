import json
import logging
import uuid
from fastapi import APIRouter, Depends, File, Request, Response, UploadFile
from openai import OpenAI
from sqlalchemy.orm import Session

from lexie_server.config import get_settings
from lexie_server.db import get_db
from lexie_server.deps import require_device_key
from lexie_server.models_orm import AgeProfile, ExplainRequest, utc_now_iso
from lexie_server.services import pipeline

logger = logging.getLogger(__name__)

MAX_BYTES = 2 * 1024 * 1024
router = APIRouter(tags=["explain"])


def _client() -> OpenAI:
    s = get_settings()
    if not s.openai_api_key:
        raise ValueError("missing_openai_key")
    return OpenAI(api_key=s.openai_api_key)


def _err(err: str, **extra: object) -> bytes:
    d: dict = {"error": err}
    d.update({k: v for k, v in extra.items()})
    return json.dumps(d, separators=(",", ":")).encode()


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
    if not s.openai_api_key:
        return Response(
            status_code=500, media_type="application/json", content=_err("internal")
        )
    try:
        data = audio.file.read()
    except Exception:  # noqa: BLE001
        return Response(
            status_code=500, media_type="application/json", content=_err("internal")
        )
    if not data:
        return Response(
            status_code=400, media_type="application/json", content=_err("transcription_empty")
        )
    if len(data) > MAX_BYTES:
        return Response(
            status_code=413, media_type="application/json", content=_err("payload_too_large")
        )
    ct = audio.content_type
    p = db.get(AgeProfile, 1)
    if not p:
        return Response(
            status_code=500, media_type="application/json", content=_err("internal")
        )
    try:
        client = _client()
        mp3, rtext, elapsed, raw, wop = pipeline.run_explain_for_profile(
            client, s, age_profile=p, audio=data, content_type=ct
        )
    except ValueError as e:
        err = str(e)
        if err == "audio_too_long":
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
            return Response(400, media_type="application/json", content=_err(err))
        return Response(400, media_type="application/json", content=_err(err or "internal"))
    except RuntimeError as e:
        if "openai_unavailable" in str(e):
            return Response(502, media_type="application/json", content=_err("openai_unavailable"))
        return Response(500, media_type="application/json", content=_err("internal"))

    rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
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
