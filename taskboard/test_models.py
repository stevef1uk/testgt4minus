from __future__ import annotations

import pytest

from models import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    project_from_row,
    project_to_dict,
    task_from_row,
    task_to_dict,
    validate_project_name,
    validate_task_fields,
)


def test_validation_exports_match_spec():
    assert VALID_STATUSES == frozenset({"todo", "doing", "done"})
    assert VALID_PRIORITIES == frozenset({"low", "medium", "high"})
    assert validate_project_name("  Alpha  ") == "Alpha"
    with pytest.raises(ValueError):
        validate_project_name(" ")
    with pytest.raises(ValueError):
        validate_project_name("x" * 101)


def test_validate_task_fields_normalizes_and_rejects_invalid_values():
    values = validate_task_fields(
        title="  Ship it ",
        description="details",
        status="doing",
        priority="high",
    )
    assert values == {
        "title": "Ship it",
        "description": "details",
        "status": "doing",
        "priority": "high",
    }
    with pytest.raises(ValueError):
        validate_task_fields(title="", description="", status="todo", priority="medium")
    with pytest.raises(ValueError):
        validate_task_fields(title="x", description="", status="in_progress", priority="medium")


def test_row_mappings_match_schema_without_extraneous_fields():
    project = project_from_row({"id": 1, "name": "Alpha", "created_at": "now"})
    assert project_to_dict(project) == {"id": 1, "name": "Alpha", "created_at": "now"}

    task = task_from_row({
        "id": 2,
        "project_id": 1,
        "title": "Ship",
        "description": "details",
        "status": "doing",
        "priority": "high",
        "created_at": "now",
        "updated_at": "later",
    })
    assert task_to_dict(task) == {
        "id": 2,
        "project_id": 1,
        "title": "Ship",
        "description": "details",
        "status": "doing",
        "priority": "high",
        "created_at": "now",
        "updated_at": "later",
    }