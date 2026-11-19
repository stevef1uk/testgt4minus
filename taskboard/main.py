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

    @application.delete("/api/projects/{project_id}", status_code=204)
    def delete_project(project_id: int):
        if not repository.delete_project(project_id, selected_path):
            return _error(404, "project not found")
        return Response(status_code=204)

    return application


app = create_app()