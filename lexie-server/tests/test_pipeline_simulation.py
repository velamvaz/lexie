"""Simulations for /explain pipeline: call order, gating, headword path (no live OpenAI)."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from lexie_server.services import pipeline as pipeline_mod

_PROFILE = SimpleNamespace(
    child_name="Child",
    age_years=6,
    reading_level="grade-level",
    explanation_style=None,
)


def test_run_explain_happy_path_whisper_chat_tts_order(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        pipeline_mod, "get_audio_duration_seconds", lambda *_a, **_k: 1.0
    )

    def _transcribe(*_a, **_k):
        calls.append("transcribe")
        return "sorcerer"

    def _chat(*_a, **_k):
        calls.append("chat")
        return {"explanation_text": "A sorcerer is a kind of magic user."}

    def _tts(*_a, **_k):
        calls.append("tts")
        return b"fake-mp3-a"

    monkeypatch.setattr(pipeline_mod, "_transcribe_open", _transcribe)
    monkeypatch.setattr(pipeline_mod, "_chat_json", _chat)
    monkeypatch.setattr(pipeline_mod, "_tts_bytes", _tts)

    settings = MagicMock()
    settings.headword_tts = False
    settings.whisper_model = "whisper-1"
    settings.openai_chat_model = "gpt-4o-mini"
    settings.openai_tts_model = "tts-1"
    settings.openai_tts_voice = "nova"

    mp3, _log, _lat, _raw, _wop = pipeline_mod.run_explain_for_profile(
        MagicMock(),
        settings,
        age_profile=_PROFILE,
        audio=b"\x00" * 100,
        content_type="audio/webm",
    )

    assert calls == ["transcribe", "chat", "tts"]
    assert mp3 == b"fake-mp3-a"


def test_run_explain_headword_two_tts_and_concat(monkeypatch: pytest.MonkeyPatch) -> None:
    tts_calls: list[str] = []

    monkeypatch.setattr(
        pipeline_mod, "get_audio_duration_seconds", lambda *_a, **_k: 1.0
    )
    monkeypatch.setattr(
        pipeline_mod, "_transcribe_open", lambda *_a, **_k: "word"
    )
    monkeypatch.setattr(
        pipeline_mod,
        "_chat_json",
        lambda *_a, **_k: {
            "explanation_text": "Explanation line.",
            "headword": "sorcerer",
        },
    )

    def _tts(_client, _settings, text: str) -> bytes:
        tts_calls.append(text)
        return f"MP3:{text}".encode()

    concat_calls: list[tuple[bytes, bytes]] = []

    def _concat(a: bytes, b: bytes) -> bytes:
        concat_calls.append((a, b))
        return a + b"+concat+" + b

    monkeypatch.setattr(pipeline_mod, "_tts_bytes", _tts)
    monkeypatch.setattr(pipeline_mod, "_concat_mp3", _concat)

    settings = MagicMock()
    settings.headword_tts = True
    settings.whisper_model = "whisper-1"
    settings.openai_chat_model = "gpt-4o-mini"
    settings.openai_tts_model = "tts-1"
    settings.openai_tts_voice = "nova"

    mp3, _log, _lat, _raw, _wop = pipeline_mod.run_explain_for_profile(
        MagicMock(),
        settings,
        age_profile=_PROFILE,
        audio=b"\x00" * 100,
        content_type="audio/webm",
    )

    assert tts_calls == ["Explanation line.", "sorcerer"]
    assert len(concat_calls) == 1
    assert concat_calls[0][0] == b"MP3:Explanation line."
    assert concat_calls[0][1] == b"MP3:sorcerer"
    assert b"+concat+" in mp3


def test_run_explain_audio_too_short_skips_whisper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        pipeline_mod, "get_audio_duration_seconds", lambda *_a, **_k: 0.2
    )

    def _should_not_transcribe(*_a, **_k):
        raise AssertionError("Whisper should not run when duration < 0.4s")

    monkeypatch.setattr(pipeline_mod, "_transcribe_open", _should_not_transcribe)

    settings = MagicMock()
    settings.headword_tts = False

    with pytest.raises(ValueError, match="audio_too_short"):
        pipeline_mod.run_explain_for_profile(
            MagicMock(),
            settings,
            age_profile=_PROFILE,
            audio=b"\x00" * 100,
            content_type="audio/webm",
        )
