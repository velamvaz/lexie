import importlib
import os
from collections.abc import Generator

import pytest
from starlette.testclient import TestClient

# Defaults before any lexie_server import (conftest loads first in pytest)
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake")
os.environ.setdefault("LEXIE_DEVICE_KEY", "test-device")
os.environ.setdefault("LEXIE_ADMIN_TOKEN", "test-admin")
os.environ.setdefault("LEXIE_DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture
def test_client(
    tmp_path, monkeypatch
) -> Generator[TestClient, None, None]:
    """Fresh settings + app + DB per test (isolated file DB under tmp_path)."""
    db_path = tmp_path / "t.db"
    monkeypatch.setenv("LEXIE_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("LEXIE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LEXIE_DEVICE_KEY", "devdev")
    monkeypatch.setenv("LEXIE_ADMIN_TOKEN", "admadm")
    monkeypatch.setenv("LEXIE_LOG_REQUESTS", "0")

    from lexie_server.config import get_settings
    from lexie_server.db import reset_app_state
    from lexie_server import main as main_mod

    reset_app_state()
    get_settings.cache_clear()
    importlib.reload(main_mod)

    with TestClient(main_mod.app) as c:
        yield c

    reset_app_state()
    get_settings.cache_clear()
