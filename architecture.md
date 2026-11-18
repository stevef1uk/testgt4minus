# Architecture for testgt4minus

layout_root: taskboard

## Overview

TaskBoard is a local-only Python 3.12 Kanban MVP matching the SPEC: FastAPI,
built-in sqlite3, Jinja2 server-rendered HTML, and vanilla JavaScript. It has
no authentication, ORM, external service, frontend compilation, background
jobs, WebSockets, or containerized application. SQLite schema initialization is
idempotent, repository operations open and close connections per operation, and
the default database is taskboard.db in the repository working directory unless
an explicit path or nonempty TASKBOARD_DB_PATH is supplied.

DDL belongs only to taskboard/db.py, SQL and transactions to
taskboard/repository.py, pure validation and row mapping to taskboard/models.py,
HTTP routes and dependency wiring to taskboard/main.py, and browser behavior to
taskboard/static/app.js. The root route renders taskboard/templates/index.html
and serves taskboard/static/app.js and taskboard/static/style.css. User values
are rendered with DOM textContent and never raw HTML.

## Planned file layout

Every concrete SPEC and workflow-profile deliverable is listed.
- `taskboard/pyproject.toml` — package metadata and runtime/test dependencies.
- `taskboard/README.md` — setup, server, pytest, and browser-test instructions.
- `taskboard/.gitignore` — database, environment, cache, and report exclusions.
- `taskboard/__init__.py` — importable package marker and metadata.
- `taskboard/main.py` — create_app, module app, request parsing, routes, and template serving.
- `taskboard/db.py` — SQLite connection setup and idempotent schema DDL.
- `taskboard/models.py` — enum constants, validation, and row mapping.
- `taskboard/repository.py` — parameterized project/task queries and transactions.
- `taskboard/templates/index.html` — TaskBoard forms, selector, columns, and states.
- `taskboard/static/app.js` — browser API calls, state, rendering, filters, and controls.
- `taskboard/static/style.css` — responsive layout and visual states.
- `taskboard/package.json` and `taskboard/package-lock.json` — pinned Playwright test-runner dependencies only; no application build.
- `taskboard/tests/conftest.py` — isolated temporary database and client fixtures.
- `taskboard/tests/test_api.py` — API contract, validation, ordering, and status tests.
- `taskboard/tests/test_repository.py` — persistence, filtering, update, and cascade tests.
- `taskboard/tests/test_ui_content.py` — root and static-content integration tests.
- `taskboard/playwright.config.ts` — host-server Playwright configuration.
- `taskboard/playwright/taskboard.spec.ts` — three independent browser scenarios.

## Module / bead ownership

| File | Owns exported surface | Must not define |
|---|---|---|
| `taskboard/db.py` | `connect(db_path: str) -> sqlite3.Connection`; `init_schema(db_path: str) -> None` | HTTP routes or application queries |
| `taskboard/models.py` | `VALID_STATUSES`; `VALID_PRIORITIES`; `validate_project_name`; `validate_task_fields`; `project_from_row`; `task_from_row` | SQLite I/O or FastAPI objects |
| `taskboard/repository.py` | `ProjectRepository`; `TaskRepository`; `list_projects() -> list[dict]`; `create_project(name: str) -> dict`; `delete_project(project_id: int) -> bool`; `list_tasks(project_id: int, status: str | None = None, priority: str | None = None) -> list[dict]`; `create_task(...) -> dict`; `update_task(task_id: int, changes: dict) -> dict | None`; `delete_task(task_id: int) -> bool` | HTML, routes, or request parsing |
| `taskboard/main.py` | `create_app(db_path: str | None = None) -> FastAPI`; module-level `app` | SQL statements or browser state |
| `taskboard/__init__.py` | package metadata only | duplicate app construction |
| `taskboard/templates/index.html` | semantic forms, selector, three columns, empty/error regions | database calls or inline application logic |
| `taskboard/static/app.js` | browser API, rendering, filtering, and controls | server validation or raw user-content HTML |
| `taskboard/static/style.css` | responsive presentation and visual states | application data or JavaScript behavior |
| `taskboard/tests/conftest.py` | temporary-path app and client fixtures | production behavior |
| `taskboard/tests/test_repository.py` | repository and persistence assertions | HTTP or browser assertions |
| `taskboard/tests/test_api.py` | API contract assertions | repository implementation or browser assertions |
| `taskboard/tests/test_ui_content.py` | rendered page and nonempty asset assertions | persistence implementation |
| `taskboard/playwright/taskboard.spec.ts` | browser acceptance scenarios | application source |

