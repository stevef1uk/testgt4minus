from fastapi.testclient import TestClient

from taskboard.main import app

client = TestClient(app)


def test_root_and_static_responses_have_documented_content_types():
    root = client.get("/")
    assert root.status_code == 200
    assert root.headers["content-type"].startswith("text/html")
    assert "TaskBoard" in root.text

    script = client.get("/static/app.js")
    assert script.status_code == 200
    assert script.headers["content-type"].startswith(("text/javascript", "application/javascript"))


def test_documented_errors_and_validation_statuses():
    missing = client.get("/api/projects/999999")
    assert missing.status_code == 404
    assert missing.json() == {"error": "project not found"}
    missing_task = client.get("/api/tasks/999999")
    assert missing_task.status_code == 404
    assert missing_task.json() == {"error": "task not found"}

    malformed = client.get("/api/projects/not-an-integer")
    assert malformed.status_code == 422

    project = client.post("/api/projects", json={"name": "Validation"})
    assert project.status_code == 201
    project_id = project.json()["id"]

    for payload in (
        {"title": "bad", "status": "invalid"},
        {"title": "bad", "priority": "invalid"},
        {"title": ""},
        {"title": "x" * 201},
        {"title": "ok", "description": "x" * 2001},
    ):
        response = client.post(f"/api/projects/{project_id}/tasks", json=payload)
        assert response.status_code == 422
        assert response.headers["content-type"].startswith("application/json")


def test_composed_filters_and_project_delete_cascade():
    project = client.post("/api/projects", json={"name": "Filters"})
    assert project.status_code == 201
    project_id = project.json()["id"]
    for status, priority in (("todo", "high"), ("todo", "low"), ("done", "high")):
        response = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": f"{status}-{priority}", "status": status, "priority": priority},
        )
        assert response.status_code == 201

    filtered = client.get(
        f"/api/projects/{project_id}/tasks",
        params={"status": "todo", "priority": "high"},
    )
    assert filtered.status_code == 200
    assert [task["title"] for task in filtered.json()] == ["todo-high"]

    deleted = client.delete(f"/api/projects/{project_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/api/projects/{project_id}").status_code == 404
    assert client.get(f"/api/projects/{project_id}/tasks").json() == []