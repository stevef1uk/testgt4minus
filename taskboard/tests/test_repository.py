from __future__ import annotations

import pytest

from taskboard import db
from taskboard.repository import ProjectRepository, TaskRepository


@pytest.fixture()
def repositories(tmp_path):
    path = tmp_path / "taskboard.db"
    db.initialize(path)
    return ProjectRepository(path), TaskRepository(path)


def test_schema_is_idempotent_and_empty(repositories):
    projects, tasks = repositories
    db.initialize(projects.db_path)
    assert projects.list_projects() == []
    assert tasks.list_tasks(1) == []


def test_projects_and_tasks_have_defaults_and_ascending_ids(repositories):
    projects, tasks = repositories
    first = projects.create_project(" Alpha ")
    second = projects.create_project("Beta")
    assert [item["id"] for item in projects.list_projects()] == [
        first["id"], second["id"]
    ]
    task = tasks.create_task(first["id"], "Ship it")
    assert task["title"] == "Ship it"
    assert task["status"] == "todo"
    assert task["priority"] == "medium"
    assert "T" in task["created_at"]


def test_task_filters_compose_and_partial_update_preserves_values(repositories):
    projects, tasks = repositories
    project = projects.create_project("Project")
    high = tasks.create_task(project["id"], "High", priority="high", status="doing")
    tasks.create_task(project["id"], "Low", priority="low", status="todo")
    assert [item["id"] for item in tasks.list_tasks(
        project["id"], "doing", "high"
    )] == [high["id"]]
    updated = tasks.update_task(high["id"], {"title": "Renamed"})
    assert updated["title"] == "Renamed"
    assert updated["priority"] == "high"
    assert updated["status"] == "doing"


def test_project_delete_cascades_tasks(repositories):
    projects, tasks = repositories
    project = projects.create_project("Project")
    task = tasks.create_task(project["id"], "Task")
    assert projects.delete_project(project["id"]) is True
    assert tasks.list_tasks(project["id"]) == []
    assert tasks.delete_task(task["id"]) is False