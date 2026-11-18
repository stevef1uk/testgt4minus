"""Pure validation and row‑mapping helpers for TaskBoard."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

VALID_STATUSES = ("todo", "doing", "done")
VALID_PRIORITIES = ("low", "medium", "high")


def validate_project_name(name: str) -> str:
    """Trim and validate a project name."""
    if not isinstance(name, str):
        raise ValueError("project name must be a string")
    value = name.strip()
    if not value:
        raise ValueError("project name cannot be empty")
    if len(value) > 80:
        raise ValueError("project name cannot exceed 80 characters")
    return value


def validate_task_fields(
    title: str,
    description: str = "",
    priority: str = "medium",
    status: str = "todo",
) -> dict[str, str]:
    """Validate and normalize task fields for persistence."""
    if not isinstance(title, str):
        raise ValueError("task title must be a string")
    normalized_title = title.strip()
    if not normalized_title:
        raise ValueError("task title cannot be empty")
    if len(normalized_title) > 120:
        raise ValueError("task title cannot exceed 120 characters")
    if not isinstance(description, str):
        raise ValueError("description must be a string")
    if len(description) > 1000:
        raise ValueError("description cannot exceed 1000 characters")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"invalid priority: {priority!r}")
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status!r}")

    return {
        "title": normalized_title,
        "description": description,
        "priority": priority,
        "status": status,
    }


def project_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a DB row representing a project into a JSON‑serialisable dict."""
    return {
        "id": row["id"],
        "name": row["name"],
        "created_at": row["created_at"],
    }


def task_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a DB row representing a task into a JSON‑serialisable dict."""
    return {
        "id": row["id"],
        "project_id": row["project_id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "priority": row["priority"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }