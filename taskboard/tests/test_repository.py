from __future__ import annotations

from datetime import datetime

import pytest

from taskboard import repository


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "taskboard.sqlite3")


def test_empty_lists_and_idempotent_initialization(db_path):
    assert repository.list_projects(db_path) == []
    assert repository.list_tasks(999, db_path=db_path) == []
    assert repository.list_projects(db_path) == []


def test_projects_have_ascending_ids_and_utc_timestamps(db_path):
    first = repository.create_project(" First ", db_path=db_path)
    second = repository.create_project("Second", db_path=db_path)

    assert first["id"] < second["id"]
    assert first["name"] == "First"
    assert datetime.fromisoformat(first["created_at"]).tzinfo is not None
    assert repository.list_projects(db_path) == [first, second]


def test_tasks_defaults_filters_and_conjunction(db_path):
    project = repository.create_project("Project", db_path=db_path)
    first = repository.create_task(
        project["id"],
        "First",
        description="details",
        db_path=db_path,
    )
    second = repository.create_task(project["id"], "Second", db_path=db_path)
    second = repository.update_task(
        second["id"],
        {"status": "doing", "priority": "high"},
        db_path=db_path,
    )

    assert second is not None
    assert first["status"] == "todo"
    assert first["priority"] == "medium"
    assert repository.list_tasks(project["id"], db_path=db_path) == [first, second]
    assert repository.list_tasks(project["id"], status="doing", db_path=db_path) == [second]
    assert repository.list_tasks(project["id"], priority="high", db_path=db_path) == [second]
    assert repository.list_tasks(
        project["id"], status="doing", priority="high", db_path=db_path
    ) == [second]


def test_partial_update_preserves_omitted_values(db_path):
    project = repository.create_project("Project", db_path=db_path)
    task = repository.create_task(
        project["id"],
        "Original",
        description="keep",
        priority="high",
        db_path=db_path,
    )

    updated = repository.update_task(
        task["id"], {"title": "Changed", "status": "done"}, db_path=db_path
    )

    assert updated is not None
    assert updated["title"] == "Changed"
    assert updated["status"] == "done"
    assert updated["description"] == "keep"
    assert updated["priority"] == "high"


def test_project_delete_cascades_tasks_and_missing_deletes_are_false(db_path):
    project = repository.create_project("Project", db_path=db_path)
    task = repository.create_task(project["id"], "Task", db_path=db_path)

    assert repository.delete_project(project["id"], db_path=db_path) is True
    assert repository.list_tasks(project["id"], db_path=db_path) == []
    assert repository.delete_project(project["id"], db_path=db_path) is False
    assert repository.delete_task(task["id"], db_path=db_path) is False