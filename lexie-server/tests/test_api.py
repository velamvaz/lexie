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


def test_prototype_served(test_client) -> None:
    r = test_client.get("/prototype/")
    assert r.status_code in (200, 307)


def test_admin_page_200(test_client) -> None:
    r = test_client.get("/admin")
    assert r.status_code == 200
    assert "Lexie" in r.text
