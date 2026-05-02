from pathlib import Path

from sqlalchemy import create_engine, text


def _count_explain_request_rows(db_path: Path) -> int:
    eng = create_engine(f"sqlite:///{db_path}")
    with eng.connect() as conn:
        return int(conn.execute(text("select count(*) from explain_request")).scalar_one())


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


def test_explain_200_with_pipeline_mock(test_client, monkeypatch) -> None:
    from lexie_server.routers import explain as explain_router

    def _fake_run(*_a, **_k):
        return b"\xff" * 8, "Explained", 99, "raw t", "word"

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

    def _fake_run(*_a, **_k):
        return b"\xff" * 8, "{}", 10, "raw", "w"

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


def test_explain_inserts_explain_request_when_log_on(
    test_client_log_requests_on, monkeypatch
) -> None:
    from lexie_server.routers import explain as explain_router

    def _fake_run(*_a, **_k):
        return b"\xff" * 8, '{"explanation_text":"x"}', 10, "raw", "w"

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

    def _fake_run(*_a, **_k):
        return b"\xff" * 8, "{}", 1, "raw", "w"

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
