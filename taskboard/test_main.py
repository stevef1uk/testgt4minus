from __future__ import annotations

from taskboard.main import create_app


def test_task_mutation_routes_are_not_project_scoped(tmp_path):
    app = create_app(str(tmp_path / "tasks.sqlite3"))
    paths = {route.path for route in app.routes}
    assert "/api/tasks/{task_id}" in paths
    assert "/api/projects/{project_id}/tasks/{task_id}" not in paths