from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).with_name("taskboard.db")


def database_path(db_path: str | os.PathLike[str] | None = None) -> Path:
    """Return the configured database path using the documented precedence."""
    if db_path is not None and str(db_path):
        return Path(db_path)
    configured = os.environ.get("TASKBOARD_DB_PATH", "")
    if configured:
        return Path(configured)
    return DEFAULT_DB_PATH


def connect(db_path: str | os.PathLike[str] | None = None) -> sqlite3.Connection:
    """Open a configured SQLite connection and ensure its schema exists."""
    connection = sqlite3.connect(database_path(db_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    _create_schema(connection)
    return connection


def init_schema(db_path: str | os.PathLike[str] | None = None) -> None:
    """Create the application schema idempotently."""
    connection = sqlite3.connect(database_path(db_path))
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        _create_schema(connection)
    finally:
        connection.close()


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'todo',
            priority TEXT NOT NULL DEFAULT 'medium',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_project_id
            ON tasks(project_id);
        """
    )
    connection.commit()