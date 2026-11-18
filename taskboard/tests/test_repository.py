from __future__ import annotations

from datetime import datetime

import pytest

from taskboard.db import init_schema
from taskboard.repository import ProjectRepository, TaskRepository


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "taskboard-test.db"
    init_schema(path)
    return path


def test_project_repository_starts_empty_and_is_idempotent(db_path):
    init_schema(db_path)
    repository = ProjectRepository(db_path)
    assert repository.list_projects() == []


def test_projects_are_created_and_listed_in_id_order(db_path):
    repository = ProjectRepository(db_path)
    first = repository.create_project("  Alpha  ")
    second = repository.create_project("Beta")

    assert first["name"] == "Alpha"
    assert repository.list_projects() == [first, second]
    assert first["id"] < second["id"]
    datetime.fromisoformat(first["created_at"])


def test_project_delete_reports_missing_and_cascades_tasks(db_path):
    projects = ProjectRepository(db_path)
    tasks = TaskRepository(db_path)
    project = projects.create_project("Alpha")
    task = tasks.create_task(project["id"], "Task")

    assert projects.delete_project(project["id"]) is True
    assert projects.delete_project(project["id"]) is False
    assert tasks.list_tasks(project["id"]) == []


def test_tasks_have_defaults_filters_and_ascending_ids(db_path):
    projects = ProjectRepository(db_path)
    tasks = TaskRepository(db_path)
    project = projects.create_project("Alpha")

    first = tasks.create_task(project["id"], "First")
    second = tasks.create_task(
        project["id"], "Second", description="Details", priority="high", status="doing"
    )
    third = tasks.create_task(
        project["id"], "Third", priority="high", status="done"
    )

    assert first["status"] == "todo"
    assert first["priority"] == "medium"
    assert [item["id"] for item in tasks.list_tasks(project["id"])] == [
        first["id"], second["id"], third["id"]
    ]
    assert [item["id"] for item in tasks.list_tasks(project["id"], status="doing")] == [
        second["id"]
    ]
    assert [item["id"] for item in tasks.list_tasks(project["id"], priority="high")] == [
        second["id"], third["id"]
    ]
    assert tasks.list_tasks(project["id"], status="doing", priority="high") == [second]
    datetime.fromisoformat(first["created_at"])
    datetime.fromisoformat(first["updated_at"])


def test_task_update_is_partial_and_delete_reports_missing(db_path):
    projects = ProjectRepository(db_path)
    tasks = TaskRepository(db_path)
    project = projects.create_project("Alpha")
    task = tasks.create_task(project["id"], "Original", description="Keep", priority="low")

    updated = tasks.update_task(task["id"], {"title": "Updated", "status": "done"})
    assert updated["title"] == "Updated"
    assert updated["status"] == "done"
    assert updated["description"] == "Keep"
    assert updated["priority"] == "low"
    assert tasks.update_task(9999, {"title": "Missing"}) is None
    assert tasks.delete_task(task["id"]) is True
    assert tasks.delete_task(task["id"]) is False


@pytest.mark.parametrize(
    ("operation", "arguments"),
    [
        ("create_project", ("",)),
        ("create_task", (1, "")),
        ("create_task", (1, "Task", "", "urgent", "todo")),
        ("create_task", (1, "Task", "", "medium", "blocked")),
    ],
)
def test_repository_rejects_invalid_fields(db_path, operation, arguments):
    projects = ProjectRepository(db_path)
    tasks = TaskRepository(db_path)
    project = projects.create_project("Alpha")

    if operation == "create_project":
        with pytest.raises(ValueError):
            projects.create_project(*arguments)
    else:
        arguments = (project["id"],) + arguments[1:]
        with pytest.raises(ValueError):
            tasks.create_task(*arguments)