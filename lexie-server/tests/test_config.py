"""Settings / env aliases (regression: wrong names in .env silently ignored)."""

from lexie_server.config import Settings


def test_settings_reads_lexie_chat_model_env(monkeypatch) -> None:
    monkeypatch.setenv("LEXIE_CHAT_MODEL", "gpt-test-model")
    s = Settings()
    assert s.openai_chat_model == "gpt-test-model"


def test_settings_reads_lexie_tts_model_and_voice_env(monkeypatch) -> None:
    monkeypatch.setenv("LEXIE_TTS_MODEL", "tts-test")
    monkeypatch.setenv("LEXIE_TTS_VOICE", "echo")
    s = Settings()
    assert s.openai_tts_model == "tts-test"
    assert s.openai_tts_voice == "echo"


def test_lexie_openai_chat_model_is_not_an_alias(monkeypatch) -> None:
    """Document: LEXIE_OPENAI_* names are NOT read (extra=ignore)."""
    monkeypatch.setenv("LEXIE_OPENAI_CHAT_MODEL", "should-not-apply")
    monkeypatch.delenv("LEXIE_CHAT_MODEL", raising=False)
    s = Settings()
    assert s.openai_chat_model == "gpt-4o-mini"
