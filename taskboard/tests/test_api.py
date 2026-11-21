from __future__ import annotations

from datetime import datetime

import pytest


def assert_timestamp(value: str) -> None:
    assert isinstance(value, str)
    datetime.fromisoformat(value)


def test_root_static_and_api_content_types(client):
    root = client.get("/")
    assert root.status_code == 200
    assert root.headers["content-type"].startswith("text/html")
    assert "Taskboard" in root.text

    static = client.get("/static/style.css")
    assert static.status_code == 200
    assert static.headers["content-type"].startswith("text/css")

    script = client.get("/static/app.js")
    assert script.status_code == 200
    assert script.headers["content-type"].startswith(("text/javascript", "application/javascript"))

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.headers["content-type"].startswith("application/json")


def test_health_and_empty_projects(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.get("/api/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_project_and_task_round_trip_and_ordering(client):
    first = client.post("/api/projects", json={"name": "Alpha"})
    assert first.status_code == 201
    project = first.json()
    assert project["name"] == "Alpha"
    assert_timestamp(project["created_at"])
    second = client.post("/api/projects", json={"name": "Beta"})
    assert second.status_code == 201
    projects = client.get("/api/projects")
    assert projects.status_code == 200
    assert [item["id"] for item in projects.json()] == [project["id"], second.json()["id"]]

    created = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Build API", "description": "Details", "priority": "high"},
    )
    assert created.status_code == 201
    task = created.json()
    assert task["project_id"] == project["id"]
    assert task["title"] == "Build API"
    assert task["description"] == "Details"
    assert task["priority"] == "high"
    assert task["status"] == "todo"
    assert_timestamp(task["created_at"])
    assert_timestamp(task["updated_at"])

    defaulted = client.post(f"/api/projects/{project['id']}/tasks", json={"title": "Default"})
    assert defaulted.status_code == 201
    assert defaulted.json()["description"] == ""
    assert defaulted.json()["priority"] == "medium"
    assert defaulted.json()["status"] == "todo"
    tasks = client.get(f"/api/projects/{project['id']}/tasks")
    assert tasks.status_code == 200
    assert [item["id"] for item in tasks.json()] == [task["id"], defaulted.json()["id"]]


def test_partial_patch_preserves_omitted_values(client):
    project = client.post("/api/projects", json={"name": "Updates"}).json()
    task = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Original", "description": "Details", "priority": "high"},
    ).json()
    response = client.patch(f"/api/tasks/{task['id']}", json={"title": "Renamed", "status": "done"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Renamed"
    assert updated["status"] == "done"
    assert updated["description"] == "Details"
    assert updated["priority"] == "high"
    assert client.patch(f"/api/tasks/{task['id']}", json={}).status_code == 400


@pytest.mark.parametrize(
    ("path", "payload", "status"),
    [
        ("/api/projects", {"name": ""}, 422),
        ("/api/projects/999/tasks", {"title": "orphan"}, 404),
        ("/api/projects/999/tasks", {"title": ""}, 422),
    ],
)
def test_invalid_create_requests_are_rejected(client, path, payload, status):
    response = client.post(path, json=payload)
    assert response.status_code == status
    assert response.headers["content-type"].startswith("application/json")


def test_deferred_error_objects_and_validation_boundaries(client):
    missing = client.get("/api/projects/999")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "project not found"}

    malformed = client.get("/api/projects/not-an-integer")
    assert malformed.status_code == 422
    assert malformed.headers["content-type"].startswith("application/json")
    assert malformed.json()["detail"][0]["type"] == "int_parsing"

    project_id = client.post("/api/projects", json={"name": "Validation"}).json()["id"]
    assert client.get(f"/api/projects/{project_id}/tasks").json() == []

    cases = [
        ({"title": "bad", "status": "invalid"}, "invalid status", {"detail": "invalid status"}),
        ({"title": "bad", "priority": "invalid"}, "invalid priority", {"detail": "invalid priority"}),
        ({"title": ""}, "title", None),
        ({"title": "x" * 301}, "title", None),
        ({"title": "bad", "description": "x" * 1001}, "description", None),
    ]
    for payload, field, expected_body in cases:
        response = client.post(f"/api/projects/{project_id}/tasks", json=payload)
        assert response.status_code == 400
        assert response.headers["content-type"].startswith("application/json")
        body = response.json()
        if expected_body is None:
            assert set(body) == {"error"}
            assert field in body["error"]
        else:
            assert body == expected_body
        assert client.get(f"/api/projects/{project_id}/tasks").json() == []

    created = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Preserved", "description": "short"},
    )
    assert created.status_code == 201
    task_id = created.json()["id"]
    before_patch = client.get(f"/api/projects/{project_id}/tasks").json()

    invalid_patch = client.patch(
        f"/api/tasks/{task_id}",
        json={"title": "Changed", "description": "x" * 1001},
    )
    assert invalid_patch.status_code == 400
    assert set(invalid_patch.json()) == {"error"}
    assert "description" in invalid_patch.json()["error"]
    assert client.get(f"/api/projects/{project_id}/tasks").json() == before_patch


def test_composed_filters_and_project_delete_cascade(client):
    project = client.post("/api/projects", json={"name": "Filters"}).json()
    project_id = project["id"]
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
    assert [task["title"] for task in filtered.json()] == ["todo-high", "todo-low", "done-high"]
    assert all(task["project_id"] == project_id for task in filtered.json())

    deleted = client.delete(f"/api/projects/{project_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/api/projects/{project_id}").status_code == 404
    remaining = client.get(f"/api/projects/{project_id}/tasks")
    assert remaining.status_code == 404
    assert remaining.json() == {"detail": "project not found"}