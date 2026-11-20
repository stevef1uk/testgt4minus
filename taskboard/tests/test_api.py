from __future__ import annotations


def test_health_endpoint_returns_exact_status(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_renders_html_with_static_assets(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="project-page"' in response.text
    assert "/static/app" in response.text
    assert "/static/style" in response.text


def test_static_assets_are_reachable(client):
    app_script = client.get("/static/app.js")
    stylesheet = client.get("/static/style.css")
    assert app_script.status_code == 200
    assert app_script.content
    assert stylesheet.status_code == 200
    assert stylesheet.content


def test_projects_start_empty(client):
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_create_project_persists_and_ignores_unknown_fields(client):
    response = client.post(
        "/api/projects",
        json={"name": " Alpha ", "unknown": "ignored"},
    )
    assert response.status_code == 201
    project = response.json()
    assert project["name"] == "Alpha"
    assert set(project) == {"id", "name", "created_at"}

    listed = client.get("/api/projects")
    assert listed.status_code == 200
    assert listed.json() == [project]


def test_invalid_project_payload_returns_error(client):
    response = client.post("/api/projects", json={"name": "   "})
    assert response.status_code == 400
    assert "error" in response.json()

    missing = client.post("/api/projects", json={})
    assert missing.status_code == 400
    assert "error" in missing.json()


def test_delete_project_returns_empty_204_and_404_for_missing(client):
    project = client.post("/api/projects", json={"name": "Temporary"}).json()

    deleted = client.delete(f"/api/projects/{project['id']}")
    assert deleted.status_code == 204
    assert deleted.content == b""

    missing = client.delete(f"/api/projects/{project['id']}")
    assert missing.status_code == 404
    assert "error" in missing.json()


def test_configured_databases_are_isolated(tmp_path, monkeypatch):
    import importlib
    from fastapi.testclient import TestClient

    first_path = tmp_path / "first.sqlite3"
    second_path = tmp_path / "second.sqlite3"
    import taskboard.main as main

    monkeypatch.setenv("TASKBOARD_DB_PATH", str(first_path))
    first_app = importlib.reload(main).create_app(str(first_path))
    with TestClient(first_app) as first_client:
        created = first_client.post("/api/projects", json={"name": "First"})
        assert created.status_code == 201
        assert [item["name"] for item in first_client.get("/api/projects").json()] == ["First"]

    monkeypatch.setenv("TASKBOARD_DB_PATH", str(second_path))
    second_app = importlib.reload(main).create_app(str(second_path))
    with TestClient(second_app) as second_client:
        assert second_client.get("/api/projects").json() == []


def test_missing_project_returns_structured_404(client):
    response = client.get("/api/projects/999999")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "project not found"}