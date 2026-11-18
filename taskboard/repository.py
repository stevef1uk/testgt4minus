"""SQLite repositories for TaskBoard projects and tasks."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import connect, init_schema
from .models import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    project_from_row,
    task_from_row,
    validate_project_name,
    validate_task_fields,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProjectRepository:
    """Persist and retrieve projects from a SQLite database."""

    def __init__(self, db_path: str | Path):
        self.db_path = db_path
        init_schema(db_path)

    def list_projects(self) -> list[dict[str, Any]]:
        with connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT id, name, created_at FROM projects ORDER BY id ASC"
            ).fetchall()
        return [project_from_row(row) for row in rows]

    def create_project(self, name: str) -> dict[str, Any]:
        normalized_name = validate_project_name(name)
        created_at = _utc_now()
        with connect(self.db_path) as connection:
            cursor = connection.execute(
                "INSERT INTO projects (name, created_at) VALUES (?, ?)",
                (normalized_name, created_at),
            )
            project_id = cursor.lastrowid
        return {"id": project_id, "name": normalized_name, "created_at": created_at}

    def delete_project(self, project_id: int) -> bool:
        with connect(self.db_path) as connection:
            cursor = connection.execute(
                "DELETE FROM projects WHERE id = ?", (project_id,)
            )
        return cursor.rowcount > 0


class TaskRepository:
    """Persist and retrieve tasks from a SQLite database."""

    def __init__(self, db_path: str | Path):
        self.db_path = db_path
        init_schema(db_path)

    def list_tasks(
        self,
        project_id: int,
        status: str | None = None,
        priority: str | None = None,
    ) -> list[dict[str, Any]]:
        if status is not None and status not in VALID_STATUSES:
            raise ValueError("invalid status")
        if priority is not None and priority not in VALID_PRIORITIES:
            raise ValueError("invalid priority")

        clauses = ["project_id = ?"]
        parameters: list[object] = [project_id]
        if status is not None:
            clauses.append("status = ?")
            parameters.append(status)
        if priority is not None:
            clauses.append("priority = ?")
            parameters.append(priority)

        query = (
            "SELECT id, project_id, title, description, status, priority, "
            "created_at, updated_at FROM tasks WHERE "
            + " AND ".join(clauses)
            + " ORDER BY id ASC"
        )
        with connect(self.db_path) as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [task_from_row(row) for row in rows]

    def create_task(
        self,
        project_id: int,
        title: str,
        description: str = "",
        priority: str = "medium",
        status: str = "todo",
    ) -> dict[str, Any]:
        fields = validate_task_fields(title, description, priority, status)
        now = _utc_now()
        with connect(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks
                    (project_id, title, description, status, priority,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    fields["title"],
                    fields["description"],
                    fields["status"],
                    fields["priority"],
                    now,
                    now,
                ),
            )
            task_id = cursor.lastrowid
            row = connection.execute(
                """
                SELECT id, project_id, title, description, status, priority,
                       created_at, updated_at
                FROM tasks WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
        return task_from_row(row)

    def update_task(
        self, task_id: int, changes: dict[str, Any]
    ) -> dict[str, Any] | None:
        if not changes:
            raise ValueError("task changes cannot be empty")
        allowed = {"title", "description", "priority", "status"}
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError("unsupported task field")

        with connect(self.db_path) as connection:
            existing = connection.execute(
                """
                SELECT id, project_id, title, description, status, priority,
                       created_at, updated_at
                FROM tasks WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
            if existing is None:
                return None

            values = {
                "title": existing["title"],
                "description": existing["description"],
                "priority": existing["priority"],
                "status": existing["status"],
            }
            values.update(changes)
            fields = validate_task_fields(**values)
            updated_at = _utc_now()
            connection.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, status = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    fields["title"],
                    fields["description"],
                    fields["priority"],
                    fields["status"],
                    updated_at,
                    task_id,
                ),
            )
            row = connection.execute(
                """
                SELECT id, project_id, title, description, status, priority,
                       created_at, updated_at
                FROM tasks WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
        return task_from_row(row)

    def delete_task(self, task_id: int) -> bool:
        with connect(self.db_path) as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0