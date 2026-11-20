from __future__ import annotations

from datetime import datetime, timezone

import pytest

from taskboard import db, repository


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "taskboard.sqlite3")


def test_invalid_and_overlong_names_are_rejected(db_path):
    with pytest.raises(ValueError):
        repository.create_project("   ", db_path=db_path)

    with pytest.raises(ValueError):
        repository.create_project("x" * 101, db_path=db_path)

    project = repository.create_project("Project", db_path=db_path)
    with pytest.raises(ValueError):
        repository.create_task(project["id"], "", db_path=db_path)

    with pytest.raises(ValueError):
        repository.create_task(project["id"], "x" * 121, db_path=db_path)


def test_empty_lists_and_idempotent_initialization(db_path):
    assert repository.list_projects(db_path) == []
    assert repository.list_tasks(999, db_path=db_path) == []
    assert repository.list_projects(db_path) == []


def test_projects_have_ascending_ids_and_utc_timestamps(db_path):
    first = repository.create_project(" First ", db_path=db_path)
    second = repository.create_project("Second", db_path=db_path)

    assert first["id"] < second["id"]
    assert first["name"] == "First"
    created_at = datetime.fromisoformat(first["created_at"])
    assert created_at.tzinfo is not None
    assert created_at.utcoffset() == timezone.utc.utcoffset(created_at)
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


def test_special_characters_round_trip_without_sql_interpolation(db_path):
    project_name = "R&D / O'Reilly — 项目"
    task_title = 'Fix "quoted" & escaped — 测试'

    project = repository.create_project(project_name, db_path=db_path)
    task = repository.create_task(project["id"], task_title, db_path=db_path)

    assert repository.list_projects(db_path) == [project]
    assert repository.list_tasks(project["id"], db_path=db_path) == [task]
    assert project["name"] == project_name
    assert task["title"] == task_title


def test_schema_initialization_is_explicitly_idempotent(db_path):
    assert repository.list_projects(db_path) == []
    assert repository.list_projects(db_path) == []

    project = repository.create_project("After repeated initialization", db_path=db_path)

    assert repository.list_projects(db_path) == [project]


def test_schema_contract_has_tables_pragmas_and_project_index(db_path):
    db.init_schema(db_path)

    with db.connect(db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert {"projects", "tasks"} <= tables
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA busy_timeout").fetchone()[0] == 5000

        indexes = connection.execute("PRAGMA index_list(tasks)").fetchall()
        indexed_columns = {
            column[2]
            for index in indexes
            for column in connection.execute(
                f'PRAGMA index_info("{index[1]}")'
            ).fetchall()
        }
        assert "project_id" in indexed_columns
def test_project_and_task_field_contract_has_expected_types(db_path):
    project = repository.create_project("Project", db_path=db_path)
    task = repository.create_task(project["id"], "Task", db_path=db_path)

    assert set(project) == {"id", "name", "created_at"}
    assert isinstance(project["id"], int)
    assert isinstance(project["name"], str)
    assert isinstance(project["created_at"], str)

    assert set(task) == {
        "id",
        "project_id",
        "title",
        "description",
        "status",
        "priority",
        "created_at",
        "updated_at",
    }
    assert isinstance(task["id"], int)
    assert isinstance(task["project_id"], int)
    assert isinstance(task["title"], str)
    assert isinstance(task["description"], str)
    assert isinstance(task["status"], str)
    assert isinstance(task["priority"], str)
    assert isinstance(task["created_at"], str)
    assert isinstance(task["updated_at"], str)


def test_invalid_descriptions_statuses_and_priorities_are_rejected(db_path):
    project = repository.create_project("Project", db_path=db_path)

    for description in ("x" * 1001,):
        with pytest.raises(ValueError):
            repository.create_task(
                project["id"], "Task", description=description, db_path=db_path
            )

    task = repository.create_task(project["id"], "Task", db_path=db_path)

    for status in ("invalid", "", None):
        with pytest.raises(ValueError):
            repository.update_task(
                task["id"], {"status": status}, db_path=db_path
            )

    for priority in ("invalid", "", None):
        with pytest.raises(ValueError):
            repository.update_task(
                task["id"], {"priority": priority}, db_path=db_path
            )