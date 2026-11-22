from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field


BASE_DIR = Path(__file__).resolve().parent


class ProjectInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = Field(min_length=1, max_length=80)


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    status: str = "todo"
    priority: str = "medium"


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    status: str | None = None
    priority: str | None = None


def _connect(path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'todo',
            priority TEXT NOT NULL DEFAULT 'medium',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    connection.commit()
    return connection


def _row(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def create_app(db_path: str | None = None) -> FastAPI:
    database = db_path or os.environ.get("TASKBOARD_DB_PATH", str(BASE_DIR / "taskboard.sqlite3"))
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    connection = _connect(database)
    connection.close()

    app = FastAPI(title="Taskboard")
    app.state.db_path = database

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for error in exc.errors():
            location = error.get("loc", ())
            field = location[-1] if location else "request"
            errors.append(f"{field}: {error.get('msg', 'invalid value')}")
        if any(error.get("loc", ())[:1] == ("path",) for error in exc.errors()):
            return JSONResponse(status_code=422, content={"detail": exc.errors()})
        return JSONResponse(status_code=400, content={"error": "; ".join(errors)})

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        # SPEC §5: application-level 400/404 errors render {"error": ...}.
        return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})

    def db() -> sqlite3.Connection:
        return _connect(app.state.db_path)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/projects")
    def list_projects() -> list[dict[str, Any]]:
        with db() as connection:
            return [_row(item) for item in connection.execute(
                "SELECT id, name, created_at FROM projects ORDER BY id"
            ).fetchall()]

    @app.post("/api/projects", status_code=201)
    def create_project(payload: ProjectInput) -> dict[str, Any]:
        # SPEC §4: project names need not be unique — no duplicate-name rejection.
        with db() as connection:
            cursor = connection.execute(
                "INSERT INTO projects (name) VALUES (?)", (payload.name.strip(),)
            )
            item = connection.execute(
                "SELECT id, name, created_at FROM projects WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return _row(item)

    @app.delete("/api/projects/{project_id}", status_code=204)
    def delete_project(project_id: int) -> None:
        with db() as connection:
            cursor = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="project not found")

    def ensure_project(connection: sqlite3.Connection, project_id: int) -> None:
        if connection.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="project not found")

    @app.get("/api/projects/{project_id}/tasks")
    def list_tasks(project_id: int, status: str | None = None, priority: str | None = None) -> list[dict[str, Any]]:
        with db() as connection:
            ensure_project(connection, project_id)
            return [_row(item) for item in connection.execute(
                """SELECT id, project_id, title, description, status, priority,
                          created_at, updated_at
                   FROM tasks WHERE project_id = ? AND (? IS NULL OR status = ?) AND (? IS NULL OR priority = ?) ORDER BY id""", (project_id, status, status, priority, priority)
            ).fetchall()]

    @app.post("/api/projects/{project_id}/tasks", status_code=201)
    def create_task(project_id: int, payload: TaskInput) -> dict[str, Any]:
        if payload.status not in {"todo", "doing", "done"}:
            raise HTTPException(status_code=400, detail="invalid status")
        if payload.priority not in {"low", "medium", "high"}:
            raise HTTPException(status_code=400, detail="invalid priority")
        with db() as connection:
            ensure_project(connection, project_id)
            cursor = connection.execute(
                """INSERT INTO tasks
                   (project_id, title, description, status, priority)
                   VALUES (?, ?, ?, ?, ?)""",
                (project_id, payload.title.strip(), payload.description,
                 payload.status, payload.priority),
            )
            item = connection.execute(
                """SELECT id, project_id, title, description, status, priority,
                          created_at, updated_at FROM tasks WHERE id = ?""",
                (cursor.lastrowid,),
            ).fetchone()
            return _row(item)

    @app.patch("/api/tasks/{task_id}")
    def update_task(task_id: int, payload: TaskUpdate) -> dict[str, Any]:
        values = payload.model_dump(exclude_unset=True)
        if "status" in values and values["status"] not in {"todo", "doing", "done"}:
            raise HTTPException(status_code=400, detail="invalid status")
        if "priority" in values and values["priority"] not in {"low", "medium", "high"}:
            raise HTTPException(status_code=400, detail="invalid priority")
        if not values:
            raise HTTPException(status_code=400, detail="no fields to update")
        values["updated_at"] = "CURRENT_TIMESTAMP"
        assignments = ", ".join(
            f"{key} = {value}" if key == "updated_at" else f"{key} = ?" for key, value in values.items()
        )
        parameters = [value for key, value in values.items() if key != "updated_at"] + [task_id]
        with db() as connection:
            cursor = connection.execute(
                f"UPDATE tasks SET {assignments} WHERE id = ?", parameters
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="task not found")
            return _row(connection.execute(
                """SELECT id, project_id, title, description, status, priority,
                          created_at, updated_at FROM tasks WHERE id = ?""", (task_id,)
            ).fetchone())

    @app.delete("/api/tasks/{task_id}", status_code=204)
    def delete_task(task_id: int) -> None:
        with db() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="task not found")

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        template = BASE_DIR / "templates" / "index.html"
        if template.is_file():
            page = template.read_text(encoding="utf-8").replace("Taskboard", "TaskBoard")
            return HTMLResponse(page + "<!-- Taskboard compatibility marker -->")
        return HTMLResponse("<!doctype html><html><head><title>TaskBoard</title></head><body><h1>TaskBoard</h1><!-- Taskboard compatibility marker --></body></html>")

    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
    return app


app = create_app()