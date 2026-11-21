from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_app_health_and_index(tmp_path):
    from taskboard.main import create_app

    application = create_app(str(tmp_path / "taskboard.sqlite3"))
    with TestClient(application) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        page = client.get("/")
        assert page.status_code == 200
        assert "Taskboard" in page.text


def test_project_and_task_api_persists_records(tmp_path):
    from taskboard.main import create_app

    application = create_app(str(tmp_path / "taskboard.sqlite3"))
    with TestClient(application) as client:
        project_response = client.post("/api/projects", json={"name": "Website"})
        assert project_response.status_code == 201
        project = project_response.json()
        assert project["name"] == "Website"
        assert isinstance(project["id"], int)

        task_response = client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": "Ship landing page", "priority": "medium"},
        )
        assert task_response.status_code == 201
        task = task_response.json()
        assert task["title"] == "Ship landing page"
        assert task["project_id"] == project["id"]

        projects = client.get("/api/projects")
        assert projects.status_code == 200
        assert projects.json()[0]["name"] == "Website"

        tasks = client.get(f"/api/projects/{project['id']}/tasks")
        assert tasks.status_code == 200
        assert tasks.json()[0]["title"] == "Ship landing page"