"""Admin telemetry APIs (WX-021)."""

from sqlalchemy import create_engine, text

from lexie_server.models_orm import utc_now_iso


def test_telemetry_summary_401_without_admin(test_client) -> None:
    r = test_client.get("/admin/telemetry/summary")
    assert r.status_code == 401


def test_telemetry_summary_200_empty(test_client) -> None:
    r = test_client.get(
        "/admin/telemetry/summary",
        headers={"Authorization": "Bearer admadm"},
    )
    assert r.status_code == 200
    j = r.json()
    assert j["total_rows"] == 0
    assert j["by_outcome"] == {}
    assert "period" in j


def test_telemetry_summary_with_rows(test_client_telemetry_on, monkeypatch) -> None:
    from lexie_server.routers import explain as explain_router
    from lexie_server.services.pipeline import ExplainPipelineResult, PipelineTimings

    def _fake_run(*_a, **_k):
        return ExplainPipelineResult(
            mp3=b"\xff" * 4,
            response_log_text="{}",
            latency_ms=100,
            raw_transcript="x",
            word_or_phrase="w",
            timings=PipelineTimings(1, 10, 20, 30, 0, 0),
        )

    monkeypatch.setattr(
        explain_router.pipeline, "run_explain_for_profile", _fake_run
    )
    client, db_path = test_client_telemetry_on
    r = client.post(
        "/explain",
        files={"audio": ("a.webm", b"\x00" * 32, "audio/webm")},
        headers={"Authorization": "Bearer devdev"},
    )
    assert r.status_code == 200

    r2 = client.get(
        "/admin/telemetry/summary",
        headers={"Authorization": "Bearer admadm"},
    )
    assert r2.status_code == 200
    j = r2.json()
    assert j["total_rows"] >= 1
    assert j["by_outcome"].get("ok", 0) >= 1
    assert j["latency_ms"]["n"] >= 1
    assert j["latency_ms"]["p50"] == 100


def test_telemetry_recent_limit(test_client) -> None:
    r = test_client.get(
        "/admin/telemetry/recent?limit=3",
        headers={"Authorization": "Bearer admadm"},
    )
    assert r.status_code == 200
    assert r.json()["rows"] == []


def test_telemetry_count(test_client) -> None:
    r = test_client.get(
        "/admin/telemetry/count",
        headers={"Authorization": "Bearer admadm"},
    )
    assert r.status_code == 200
    assert r.json()["explain_telemetry_rows"] == 0


def test_telemetry_row_roundtrip_sql(test_client_telemetry_on) -> None:
    """Direct insert + summary picks up row (date filter)."""
    client, db_path = test_client_telemetry_on
    now = utc_now_iso()
    eng = create_engine(f"sqlite:///{db_path}")
    with eng.begin() as conn:
        conn.execute(
            text(
                "insert into explain_telemetry (id, profile_id, request_id, created_at, "
                "http_status, outcome, failed_stage, total_ms, duration_check_ms, "
                "whisper_ms, chat_ms, tts_ms, headword_ms, concat_ms, "
                "upload_bytes_bucket, audio_content_class) values "
                "(:id, 1, 'r1', :created_at, 200, 'ok', null, 50, 1, 2, 3, 4, 0, 0, "
                "'le_8k', 'webm')"
            ),
            {"id": "t-test-1", "created_at": now},
        )

    r = client.get(
        "/admin/telemetry/summary",
        headers={"Authorization": "Bearer admadm"},
    )
    assert r.status_code == 200
    assert r.json()["total_rows"] >= 1
