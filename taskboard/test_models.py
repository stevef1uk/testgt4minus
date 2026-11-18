from __future__ import annotations

import pytest

from taskboard.models import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    project_from_row,
    task_from_row,
    validate_project_name,
    validate_task_fields,
)


def test_validation_constants_match_supported_values():
    assert VALID_STATUSES == ("todo", "doing", "done")
    assert VALID_PRIORITIES == ("low", "medium", "high")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("  Website  ", "Website"), ("TaskBoard", "TaskBoard")],
)
def test_validate_project_name_strips_valid_names(raw, expected):
    assert validate_project_name(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", None])
def test_validate_project_name_rejects_invalid_names(raw):
    with pytest.raises(ValueError):
        validate_project_name(raw)


def test_validate_task_fields_normalizes_and_returns_all_fields():
    assert validate_task_fields(
        "  Build UI  ", "Description", "high", "doing"
    ) == {
        "title": "Build UI",
        "description": "Description",
        "priority": "high",
        "status": "doing",
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"title": ""},
        {"title": "Task", "priority": "urgent"},
        {"title": "Task", "status": "blocked"},
        {"title": "Task", "description": None},
    ],
)
def test_validate_task_fields_rejects_invalid_fields(kwargs):
    with pytest.raises(ValueError):
        validate_task_fields(**kwargs)


def test_project_from_row_maps_project_columns():
    row = {"id": 3, "name": "Roadmap", "created_at": "2024-01-01T00:00:00"}
    assert project_from_row(row) == row


def test_task_from_row_maps_task_columns():
    row = {
        "id": 4,
        "project_id": 3,
        "title": "Ship",
        "description": "Release it",
        "status": "todo",
        "priority": "medium",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }
    assert task_from_row(row) == row