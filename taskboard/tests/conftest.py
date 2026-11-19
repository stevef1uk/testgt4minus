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
    with TestClient(application) as test_client:
        yield test_client