Repository methods return the exact project and task JSON shapes from the SPEC.
Names and titles are trimmed and length-checked, descriptions are strings up
to 1000 characters, IDs are ascending, timestamps have explicit UTC offsets,
foreign keys cascade project deletion, and all writes use parameterized SQL.

## HTTP + entrypoint integration

The exact route surface is GET `/api/health`; GET and POST `/api/projects`;
DELETE `/api/projects/{project_id}`; GET and POST
`/api/projects/{project_id}/tasks`; PATCH and DELETE `/api/tasks/{task_id}`;
GET `/`; and static GET requests for `/static/app.js` and `/static/style.css`.
Health and lists return 200, creates 201, PATCH 200, and deletes 204 with an
empty body. Application failures are `{"error":"human-readable message"}` with
400 or 404. Malformed integer paths retain FastAPI 422 behavior.

create_app chooses the explicit database path, then nonempty
TASKBOARD_DB_PATH, then taskboard.db, stores the selected string in app state,
initializes the schema, and wires repositories around per-operation
connections. It registers StaticFiles and renders the template. The module
app supports `python -m uvicorn taskboard.main:app --host 127.0.0.1 --port 8080`.
Create payloads ignore unknown properties and apply defaults. Patch accepts only
a nonempty subset of title, description, priority, and status; null values,
client IDs, timestamps, and project reassignment are rejected. Query filters
validate independently and combine with AND.

## Unit tests

taskboard/tests/test_repository.py covers idempotent startup, empty lists,
ascending IDs, defaults, UTC timestamps, status and priority filters including
their conjunction, partial updates, and project cascade deletion.
taskboard/tests/test_api.py covers exact health JSON, project/task round trips,
all specified 400/404 cases, invalid lengths and enums, filter ordering, empty
arrays, and bodyless 204 deletes. taskboard/tests/conftest.py uses a fresh
temporary database per test and never touches the runtime database.
taskboard/tests/test_ui_content.py checks real TaskBoard markup, forms, all
three headings, and nonempty static responses.

## Integration and testing

Run all project commands from `taskboard/`. Phases 1 and 2 use
`python -m pytest -q tests`; Phase 1 first installs the editable package and
test dependencies with `python -m pip install -e '.[test]'`. Phase 3 runs
`python -m pytest -q tests && npm install --ignore-scripts && npx playwright test --config playwright.config.ts playwright`
against an already-running server at 127.0.0.1:8080. Browser scenarios use
unique project names and clean their own rows. Assertions inspect real task
text, state transitions, filtering, and deletion rather than only status codes.

## E2E / integration testing

taskboard/playwright/taskboard.spec.ts verifies initial heading and
columns, browser creation and todo-to-doing-to-done movement followed by
deletion, and high-priority filtering with reset. taskboard/playwright.config.ts
targets the existing host server and creates no second application or
container. Done cards hide or disable Move forward.

## Delivery phases

