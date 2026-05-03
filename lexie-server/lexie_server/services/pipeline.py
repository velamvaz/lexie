import json
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import httpx
from openai import APIStatusError, OpenAI, RateLimitError

from lexie_server.audioutil import get_audio_duration_seconds
from lexie_server.config import Settings
from lexie_server.prompts import build_system_message, json_user_instruction


class OpenAIUnavailable(RuntimeError):
    """Upstream OpenAI/HTTP failure; ``stage`` is stt | llm | tts for telemetry."""

    def __init__(self, stage: str) -> None:
        self.stage = stage
        super().__init__(f"openai_unavailable:{stage}")


@dataclass(frozen=True)
class PipelineTimings:
    duration_check_ms: int
    whisper_ms: int
    chat_ms: int
    tts_ms: int
    headword_ms: int
    concat_ms: int


@dataclass(frozen=True)
class ExplainPipelineResult:
    mp3: bytes
    response_log_text: str
    latency_ms: int
    raw_transcript: str
    word_or_phrase: str
    timings: PipelineTimings


def _with_retries(fn: Any, *, attempts: int = 3) -> Any:
    delay = 0.5
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except RateLimitError as e:
            last = e
            if i + 1 == attempts:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 4.0)
        except APIStatusError as e:
            last = e
            st = getattr(e, "status_code", None) or 0
            if st in (429, 500, 502, 503) and i + 1 < attempts:
                time.sleep(delay)
                delay = min(delay * 2, 4.0)
                continue
            raise
    if last:
        raise last
    raise RuntimeError("unreachable")


def _transcribe_open(
    client: OpenAI, settings: Settings, audio: bytes, content_type: str | None
) -> str:
    buf = BytesIO(audio)
    if content_type and "wav" in content_type.lower():
        ext = "wav"
    elif content_type and "mpeg" in content_type.lower():
        ext = "mp3"
    else:
        ext = "webm"
    buf.name = f"in.{ext}"
    r = _with_retries(
        lambda: client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=buf,
        )
    )
    return (getattr(r, "text", None) or "") if r else ""


def _chat_json(
    client: OpenAI,
    settings: Settings,
    system_message: str,
    transcript: str,
    need_headword: bool,
) -> dict[str, Any]:
    inst = json_user_instruction(need_headword)
    r = _with_retries(
        lambda: client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[
                {"role": "system", "content": system_message},
                {
                    "role": "user",
                    "content": f"{inst}\n\nTranscript: {transcript}",
                },
            ],
            max_tokens=200,
            response_format={"type": "json_object"},
        )
    )
    content = (r.choices[0].message.content or "").strip()  # type: ignore[union-attr]
    if not content:
        raise ValueError("explanation_invalid")
    try:
        j = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError("explanation_invalid") from e
    if not isinstance(j, dict):
        raise ValueError("explanation_invalid")
    return j


def _tts_bytes(client: OpenAI, settings: Settings, t: str) -> bytes:
    s = _with_retries(
        lambda: client.audio.speech.create(
            model=settings.openai_tts_model,
            voice=settings.openai_tts_voice,  # type: ignore[arg-type]
            input=t,
        )
    )
    if hasattr(s, "read"):
        return s.read()  # type: ignore[no-any-return]
    return b""


def _concat_mp3(a: bytes, b: bytes) -> bytes:
    from pydub import AudioSegment

    s1 = AudioSegment.from_file(BytesIO(a), format="mp3")
    s2 = AudioSegment.from_file(BytesIO(b), format="mp3")
    out = s1 + s2
    buf = BytesIO()
    out.export(buf, format="mp3")
    return buf.getvalue()


def _trunc_transcript(s: str, n: int) -> str:
    if len(s) <= n:
        return s
    return s[:n]


def run_explain_for_profile(
    client: OpenAI,
    settings: Settings,
    *,
    age_profile: Any,
    audio: bytes,
    content_type: str | None,
) -> ExplainPipelineResult:
    """Run Whisper → chat JSON → TTS; return audio, log text, timings (WX-020)."""
    t0 = time.perf_counter()
    try:
        dur = get_audio_duration_seconds(audio, content_type)
    except Exception:  # noqa: BLE001 — ffmpeg/pydub: treat as unprocessable
        raise ValueError("unintelligible_audio") from None
    duration_check_ms = int((time.perf_counter() - t0) * 1000)
    if dur < 0.4:
        raise ValueError("audio_too_short")
    if dur > 30.0:
        raise ValueError("audio_too_long")
    t_ws = time.perf_counter()
    try:
        raw = (_transcribe_open(client, settings, audio, content_type) or "").strip()
    except (APIStatusError, RateLimitError, httpx.RequestError) as e:
        raise OpenAIUnavailable("stt") from e
    whisper_ms = int((time.perf_counter() - t_ws) * 1000)
    if not raw:
        raise ValueError("transcription_empty")
    need_head = settings.headword_tts
    sm = build_system_message(
        age_profile.child_name,
        age_profile.age_years,
        age_profile.reading_level,
        age_profile.explanation_style,
    )
    t_chat = time.perf_counter()
    try:
        j = _chat_json(client, settings, sm, raw, need_headword=need_head)
    except ValueError:
        raise
    except (APIStatusError, RateLimitError, httpx.RequestError) as e:
        raise OpenAIUnavailable("llm") from e
    chat_ms = int((time.perf_counter() - t_chat) * 1000)

    explanation_text = (j.get("explanation_text") or "").strip()
    if not explanation_text:
        raise ValueError("explanation_invalid")

    if need_head:
        hw = (j.get("headword") or "").strip()
        text_for_log = json.dumps(
            {"explanation_text": explanation_text, "headword": hw or None},
            ensure_ascii=False,
        )
    else:
        text_for_log = json.dumps(
            {"explanation_text": explanation_text},
            ensure_ascii=False,
        )
    wop = _trunc_transcript(raw, 200)

    headword_ms = 0
    concat_ms = 0
    t_tts = time.perf_counter()
    try:
        mp3 = _tts_bytes(client, settings, explanation_text)
    except (APIStatusError, RateLimitError, httpx.RequestError) as e:
        raise OpenAIUnavailable("tts") from e
    tts_ms = int((time.perf_counter() - t_tts) * 1000)
    try:
        if need_head and (j.get("headword") or "").strip():
            t_hw = time.perf_counter()
            mp3 = _concat_mp3(
                mp3, _tts_bytes(client, settings, (j.get("headword") or "").strip())
            )
            headword_ms = int((time.perf_counter() - t_hw) * 1000)
            # _concat_mp3 includes second TTS; split not exact — store combined as headword_ms
            concat_ms = 0
    except (APIStatusError, RateLimitError, httpx.RequestError) as e:
        raise OpenAIUnavailable("tts") from e
    except Exception as e:  # noqa: BLE001
        raise OpenAIUnavailable("tts") from e

    elapsed = int((time.perf_counter() - t0) * 1000)
    timings = PipelineTimings(
        duration_check_ms=duration_check_ms,
        whisper_ms=whisper_ms,
        chat_ms=chat_ms,
        tts_ms=tts_ms,
        headword_ms=headword_ms,
        concat_ms=concat_ms,
    )
    return ExplainPipelineResult(
        mp3=mp3,
        response_log_text=text_for_log,
        latency_ms=elapsed,
        raw_transcript=raw,
        word_or_phrase=wop,
        timings=timings,
    )
