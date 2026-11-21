from __future__ import annotations

import sqlite3

from taskboard import db


def test_default_path_is_repository_root_relative(monkeypatch, tmp_path):
    monkeypatch.delenv("TASKBOARD_DB_PATH", raising=False)
    monkeypatch.chdir(tmp_path)
    assert db.database_path().name == "taskboard.db"
    assert db.database_path().parent.name == "taskboard"


def test_schema_matches_spec_and_connection_pragmas(tmp_path):
    path = tmp_path / "taskboard.db"
    db.initialize(path)

    with db.connect(path) as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
        projects = {
            row[1] for row in connection.execute("PRAGMA table_info(projects)")
        }
        tasks = {
            row[1] for row in connection.execute("PRAGMA table_info(tasks)")
        }
        assert projects == {"id", "name", "created_at"}
        assert tasks == {
            "id", "project_id", "title", "description", "status", "priority",
            "created_at", "updated_at",
        }

        connection.execute("INSERT INTO projects (name) VALUES (?)", ("same",))
        connection.execute("INSERT INTO projects (name) VALUES (?)", ("same",))
        connection.execute(
            "INSERT INTO tasks (project_id, title, description, status, priority) "
            "VALUES (?, ?, ?, ?, ?)",
            (1, "Task", "", "todo", "medium"),
        )
        timestamp = connection.execute(
            "SELECT created_at FROM projects"
        ).fetchone()[0]
        assert "T" in timestamp
        assert timestamp.endswith("+00:00")


def test_schema_is_idempotent(tmp_path):
    path = tmp_path / "taskboard.db"
    db.initialize(path)
    db.initialize(path)
    with db.connect(path) as connection:
        assert connection.execute("SELECT count(*) FROM projects").fetchone()[0] == 0