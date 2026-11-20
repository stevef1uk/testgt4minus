from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "taskboard.sqlite3"
    monkeypatch.setenv("TASKBOARD_DB_PATH", str(database_path))

    import taskboard.main as main

    application = importlib.reload(main).create_app(str(database_path))
    # The fixture contract is a fresh, usable database-backed client for every test.
    assert database_path.exists()
    with TestClient(application) as test_client:
        health = test_client.get("/api/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}
        yield test_client