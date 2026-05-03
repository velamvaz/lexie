import importlib
import os
from collections.abc import Generator
from pathlib import Path

import pytest
from starlette.testclient import TestClient

# Defaults before any lexie_server import (conftest loads first in pytest)
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake")
os.environ.setdefault("LEXIE_DEVICE_KEY", "test-device")
os.environ.setdefault("LEXIE_ADMIN_TOKEN", "test-admin")
os.environ.setdefault("LEXIE_DATABASE_URL", "sqlite:///:memory:")


def _reload_app_with_db(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    log_requests: str,
    store_telemetry: str = "0",
) -> Path:
    db_path = tmp_path / "t.db"
    monkeypatch.setenv("LEXIE_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("LEXIE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LEXIE_DEVICE_KEY", "devdev")
    monkeypatch.setenv("LEXIE_ADMIN_TOKEN", "admadm")
    monkeypatch.setenv("LEXIE_LOG_REQUESTS", log_requests)
    monkeypatch.setenv("LEXIE_STORE_TELEMETRY", store_telemetry)

    from lexie_server.config import get_settings
    from lexie_server.db import reset_app_state
    from lexie_server import main as main_mod

    reset_app_state()
    get_settings.cache_clear()
    importlib.reload(main_mod)
    return db_path


@pytest.fixture
def test_client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    """Fresh settings + app + DB per test (isolated file DB under tmp_path)."""
    _reload_app_with_db(tmp_path, monkeypatch, log_requests="0")
    from lexie_server.config import get_settings
    from lexie_server.db import reset_app_state
    from lexie_server import main as main_mod

    try:
        with TestClient(main_mod.app) as c:
            yield c
    finally:
        reset_app_state()
        get_settings.cache_clear()


@pytest.fixture
def test_client_and_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[tuple[TestClient, Path], None, None]:
    """TestClient plus SQLite path for direct DB assertions (e.g. explain_request rows)."""
    _reload_app_with_db(tmp_path, monkeypatch, log_requests="0")
    from lexie_server.config import get_settings
    from lexie_server.db import reset_app_state
    from lexie_server import main as main_mod

    db_path = tmp_path / "t.db"
    try:
        with TestClient(main_mod.app) as c:
            yield c, db_path
    finally:
        reset_app_state()
        get_settings.cache_clear()


@pytest.fixture
def test_client_log_requests_on(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[tuple[TestClient, Path], None, None]:
    """Same as test_client_and_db but LEXIE_LOG_REQUESTS=1."""
    _reload_app_with_db(tmp_path, monkeypatch, log_requests="1")
    from lexie_server.config import get_settings
    from lexie_server.db import reset_app_state
    from lexie_server import main as main_mod

    db_path = tmp_path / "t.db"
    try:
        with TestClient(main_mod.app) as c:
            yield c, db_path
    finally:
        reset_app_state()
        get_settings.cache_clear()


@pytest.fixture
def test_client_telemetry_on(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[tuple[TestClient, Path], None, None]:
    """SQLite file DB with LEXIE_STORE_TELEMETRY=1 (WX-020)."""
    _reload_app_with_db(tmp_path, monkeypatch, log_requests="0", store_telemetry="1")
    from lexie_server.config import get_settings
    from lexie_server.db import reset_app_state
    from lexie_server import main as main_mod

    db_path = tmp_path / "t.db"
    try:
        with TestClient(main_mod.app) as c:
            yield c, db_path
    finally:
        reset_app_state()
        get_settings.cache_clear()