```yaml
delivery_phases:
  - id: foundation-and-projects
    title: Foundation and projects
    spec_focus: Foundation and projects
    required_files:
      - taskboard/pyproject.toml
      - taskboard/README.md
      - taskboard/.gitignore
      - taskboard/__init__.py
      - taskboard/main.py
      - taskboard/db.py
      - taskboard/models.py
      - taskboard/repository.py
      - taskboard/tests/conftest.py
      - taskboard/tests/test_api.py
      - taskboard/tests/test_repository.py
      - taskboard/templates/index.html
      - taskboard/static/app.js
      - taskboard/static/style.css
    qa_verify_command: "cd taskboard && python -m pip install -e '.[test]' && python -m pytest -q tests"
    depends_on: []
    file_dependencies:
      taskboard/repository.py: [taskboard/db.py, taskboard/models.py]
      taskboard/main.py: [taskboard/db.py, taskboard/models.py, taskboard/repository.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css]
      taskboard/tests/conftest.py: [taskboard/main.py]
      taskboard/tests/test_api.py: [taskboard/tests/conftest.py, taskboard/main.py]
      taskboard/tests/test_repository.py: [taskboard/db.py, taskboard/models.py, taskboard/repository.py]
      taskboard/tests/test_ui_content.py: [taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css]
  - id: tasks-and-kanban-ui
    title: Tasks and Kanban UI
    spec_focus: Tasks and Kanban UI
    required_files:
      - taskboard/tests/test_ui_content.py
    qa_verify_command: "cd taskboard && python -m pytest -q tests"
    depends_on: [foundation-and-projects]
    file_dependencies:
      taskboard/tests/test_ui_content.py: [taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css]
  - id: filters-browser-tests-and-release-check
    title: Filters, browser tests, and release check
    spec_focus: Filters, browser tests, and release check
    required_files:
      - taskboard/playwright.config.ts
      - taskboard/playwright/taskboard.spec.ts
      - taskboard/package.json
      - taskboard/package-lock.json
    qa_verify_command: "cd taskboard && python -m pytest -q tests && npm install --ignore-scripts && npx playwright test --config playwright.config.ts playwright"
    depends_on: [tasks-and-kanban-ui]
    file_dependencies:
      taskboard/playwright/taskboard.spec.ts: [taskboard/playwright.config.ts, taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css]
```

Phase 1 owns the runnable foundation and all prerequisites required by its
SPEC exit criteria. Phase 2 owns the in-place task and Kanban continuation and
content-test continuation. Phase 3 owns the canonical browser tests, filter
evidence, and final release verification.
Every profile-declared concrete path has an owner and dependencies are acyclic.

## Requirements

### foundation-and-projects

Deliver package metadata, README, ignore rules, package, schema, repositories,
app factory, health/project routes, real root HTML/static mounting, and isolated
tests. Use idempotent DDL, foreign keys, busy_timeout 5000, UTC timestamps,
projects/tasks tables, and the tasks.project_id index. The phase command proves
exact health JSON, project CRUD, real HTML, and static delivery.

### tasks-and-kanban-ui

Extend the application with task repository operations, task routes,
validation, project selection, task creation/edit/delete, Kanban columns, and
todo-to-doing-to-done controls. Preserve Phase 1 contracts and test isolation.
Expanded tests prove defaults, filters, partial updates, invalid fields, missing
resources, cascade behavior, exact responses, and rendered forms. Acceptance
demonstrates create, move, edit, and delete through the real UI.

### filters-browser-tests-and-release-check

Complete status and priority filters, visible empty and error states, complete
pytest coverage, and three independent Playwright scenarios. The release
command runs pytest and the specified Playwright command against 127.0.0.1:8080.
No duplicate aliases, routes, or deployment mechanisms are needed.

## Acceptance mapping

The architecture maps every SPEC goal to a concrete module and phase gate.
SQLite invariants and persistence are in taskboard/db.py and
taskboard/repository.py; validation and mapping are in taskboard/models.py;
HTTP contracts are in taskboard/main.py; and the browser workflow is in
taskboard/templates/index.html, taskboard/static/app.js, and
taskboard/static/style.css. Every profile-required path has phase ownership,
dependencies are acyclic, all phases are testable, and acceptance checks cover
persistence, rendering, filtering, and real browser state changes without
adding out-of-scope capability.
