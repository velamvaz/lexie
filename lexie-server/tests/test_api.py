import importlib
from pathlib import Path

from sqlalchemy import create_engine, text
from starlette.testclient import TestClient


def _count_explain_request_rows(db_path: Path) -> int:
    eng = create_engine(f"sqlite:///{db_path}")
    with eng.connect() as conn:
        return int(conn.execute(text("select count(*) from explain_request")).scalar_one())


def _count_explain_telemetry_rows(db_path: Path) -> int:
    eng = create_engine(f"sqlite:///{db_path}")
    with eng.connect() as conn:
        return int(conn.execute(text("select count(*) from explain_telemetry")).scalar_one())


def test_health(test_client) -> None:
    r = test_client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "version" in data


def test_profile_401_without_admin(test_client) -> None:
    r = test_client.get("/profile")
    assert r.status_code == 401
    assert r.json()["detail"]["error"] == "unauthorized"


def test_profile_200_with_admin(test_client) -> None:
    r = test_client.get(
        "/profile", headers={"Authorization": "Bearer admadm"}
    )
    assert r.status_code == 200
    j = r.json()
    assert j["child_name"] == "Child"
    assert j["age_years"] == 6
    assert j["reading_level"] == "grade-level"


def test_profile_patch_no_fields(test_client) -> None:
    r = test_client.patch(
        "/profile",
        json={},
        headers={"Authorization": "Bearer admadm"},
    )
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "no_fields"


def test_explain_401_no_device_key(test_client) -> None:
    r = test_client.post(
        "/explain",
        files={"audio": ("a.webm", b"x", "audio/webm")},
    )
    assert r.status_code == 401
    assert r.json()["detail"]["error"] == "unauthorized"


def test_explain_401_wrong_device_key(test_client) -> None:
    r = test_client.post(
        "/explain",
        files={"audio": ("a.webm", b"x", "audio/webm")},
        headers={"Authorization": "Bearer not-the-device-key"},
    )
    assert r.status_code == 401
    assert r.json()["detail"]["error"] == "unauthorized"


def test_explain_200_with_x_device_key_header(test_client, monkeypatch) -> None:
    """SPEC: X-Device-Key accepted when LEXIE_DEVICE_KEY is set."""
    from lexie_server.routers import explain as explain_router
    from lexie_server.services.pipeline import ExplainPipelineResult, PipelineTimings

    def _fake_run(*_a, **_k):
        return ExplainPipelineResult(
            mp3=b"\xff" * 4,
            response_log_text="{}",
            latency_ms=7,
            raw_transcript="t",
            word_or_phrase="w",
            timings=PipelineTimings(0, 0, 0, 0, 0, 0),
        )

    monkeypatch.setattr(
        explain_router.pipeline, "run_explain_for_profile", _fake_run
    )
    r = test_client.post(
        "/explain",
        files={"audio": ("a.webm", b"\x00" * 16, "audio/webm")},
        headers={"X-Device-Key": "devdev"},
    )
    assert r.status_code == 200
    assert r.headers.get("X-Explain-Latency-Ms") == "7"


def test_explain_502_openai_unavailable(test_client, monkeypatch) -> None:
    from lexie_server.routers import explain as explain_router
    from lexie_server.services.pipeline import OpenAIUnavailable

    def _boom(*_a, **_k):
        raise OpenAIUnavailable("llm")

    monkeypatch.setattr(
        explain_router.pipeline, "run_explain_for_profile", _boom
    )
    r = test_client.post(
        "/explain",
        files={"audio": ("a.webm", b"\x00" * 16, "audio/webm")},
        headers={"Authorization": "Bearer devdev"},
    )
    assert r.status_code == 502
    assert r.json()["error"] == "openai_unavailable"


