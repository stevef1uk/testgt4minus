"""Parameterized persistence operations for TaskBoard."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import db
from .models import (
    project_to_dict,
    project_from_row,
    task_to_dict,
    task_from_row,
    validate_project_name,
    validate_task_fields,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project(row: Any) -> dict[str, Any]:
    return project_to_dict(project_from_row(row))


def _task(row: Any) -> dict[str, Any]:
    task = task_to_dict(task_from_row(row))
    task["priority"] = str(row["priority"])
    return task


class ProjectRepository:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        db.initialize(self.db_path)

    def list_projects(self) -> list[dict[str, Any]]:
        with db.connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT id, name, created_at "
                "FROM projects ORDER BY id ASC"
            ).fetchall()
        return [_project(row) for row in rows]

    def create_project(self, name: str) -> dict[str, Any]:
        name = validate_project_name(name)
        now = _utc_now()
        with db.connect(self.db_path) as connection:
            cursor = connection.execute(
                "INSERT INTO projects (name, created_at) VALUES (?, ?)",
                (name, now),
            )
            row = connection.execute(
                "SELECT id, name, created_at FROM projects WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return _project(row)

    def delete_project(self, project_id: int) -> bool:
        with db.connect(self.db_path) as connection:
            cursor = connection.execute(
                "DELETE FROM projects WHERE id = ?", (project_id,)
            )
        return cursor.rowcount > 0


class TaskRepository:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        db.initialize(self.db_path)

    def list_tasks(
        self,
        project_id: int,
        status: str | None = None,
        priority: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses = ["project_id = ?"]
        values: list[Any] = [project_id]
        if status is not None:
            clauses.append("status = ?")
            values.append(status)
        if priority is not None:
            clauses.append("priority = ?")
            values.append(priority)
        with db.connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT id, project_id, title, description, status, priority, "
                "created_at, updated_at FROM tasks WHERE "
                + " AND ".join(clauses)
                + " ORDER BY id ASC",
                values,
            ).fetchall()
        return [_task(row) for row in rows]

    def create_task(
        self,
        project_id: int,
        title: str,
        description: str = "",
        status: str = "todo",
        priority: str = "medium",
    ) -> dict[str, Any]:
        fields = validate_task_fields(
            title=title,
            description=description,
            status=status,
            priority=priority,
        )
        title = fields["title"]
        description = fields["description"]
        status = fields["status"]
        priority = fields["priority"]
        with db.connect(self.db_path) as connection:
            if connection.execute(
                "SELECT 1 FROM projects WHERE id = ?", (project_id,)
            ).fetchone() is None:
                raise ValueError("project does not exist")
            now = _utc_now()
            cursor = connection.execute(
                "INSERT INTO tasks "
                "(project_id, title, description, status, priority, "
                "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    project_id,
                    title,
                    description,
                    status,
                    priority,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT id, project_id, title, description, status, priority, "
                "created_at, updated_at FROM tasks WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return _task(row)

    def update_task(
        self, task_id: int, changes: dict[str, Any]
    ) -> dict[str, Any] | None:
        allowed = {"title", "description", "status", "priority"}
        updates = {key: value for key, value in changes.items() if key in allowed}
        if not updates:
            return self._get(task_id)
        current = self._get(task_id)
        if current is None:
            return None
        fields = validate_task_fields(
            title=updates.get("title", current["title"]),
            description=updates.get("description", current["description"]),
            status=updates.get("status", current["status"]),
            priority=updates.get("priority", current["priority"]),
        )
        updates.update(fields)
        assignments = ", ".join(f"{key} = ?" for key in updates)
        values = list(updates.values()) + [_utc_now(), task_id]
        with db.connect(self.db_path) as connection:
            connection.execute(
                f"UPDATE tasks SET {assignments}, updated_at = ? WHERE id = ?",
                values,
            )
        return self._get(task_id)

    def delete_task(self, task_id: int) -> bool:
        with db.connect(self.db_path) as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0

    def _get(self, task_id: int) -> dict[str, Any] | None:
        with db.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT id, project_id, title, description, status, priority, "
                "created_at, updated_at FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        return _task(row) if row else None


def list_projects(db_path: str | Path) -> list[dict[str, Any]]:
    return ProjectRepository(db_path).list_projects()


def create_project(name: str, db_path: str | Path) -> dict[str, Any]:
    return ProjectRepository(db_path).create_project(name)


def delete_project(project_id: int, db_path: str | Path) -> bool:
    return ProjectRepository(db_path).delete_project(project_id)


def list_tasks(
    project_id: int,
    db_path: str | Path,
    status: str | None = None,
    priority: str | None = None,
) -> list[dict[str, Any]]:
    return TaskRepository(db_path).list_tasks(project_id, status, priority)


def create_task(
    project_id: int,
    title: str,
    db_path: str | Path,
    description: str = "",
    status: str = "todo",
    priority: str = "medium",
) -> dict[str, Any]:
    return TaskRepository(db_path).create_task(
        project_id, title, description, status, priority
    )


def update_task(
    task_id: int, changes: dict[str, Any], db_path: str | Path
) -> dict[str, Any] | None:
    return TaskRepository(db_path).update_task(task_id, changes)


def delete_task(task_id: int, db_path: str | Path) -> bool:
    return TaskRepository(db_path).delete_task(task_id)