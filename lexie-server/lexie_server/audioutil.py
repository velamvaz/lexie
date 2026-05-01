import io
from pathlib import Path
from typing import Any

# pydub uses ffmpeg; duration is required by SPEC before OpenAI


def _suffix_from_type(content_type: str | None) -> str:
    if not content_type:
        return "webm"
    t = content_type.split(";")[0].strip().lower()
    m: dict[str, str] = {
        "audio/webm": "webm",
        "audio/wav": "wav",
        "audio/x-wav": "wav",
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
    }
    return m.get(t, "webm")


def get_audio_duration_seconds(data: bytes, content_type: str | None) -> float:
    from pydub import AudioSegment  # import here so tests can mock

    fmt = _suffix_from_type(content_type)
    # pydub: format hint from extension
    seg: Any = AudioSegment.from_file(io.BytesIO(data), format=fmt)
    return len(seg) / 1000.0
