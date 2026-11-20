from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from taskboard import db, repository

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
STATIC_DIR = BASE_DIR / "static"


def _error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


def create_app(db_path: str | None = None) -> FastAPI:
    selected_path = str(db.database_path(db_path))
    db.init_schema(selected_path)

    application = FastAPI(title="TaskBoard")
    application.state.db_path = selected_path
    application.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @application.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/")
    def index(request: Request):
        return TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={},
        )

    @application.get("/api/projects")
    def list_projects() -> list[dict[str, Any]]:
        return repository.list_projects(selected_path)

    @application.post("/api/projects", status_code=201)
    async def create_project(request: Request):
        try:
            payload = await request.json()
        except ValueError:
            return _error(400, "request body must be a JSON object")
        if not isinstance(payload, dict) or "name" not in payload:
            return _error(400, "project name is required")
        try:
            return repository.create_project(payload["name"], selected_path)
        except (TypeError, ValueError) as exc:
            return _error(400, str(exc))

    def project_exists(project_id: int) -> bool:
        return any(
            project["id"] == project_id
            for project in repository.list_projects(selected_path)
        )

    @application.get("/api/projects/{project_id}/tasks")
    def list_project_tasks(
        project_id: int,
        status: str | None = None,
        priority: str | None = None,
    ):
        if not project_exists(project_id):
            return _error(404, "project not found")
        try:
            return repository.list_tasks(
                project_id,
                status=status,
                priority=priority,
                db_path=selected_path,
            )
        except ValueError as exc:
            return _error(400, str(exc))

    @application.post("/api/projects/{project_id}/tasks", status_code=201)
    async def create_project_task(project_id: int, request: Request):
        if not project_exists(project_id):
            return _error(404, "project not found")
        try:
            payload = await request.json()
        except ValueError:
            return _error(400, "request body must be a JSON object")
        if not isinstance(payload, dict) or "title" not in payload:
            return _error(400, "task title is required")
        try:
            return repository.create_task(
                project_id,
                payload["title"],
                description=payload.get("description"),
                priority=payload.get("priority"),
                db_path=selected_path,
            )
        except (TypeError, ValueError) as exc:
            return _error(400, str(exc))
        except LookupError as exc:
            return _error(404, str(exc))



    @application.delete("/api/projects/{project_id}", status_code=204)
    def delete_project(project_id: int):
        if not repository.delete_project(project_id, selected_path):
            return _error(404, "project not found")
        return Response(status_code=204)

    @application.patch("/api/tasks/{task_id}")
    def patch_task(task_id: int, payload: dict):
        import sqlite3

        if "project_id" in payload:
            return JSONResponse(
                status_code=400,
                content={"error": "task project cannot be changed"},
            )

        allowed = {"title", "description", "status", "priority"}
        updates = {key: value for key, value in payload.items() if key in allowed}
        if "title" in updates:
            updates["title"] = str(updates["title"]).strip()
            if not updates["title"]:
                return JSONResponse(status_code=400, content={"error": "title is required"})
        if "status" in updates and updates["status"] not in {"todo", "doing", "done"}:
            return JSONResponse(status_code=400, content={"error": "invalid status"})
        if "priority" in updates and updates["priority"] not in {"low", "medium", "high"}:
            return JSONResponse(status_code=400, content={"error": "invalid priority"})

        with sqlite3.connect(selected_path) as connection:
            connection.row_factory = sqlite3.Row
            existing = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            if existing is None:
                return JSONResponse(status_code=404, content={"error": "task not found"})
            if updates:
                assignments = ", ".join(f"{key} = ?" for key in updates)
                connection.execute(
                    f"UPDATE tasks SET {assignments} WHERE id = ?",
                    [*updates.values(), task_id],
                )
                connection.commit()
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return dict(row)

    @application.delete("/api/tasks/{task_id}", status_code=204)
    def delete_task(task_id: int):
        if not repository.delete_task(task_id, selected_path):
            return _error(404, "task not found")
        return Response(status_code=204)

    return application


app = create_app()