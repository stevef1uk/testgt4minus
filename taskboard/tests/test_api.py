from __future__ import annotations

from datetime import datetime

import pytest


def assert_timestamp(value: str) -> None:
    assert isinstance(value, str)
    datetime.fromisoformat(value)


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
    assert [item["id"] for item in projects.json()] == [
        project["id"],
        second.json()["id"],
    ]

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

    defaulted = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Default"},
    )
    assert defaulted.status_code == 201
    assert defaulted.json()["description"] == ""
    assert defaulted.json()["priority"] == "medium"
    assert defaulted.json()["status"] == "todo"

    tasks = client.get(f"/api/projects/{project['id']}/tasks")
    assert tasks.status_code == 200
    assert [item["id"] for item in tasks.json()] == [
        task["id"],
        defaulted.json()["id"],
    ]


def test_partial_patch_preserves_omitted_values(client):
    project = client.post("/api/projects", json={"name": "Updates"}).json()
    task = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Original", "description": "Details", "priority": "high"},
    ).json()

    response = client.patch(
        f"/api/tasks/{task['id']}",
        json={"title": "Renamed", "status": "doing"},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Renamed"
    assert updated["status"] == "in_progress"
    assert updated["description"] == "Details"
    assert updated["priority"] == "high"

    assert client.patch(f"/api/tasks/{task['id']}", json={}).status_code == 400


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/api/projects", {"name": ""}),
        ("/api/projects/999/tasks", {"title": "orphan"}),
        ("/api/projects/999/tasks", {"title": ""}),
    ],
)
def test_invalid_create_requests_are_rejected(client, path, payload):
    response = client.post(path, json=payload)
    assert response.status_code in {400, 404, 422}


def test_missing_resources_and_bodyless_deletes(client):
    assert client.get("/api/projects/999/tasks").status_code == 404
    assert client.patch("/api/tasks/999", json={"title": "missing"}).status_code == 404
    assert client.delete("/api/projects/999").status_code == 404
    assert client.delete("/api/tasks/999").status_code == 404

    project = client.post("/api/projects", json={"name": "Delete"}).json()
    task = client.post(
        f"/api/projects/{project['id']}/tasks", json={"title": "Task"}
    ).json()

    deleted_task = client.delete(f"/api/tasks/{task['id']}")
    assert deleted_task.status_code == 204
    assert deleted_task.content == b""

    deleted_project = client.delete(f"/api/projects/{project['id']}")
    assert deleted_project.status_code == 204
    assert deleted_project.content == b""