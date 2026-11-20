from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def test_create_app_initializes_routes_and_database(tmp_path, monkeypatch):
    database_path = tmp_path / "explicit.sqlite3"
    monkeypatch.setenv("TASKBOARD_DB_PATH", str(tmp_path / "environment.sqlite3"))

    import taskboard.main as main

    application = importlib.reload(main).create_app(str(database_path))
    with TestClient(application) as client:
        assert client.get("/api/health").json() == {"status": "ok"}
        assert client.get("/").status_code == 200
        assert client.get("/").headers["content-type"].startswith("text/html")
        assert client.get("/static/app.js").status_code == 200
        assert client.get("/static/style.css").status_code == 200
        assert database_path.exists()


def test_project_api_validates_creates_lists_and_deletes(tmp_path):
    from taskboard.main import create_app

    with TestClient(create_app(str(tmp_path / "projects.sqlite3"))) as client:
        invalid = client.post("/api/projects", json={"name": "  "})
        assert invalid.status_code == 400
        assert "error" in invalid.json()

        first = client.post("/api/projects", json={"name": "Alpha"})
        second = client.post("/api/projects", json={"name": "Beta"})
        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["name"] == "Alpha"

        projects = client.get("/api/projects")
        assert projects.status_code == 200
        assert [project["name"] for project in projects.json()] == ["Alpha", "Beta"]
        assert [project["id"] for project in projects.json()] == sorted(
            project["id"] for project in projects.json()
        )

        deleted = client.delete(f"/api/projects/{first.json()['id']}")
        assert deleted.status_code in (200, 204)
        assert [project["name"] for project in client.get("/api/projects").json()] == ["Beta"]