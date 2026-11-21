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
    with db.connect(projects.db_path) as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        indexes = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            )
        }
        assert {"projects", "tasks"}.issubset(tables)
        assert "idx_tasks_project_status_priority" in indexes
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
    assert projects.list_projects() == []
    assert tasks.list_tasks(1) == []


def test_projects_and_tasks_have_defaults_and_ascending_ids(repositories):
    projects, tasks = repositories
    first = projects.create_project(" Alpha ")
    second = projects.create_project("Beta")
    assert [item["id"] for item in projects.list_projects()] == [
        first["id"], second["id"]
    ]
    assert first["name"] == "Alpha"
    assert "description" not in first
    assert first["created_at"].endswith("+00:00")
    assert second["id"] > first["id"]
    task = tasks.create_task(first["id"], "Ship it")
    assert task["title"] == "Ship it"
    assert task["status"] == "todo"
    assert task["priority"] == "medium"
    assert task["description"] == ""
    assert task["created_at"].endswith("+00:00")
    assert task["updated_at"].endswith("+00:00")


def test_validation_length_and_unicode_rules(repositories):
    projects, tasks = repositories
    with pytest.raises(ValueError):
        projects.create_project("")
    with pytest.raises(ValueError):
        projects.create_project("x" * 201)
    with pytest.raises(ValueError):
        tasks.create_task(999, "orphan")
    with pytest.raises(ValueError):
        tasks.create_task(
            projects.create_project("Unicode ✅")["id"],
            "x" * 201,
        )
    project = projects.create_project("日本語 🚀")
    task = tasks.create_task(project["id"], "Задача", description="描述")
    assert project["name"] == "日本語 🚀"
    assert task["title"] == "Задача"
    assert task["description"] == "描述"


def test_task_filters_compose_and_partial_update_preserves_values(repositories):
    projects, tasks = repositories
    project = projects.create_project("Project")
    high = tasks.create_task(
        project["id"], "High", priority="high", status="doing"
    )
    tasks.create_task(project["id"], "Low", priority="low", status="todo")
    assert [item["id"] for item in tasks.list_tasks(
        project["id"], "doing", "high"
    )] == [high["id"]]
    updated = tasks.update_task(high["id"], {"title": "Renamed"})
    assert updated["title"] == "Renamed"
    assert updated["priority"] == "high"
    assert updated["status"] == "doing"
    assert tasks.update_task(999, {"title": "missing"}) is None


def test_separate_connections_persist_parameterized_values(repositories):
    projects, tasks = repositories
    project = projects.create_project("O'Reilly; DROP TABLE projects;")
    task = tasks.create_task(project["id"], "Quote ' and Unicode 🚀")
    with db.connect(projects.db_path) as connection:
        row = connection.execute(
            "SELECT name FROM projects WHERE id = ?", (project["id"],)
        ).fetchone()
        assert row["name"] == "O'Reilly; DROP TABLE projects;"
    assert TaskRepository(projects.db_path).list_tasks(project["id"])[0]["title"] == (
        "Quote ' and Unicode 🚀"
    )
    assert projects.list_projects()


def test_foreign_key_rejects_direct_orphan(repositories):
    projects, _ = repositories
    with db.connect(projects.db_path) as connection:
        with pytest.raises(Exception):
            connection.execute(
                "INSERT INTO tasks (project_id, title) VALUES (?, ?)",
                (999, "orphan"),
            )


def test_project_delete_cascades_tasks(repositories):
    projects, tasks = repositories
    project = projects.create_project("Project")
    task = tasks.create_task(project["id"], "Task")
    assert projects.delete_project(project["id"]) is True
    assert tasks.list_tasks(project["id"]) == []
    assert tasks.delete_task(task["id"]) is False