"""Domain models and row mappings for TaskBoard."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

VALID_STATUSES = frozenset({"todo", "doing", "done"})
VALID_PRIORITIES = frozenset({"low", "medium", "high"})


@dataclass(frozen=True, slots=True)
class Project:
    id: int
    name: str
    created_at: str


@dataclass(frozen=True, slots=True)
class Task:
    id: int
    project_id: int
    title: str
    description: str
    status: str
    priority: str
    created_at: str
    updated_at: str


def _value(row: Mapping[str, Any], key: str, default: Any = None) -> Any:
    return row[key] if key in row.keys() else default


def validate_project_name(name: str) -> str:
    value = str(name).strip()
    if not value:
        raise ValueError("project name is required")
    if len(value) > 100:
        raise ValueError("project name must be at most 100 characters")
    return value


def validate_task_fields(
    *,
    title: str,
    description: str,
    status: str,
    priority: str,
) -> dict[str, str]:
    clean_title = str(title).strip()
    clean_description = str(description).strip()
    if not clean_title:
        raise ValueError("task title is required")
    if len(clean_title) > 120:
        raise ValueError("task title must be 1-120 characters")
    if len(clean_description) > 1000:
        raise ValueError("task description must be at most 1000 characters")
    if status not in VALID_STATUSES:
        raise ValueError("invalid task status")
    if priority not in VALID_PRIORITIES:
        raise ValueError("invalid task priority")
    return {
        "title": clean_title,
        "description": clean_description,
        "status": status,
        "priority": priority,
    }


def project_from_row(row: Mapping[str, Any]) -> Project:
    return Project(
        id=int(row["id"]),
        name=str(row["name"]),
        created_at=str(_value(row, "created_at", "")),
    )


def task_from_row(row: Mapping[str, Any]) -> Task:
    return Task(
        id=int(row["id"]),
        project_id=int(row["project_id"]),
        title=str(row["title"]),
        description=str(_value(row, "description", "")),
        status=str(_value(row, "status", "todo")),
        priority=str(_value(row, "priority", "medium")),
        created_at=str(_value(row, "created_at", "")),
        updated_at=str(_value(row, "updated_at", "")),
    )


def project_to_dict(project: Project) -> dict[str, Any]:
    return asdict(project)


def task_to_dict(task: Task) -> dict[str, Any]:
    return asdict(task)