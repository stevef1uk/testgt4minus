from pathlib import Path

import sqlite3

from db import connect, init_schema


def test_schema_has_only_spec_project_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "taskboard.sqlite3"

    init_schema(db_path)

    with sqlite3.connect(db_path) as connection:
        columns = [
            row[1] for row in connection.execute("PRAGMA table_info(projects)")
        ]

    assert columns == ["id", "name", "created_at"]


def test_connect_configures_foreign_keys_and_row_factory(tmp_path: Path) -> None:
    db_path = tmp_path / "taskboard.sqlite3"

    connection = connect(db_path)
    try:
        assert connection.row_factory is sqlite3.Row
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        connection.close()