def test_explain_500_missing_openai_key(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "t.db"
    monkeypatch.setenv("LEXIE_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("LEXIE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("LEXIE_DEVICE_KEY", "devdev")
    monkeypatch.setenv("LEXIE_ADMIN_TOKEN", "admadm")
    monkeypatch.setenv("LEXIE_LOG_REQUESTS", "0")
    monkeypatch.setenv("LEXIE_STORE_TELEMETRY", "0")

    from lexie_server.config import get_settings
    from lexie_server.db import reset_app_state
    from lexie_server import main as main_mod

    reset_app_state()
    get_settings.cache_clear()
    importlib.reload(main_mod)
    try:
        with TestClient(main_mod.app) as c:
            r = c.post(
                "/explain",
                files={"audio": ("a.webm", b"\x00" * 16, "audio/webm")},
                headers={"Authorization": "Bearer devdev"},
            )
        assert r.status_code == 500
        assert r.json()["error"] == "internal"
    finally:
        reset_app_state()
        get_settings.cache_clear()
        importlib.reload(main_mod)


def test_admin_usage_401_without_admin(test_client) -> None:
    assert test_client.get("/admin/usage").status_code == 401


def test_admin_usage_200_with_admin(test_client) -> None:
    r = test_client.get(
        "/admin/usage",
        headers={"Authorization": "Bearer admadm"},
    )
    assert r.status_code == 200
    j = r.json()
    assert "month" in j and "explain_count" in j
    assert j["explain_count"] == 0


def test_explain_200_with_pipeline_mock(test_client, monkeypatch) -> None:
    from lexie_server.routers import explain as explain_router
    from lexie_server.services.pipeline import ExplainPipelineResult, PipelineTimings

    def _fake_run(*_a, **_k):
        return ExplainPipelineResult(
            mp3=b"\xff" * 8,
            response_log_text="Explained",
            latency_ms=99,
            raw_transcript="raw t",
            word_or_phrase="word",
            timings=PipelineTimings(1, 2, 3, 4, 0, 0),
        )

    monkeypatch.setattr(
        explain_router.pipeline, "run_explain_for_profile", _fake_run
    )
    r = test_client.post(
        "/explain",
        files={"audio": ("a.webm", b"\x00" * 16, "audio/webm")},
        headers={"Authorization": "Bearer devdev"},
    )
    assert r.status_code == 200
    assert r.content == b"\xff" * 8
    assert r.headers.get("X-Explain-Latency-Ms") == "99"
    assert r.headers.get("content-type", "").startswith("audio/mpeg")


def test_explain_413_payload_too_large(test_client, monkeypatch) -> None:
    from lexie_server.routers import explain as explain_router

    def _boom(*_a, **_k):
        raise AssertionError("pipeline must not run when body exceeds MAX_BYTES")

    monkeypatch.setattr(
        explain_router.pipeline, "run_explain_for_profile", _boom
    )
    from lexie_server.routers.explain import MAX_BYTES

    huge = b"z" * (MAX_BYTES + 1)
    r = test_client.post(
        "/explain",
        files={"audio": ("a.webm", huge, "audio/webm")},
        headers={"Authorization": "Bearer devdev"},
    )
    assert r.status_code == 413
    assert r.json()["error"] == "payload_too_large"


def test_explain_no_explain_request_row_when_log_off(
    test_client_and_db, monkeypatch
) -> None:
    from lexie_server.routers import explain as explain_router
    from lexie_server.services.pipeline import ExplainPipelineResult, PipelineTimings

    def _fake_run(*_a, **_k):
        return ExplainPipelineResult(
            mp3=b"\xff" * 8,
            response_log_text="{}",
            latency_ms=10,
            raw_transcript="raw",
            word_or_phrase="w",
            timings=PipelineTimings(1, 1, 1, 1, 0, 0),
        )

    monkeypatch.setattr(
        explain_router.pipeline, "run_explain_for_profile", _fake_run
    )
    client, db_path = test_client_and_db
    r = client.post(
        "/explain",
        files={"audio": ("a.webm", b"\x00" * 16, "audio/webm")},
        headers={"Authorization": "Bearer devdev"},
    )
    assert r.status_code == 200
    assert _count_explain_request_rows(db_path) == 0
    assert _count_explain_telemetry_rows(db_path) == 0


def test_explain_inserts_telemetry_when_store_on(
    test_client_telemetry_on, monkeypatch
) -> None:
    """WX-020: LEXIE_STORE_TELEMETRY=1 inserts explain_telemetry (no PII columns)."""
    from lexie_server.routers import explain as explain_router
    from lexie_server.services.pipeline import ExplainPipelineResult, PipelineTimings

    def _fake_run(*_a, **_k):
        return ExplainPipelineResult(
            mp3=b"\xff" * 8,
            response_log_text="{}",
            latency_ms=42,
            raw_transcript="raw",
            word_or_phrase="w",
            timings=PipelineTimings(5, 10, 15, 12, 0, 0),
        )

    monkeypatch.setattr(
        explain_router.pipeline, "run_explain_for_profile", _fake_run
    )
    client, db_path = test_client_telemetry_on
    r = client.post(
        "/explain",
        files={"audio": ("a.webm", b"\x00" * 16, "audio/webm")},
        headers={"Authorization": "Bearer devdev"},
    )
    assert r.status_code == 200
    assert _count_explain_telemetry_rows(db_path) == 1
    eng = create_engine(f"sqlite:///{db_path}")
    with eng.connect() as conn:
        row = conn.execute(
            text(
                "select outcome, http_status, total_ms, duration_check_ms, "
                "whisper_ms, chat_ms, tts_ms from explain_telemetry limit 1"
            )
        ).one()
    assert row.outcome == "ok"
    assert row.http_status == 200
    assert row.total_ms == 42
    assert row.duration_check_ms == 5
    assert row.whisper_ms == 10
    assert row.chat_ms == 15
    assert row.tts_ms == 12


def test_explain_inserts_explain_request_when_log_on(
    test_client_log_requests_on, monkeypatch
) -> None:
    from lexie_server.routers import explain as explain_router
    from lexie_server.services.pipeline import ExplainPipelineResult, PipelineTimings

    def _fake_run(*_a, **_k):
        return ExplainPipelineResult(
            mp3=b"\xff" * 8,
            response_log_text='{"explanation_text":"x"}',
            latency_ms=10,
            raw_transcript="raw",
            word_or_phrase="w",
            timings=PipelineTimings(1, 1, 1, 1, 0, 0),
        )

    monkeypatch.setattr(
        explain_router.pipeline, "run_explain_for_profile", _fake_run
    )
    client, db_path = test_client_log_requests_on
    r = client.post(
        "/explain",
        files={"audio": ("a.webm", b"\x00" * 16, "audio/webm")},
        headers={"Authorization": "Bearer devdev"},
    )
    assert r.status_code == 200
    assert _count_explain_request_rows(db_path) == 1


def test_explain_does_not_persist_upload_as_audio_files_under_data_dir(
    test_client_and_db, monkeypatch, tmp_path: Path
) -> None:
    """WX-018 / C6: default path keeps uploads in memory; no raw audio files on disk."""
    from lexie_server.routers import explain as explain_router
    from lexie_server.services.pipeline import ExplainPipelineResult, PipelineTimings

    def _fake_run(*_a, **_k):
        return ExplainPipelineResult(
            mp3=b"\xff" * 8,
            response_log_text="{}",
            latency_ms=1,
            raw_transcript="raw",
            word_or_phrase="w",
            timings=PipelineTimings(0, 0, 0, 0, 0, 0),
        )

    monkeypatch.setattr(
        explain_router.pipeline, "run_explain_for_profile", _fake_run
    )
    client, _db_path = test_client_and_db
    audio_suffixes = {".webm", ".wav", ".mp3", ".ogg", ".m4a"}

    def _audio_files() -> list[Path]:
        return [
            p
            for p in tmp_path.rglob("*")
            if p.is_file() and p.suffix.lower() in audio_suffixes
        ]

    assert not _audio_files()
    r = client.post(
        "/explain",
        files={"audio": ("user.webm", b"\x00" * 400, "audio/webm")},
        headers={"Authorization": "Bearer devdev"},
    )
    assert r.status_code == 200
    assert not _audio_files()


def test_prototype_served(test_client) -> None:
    r = test_client.get("/prototype/")
    assert r.status_code in (200, 307)


def test_admin_page_200(test_client) -> None:
    r = test_client.get("/admin")
    assert r.status_code == 200
    assert "Lexie" in r.text
    assert "telemetry" in r.text.lower()
