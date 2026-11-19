from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from . import db
from .models import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    project_from_row,
    task_from_row,
    validate_project_name,
    validate_task_fields,
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connection(db_path: str | None = None):
    return db.connect(db_path)


def list_projects(db_path: str | None = None) -> list[dict[str, Any]]:
    with _connection(db_path) as connection:
        rows = connection.execute(
            "SELECT id, name, created_at FROM projects ORDER BY id ASC"
        ).fetchall()
    return [project_from_row(row) for row in rows]


def create_project(name: str, db_path: str | None = None) -> dict[str, Any]:
    normalized_name = validate_project_name(name)
    created_at = _timestamp()
    with _connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO projects (name, created_at) VALUES (?, ?)",
            (normalized_name, created_at),
        )
        row = connection.execute(
            "SELECT id, name, created_at FROM projects WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        connection.commit()
    if row is None:
        raise RuntimeError("created project could not be read")
    return project_from_row(row)


def delete_project(project_id: int, db_path: str | None = None) -> bool:
    with _connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        connection.commit()
    return cursor.rowcount > 0


def _project_exists(connection: Any, project_id: int) -> bool:
    return (
        connection.execute(
            "SELECT 1 FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        is not None
    )


def list_tasks(
    project_id: int,
    status: str | None = None,
    priority: str | None = None,
    db_path: str | None = None,
) -> list[dict[str, Any]]:
    if status is not None and status not in VALID_STATUSES:
        raise ValueError("invalid task status")
    if priority is not None and priority not in VALID_PRIORITIES:
        raise ValueError("invalid task priority")

    query = """
        SELECT id, project_id, title, description, status, priority,
               created_at, updated_at
        FROM tasks
        WHERE project_id = ?
    """
    parameters: list[Any] = [project_id]
    if status is not None:
        query += " AND status = ?"
        parameters.append(status)
    if priority is not None:
        query += " AND priority = ?"
        parameters.append(priority)
    query += " ORDER BY id ASC"

    with _connection(db_path) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [task_from_row(row) for row in rows]


def create_task(
    project_id: int,
    title: str,
    description: str | None = None,
    priority: str | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    fields = validate_task_fields(
        title=title,
        description="" if description is None else description,
        priority="medium" if priority is None else priority,
        status="todo",
    )
    created_at = _timestamp()
    with _connection(db_path) as connection:
        if not _project_exists(connection, project_id):
            raise LookupError("project not found")
        cursor = connection.execute(
            """
            INSERT INTO tasks
                (project_id, title, description, status, priority, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                fields["title"],
                fields["description"],
                fields["status"],
                fields["priority"],
                created_at,
                created_at,
            ),
        )
        row = connection.execute(
            """
            SELECT id, project_id, title, description, status, priority,
                   created_at, updated_at
            FROM tasks WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        connection.commit()
    if row is None:
        raise RuntimeError("created task could not be read")
    return task_from_row(row)


def update_task(
    task_id: int,
    changes: dict[str, Any],
    db_path: str | None = None,
) -> dict[str, Any] | None:
    if not changes:
        raise ValueError("task update cannot be empty")
    unknown = set(changes) - {"title", "description", "priority", "status"}
    if unknown:
        raise ValueError("unknown task fields")

    fields = validate_task_fields(
        title=changes.get("title"),
        description=changes.get("description"),
        priority=changes.get("priority"),
        status=changes.get("status"),
        partial=True,
    )
    if not fields:
        raise ValueError("task update cannot be empty")

    assignments = ", ".join(f"{name} = ?" for name in fields)
    values = list(fields.values())
    values.extend([_timestamp(), task_id])

    with _connection(db_path) as connection:
        cursor = connection.execute(
            f"UPDATE tasks SET {assignments}, updated_at = ? WHERE id = ?",
            values,
        )
        if cursor.rowcount == 0:
            connection.commit()
            return None
        row = connection.execute(
            """
            SELECT id, project_id, title, description, status, priority,
                   created_at, updated_at
            FROM tasks WHERE id = ?
            """,
            (task_id,),
        ).fetchone()
        connection.commit()
    return task_from_row(row) if row is not None else None


def delete_task(task_id: int, db_path: str | None = None) -> bool:
    with _connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()
    return cursor.rowcount > 0


class ProjectRepository:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path

    def list_projects(self) -> list[dict[str, Any]]:
        return list_projects(self.db_path)

    def create_project(self, name: str) -> dict[str, Any]:
        return create_project(name, self.db_path)

    def delete_project(self, project_id: int) -> bool:
        return delete_project(project_id, self.db_path)


class TaskRepository:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path

    def list_tasks(
        self,
        project_id: int,
        status: str | None = None,
        priority: str | None = None,
    ) -> list[dict[str, Any]]:
        return list_tasks(project_id, status, priority, self.db_path)

    def create_task(
        self,
        project_id: int,
        title: str,
        description: str | None = None,
        priority: str | None = None,
    ) -> dict[str, Any]:
        return create_task(
            project_id, title, description, priority, self.db_path
        )

    def update_task(
        self, task_id: int, changes: dict[str, Any]
    ) -> dict[str, Any] | None:
        return update_task(task_id, changes, self.db_path)

    def delete_task(self, task_id: int) -> bool:
        return delete_task(task_id, self.db_path)