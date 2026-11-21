"""Domain models and row mappings for TaskBoard."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

STATUSES = ("todo", "in_progress", "done")
VALID_STATUSES = frozenset(STATUSES)


@dataclass(frozen=True, slots=True)
class Project:
    id: int
    name: str
    description: str
    created_at: str


@dataclass(frozen=True, slots=True)
class Task:
    id: int
    project_id: int
    title: str
    description: str
    status: str
    position: int
    created_at: str
    updated_at: str


def _value(row: Mapping[str, Any], key: str, default: Any = None) -> Any:
    return row[key] if key in row.keys() else default


def project_from_row(row: Mapping[str, Any]) -> Project:
    return Project(
        id=int(row["id"]),
        name=str(row["name"]),
        description=str(_value(row, "description", "")),
        created_at=str(_value(row, "created_at", "")),
    )


def task_from_row(row: Mapping[str, Any]) -> Task:
    return Task(
        id=int(row["id"]),
        project_id=int(row["project_id"]),
        title=str(row["title"]),
        description=str(_value(row, "description", "")),
        status=str(_value(row, "status", "todo")),
        position=int(_value(row, "position", 0)),
        created_at=str(_value(row, "created_at", "")),
        updated_at=str(_value(row, "updated_at", "")),
    )


def project_to_dict(project: Project) -> dict[str, Any]:
    return asdict(project)


def task_to_dict(task: Task) -> dict[str, Any]:
    return asdict(task)