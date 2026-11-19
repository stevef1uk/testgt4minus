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
        raise ValueError("project name must not be empty")
    if len(value) > 80:
        raise ValueError("project name must be at most 80 characters")
    return value


def validate_task_fields(
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    *,
    partial: bool = False,
) -> dict[str, str]:
    """Validate task fields and return normalized values."""
    validated: dict[str, str] = {}

    if title is not None:
        if not isinstance(title, str):
            raise ValueError("task title must be a string")
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("task title must not be empty")
        if len(normalized_title) > 120:
            raise ValueError("task title must be at most 120 characters")
        validated["title"] = normalized_title
    elif not partial:
        raise ValueError("task title is required")

    if description is not None:
        if not isinstance(description, str):
            raise ValueError("task description must be a string")
        if len(description) > 1000:
            raise ValueError("task description must be at most 1000 characters")
        validated["description"] = description
    elif not partial:
        validated["description"] = ""

    if status is not None:
        if status not in VALID_STATUSES:
            raise ValueError("invalid task status")
        validated["status"] = status

    if priority is not None:
        if priority not in VALID_PRIORITIES:
            raise ValueError("invalid task priority")
        validated["priority"] = priority
    elif not partial:
        validated["priority"] = "medium"

    return validated


def _value(row: Mapping[str, Any], key: str) -> Any:
    return row[key]


def project_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": _value(row, "id"),
        "name": _value(row, "name"),
        "created_at": _value(row, "created_at"),
    }


def task_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": _value(row, "id"),
        "project_id": _value(row, "project_id"),
        "title": _value(row, "title"),
        "description": _value(row, "description"),
        "status": _value(row, "status"),
        "priority": _value(row, "priority"),
        "created_at": _value(row, "created_at"),
        "updated_at": _value(row, "updated_at"),
    }