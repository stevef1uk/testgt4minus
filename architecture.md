# Architecture for testgt4m

layout_root: taskboard

## Overview

TaskBoard is a local-only Python 3.11+ Kanban MVP built with FastAPI,
sqlite3, Jinja2, and vanilla browser JavaScript. It persists projects and
tasks, supports the three Kanban states, task editing, filtering, deletion,
and project cascade deletion. It has no authentication, ORM, external
services, frontend compilation, Docker application, background jobs, or
alternate deployment architecture.

The package is rooted at taskboard/. Database selection is explicit
create_app(db_path), then nonempty TASKBOARD_DB_PATH, then the SPEC fallback
taskboard/taskboard.db. Connections open and close per repository operation,
enable foreign keys and busy_timeout 5000, and writes use explicit
transactions. Schema DDL belongs only to taskboard/db.py; SQL access belongs
only to taskboard/repository.py; validation and row mapping belong to
taskboard/models.py; HTTP wiring belongs to taskboard/main.py; and browser
behavior belongs to taskboard/static/app.js.

The API contract matches SPEC exactly: GET /api/health, GET /api/projects,
POST /api/projects, DELETE /api/projects/{project_id},
GET /api/projects/{project_id}/tasks,
POST /api/projects/{project_id}/tasks, PATCH /api/tasks/{task_id}, and
DELETE /api/tasks/{task_id}. API success codes are 200 for health, lists, and
updates, 201 for creates, and 204 with an empty body for deletes. Application
errors use the specified error object and 400 or 404; malformed integer paths
retain FastAPI 422 behavior. The server-rendered page is the single-page UI
and taskboard/static/app.js plus taskboard/static/style.css are served through
the specified static paths.

## Planned file layout

Every concrete SPEC deliverable is listed with the taskboard/ prefix:
- `taskboard/pyproject.toml` — setuptools metadata and runtime/test dependencies.
- `taskboard/README.md` — installation, server, test, and browser instructions.
- `taskboard/.gitignore` — databases, caches, environments, node_modules, and reports.
- `taskboard/__init__.py` — importable package marker.
- `taskboard/main.py` — app factory, API routes, page rendering, and static mounting.
- `taskboard/db.py` — path handling, connection setup, and idempotent DDL.
- `taskboard/models.py` — validation constants and row-to-JSON mapping.
- `taskboard/repository.py` — parameterized project/task queries and transactions.
- `taskboard/templates/index.html` — project/task forms, filters, columns, and status regions.
- `taskboard/static/app.js` — browser API calls, state, safe rendering, and controls.
- `taskboard/static/style.css` — responsive taskboard presentation.
- `taskboard/tests/conftest.py` — isolated temporary database fixtures.
- `taskboard/tests/test_repository.py` — persistence and repository behavior tests.
- `taskboard/tests/test_api.py` — API contract and validation tests.
- `taskboard/tests/test_ui_content.py` — rendered page and static-content tests.
- `taskboard/package.json` — Playwright development dependency.
- `taskboard/package-lock.json` — generated matching npm lockfile.
- `taskboard/playwright.config.ts` — host-server Playwright configuration.
- `taskboard/playwright/taskboard.spec.ts` — independent browser scenarios.

## Module / bead ownership

| File | Owns | Must not define |
|---|---|---|
| `taskboard/db.py` | connect(db_path: str) -> sqlite3.Connection; init_schema(db_path: str) -> None | HTTP routes or query policy |
| `taskboard/models.py` | VALID_STATUSES; VALID_PRIORITIES; project/task validators and row mappers | SQLite or FastAPI objects |
| `taskboard/repository.py` | ProjectRepository; TaskRepository; project/task CRUD and filtered list operations | HTML, routes, or request parsing |
| `taskboard/main.py` | create_app(db_path: str \| None = None) -> FastAPI; module app | SQL statements or browser state |
| `taskboard/templates/index.html` | semantic forms, selectors, columns, and message regions | database calls or inline application logic |
| `taskboard/static/app.js` | loading, creating, editing, moving, filtering, deleting, and safe DOM rendering | server validation |
| `taskboard/static/style.css` | page, form, card, column, status, and responsive styling | application data or behavior |
| `taskboard/tests/conftest.py` | temporary-path app/client fixtures | production implementation |
| `taskboard/tests/test_repository.py` | repository assertions | HTTP or browser assertions |
| `taskboard/tests/test_api.py` | API assertions | repository implementation |
| `taskboard/tests/test_ui_content.py` | HTML and static asset assertions | persistence implementation |
| `taskboard/playwright.config.ts` | host URL and browser settings | application behavior |
| `taskboard/playwright/taskboard.spec.ts` | browser acceptance and cleanup | application source |

Repositories return the exact project and task JSON shapes from SPEC. Project
names and task titles are trimmed and length checked. Descriptions preserve
content subject to the specified limit. Status and priority use only the
specified enums, IDs are ascending, timestamps have explicit UTC offsets, and
the taskboard/tasks project_id foreign key cascades project deletion.

## HTTP + entrypoint integration

taskboard/main.py creates the FastAPI application, resolves the database path,
initializes the schema, stores the selected path in app state, creates
repositories per request, mounts taskboard/static, and renders
taskboard/templates/index.html. It exports app for the documented uvicorn
command. The API route set is exactly GET /api/health, GET /api/projects,
POST /api/projects, DELETE /api/projects/{project_id},
GET /api/projects/{project_id}/tasks,
POST /api/projects/{project_id}/tasks, PATCH /api/tasks/{task_id}, and
DELETE /api/tasks/{task_id}. No single-project GET or PUT route is added.
The page and static resources are delivered as specified without additional
API aliases.

Project creation validates name and returns 201. Task creation verifies the
project, applies the specified defaults, and returns 201. Task listing checks
status and priority filters independently and combines them with AND. Task
patching accepts a nonempty subset of title, description, priority, and
status, never changes project ownership, and returns 200. Missing resources
return 404; invalid application fields return the specified 400 error object;
deletes return 204 with no body.

## Unit tests

Phase-1 repository validation is owned by `taskboard/tests/test_repository.py` and must assert the SPEC boundaries, not merely exercise successful persistence. It covers a project name of 80 characters as accepted and 81 characters as rejected, a task title of 120 characters as accepted and 121 characters as rejected, and a description at the SPEC-defined maximum as accepted and an overlong description as rejected. The same suite must assert that an unknown task status and an unknown task priority are rejected with the repository validation error, while valid status and priority values persist and round-trip. These assertions are part of the phase-1-core exit gate and must remain in the active test file.

taskboard/tests/test_repository.py proves idempotent schema initialization,
empty lists, deterministic project ordering, task defaults and timestamps,
status/priority filters including conjunction, partial updates preserving
omitted values, and project cascade deletion.

taskboard/tests/test_api.py proves exact health JSON, project and task
round trips, all specified validation failures, missing-resource behavior,
empty PATCH rejection, empty arrays, bodyless deletes, composed filters, and
ID ordering. taskboard/tests/conftest.py gives each test an explicit temporary
database and prevents use of the runtime database.

taskboard/tests/test_ui_content.py proves the rendered page contains the
TaskBoard heading, project and task forms, all three column headings, and
nonempty responses from taskboard/static/app.js and
taskboard/static/style.css.

## Integration and testing

Run project checks from taskboard/. Install dependencies before review; review
commands themselves do not install packages. The core phase runs
python -m pytest -q tests/test_repository.py. The application and Kanban
phases run python -m pytest -q tests. The browser phase runs the pytest suite
and the canonical Playwright command against the already-running local server.
Assertions must prove state changes and rendered content, not merely status
codes or placeholder existence. Browser scenarios use unique project names
and clean up their created data.

## E2E / integration testing

taskboard/playwright.config.ts targets the existing host server and does not
start a second application or container. taskboard/playwright/taskboard.spec.ts
contains three independent scenarios: initial heading and columns; project
and task creation followed by todo-to-doing-to-done movement and deletion; and
two-priority filtering with reset. Assertions inspect real task text and
column state.

## Delivery phases

```yaml
delivery_phases:
  - id: phase-1-core
    title: "Foundation and projects: core"
    spec_focus: "Foundation and projects"
    required_files:
      - taskboard/pyproject.toml
      - taskboard/README.md
      - taskboard/.gitignore
      - taskboard/__init__.py
      - taskboard/db.py
      - taskboard/models.py
      - taskboard/repository.py
      - taskboard/tests/test_repository.py
    qa_verify_command: 'cd taskboard && python -m pytest -q tests/test_repository.py'
    depends_on: []
    file_dependencies:
      taskboard/repository.py: [taskboard/db.py, taskboard/models.py]
      taskboard/tests/test_repository.py: [taskboard/db.py, taskboard/models.py, taskboard/repository.py]
  - id: phase-1-app
    title: "Foundation and projects: runnable app"
    spec_focus: "Foundation and projects"
    required_files:
      - taskboard/main.py
      - taskboard/templates/index.html
      - taskboard/static/app.js
      - taskboard/static/style.css
      - taskboard/tests/conftest.py
      - taskboard/tests/test_api.py
    qa_verify_command: 'cd taskboard && python -m pytest -q tests'
    depends_on: [phase-1-core]
    file_dependencies:
      taskboard/main.py: [taskboard/db.py, taskboard/models.py, taskboard/repository.py]
      taskboard/tests/conftest.py: [taskboard/main.py]
      taskboard/tests/test_api.py: [taskboard/tests/conftest.py, taskboard/main.py]
  - id: phase-2
    title: "Tasks and Kanban UI"
    spec_focus: "Tasks and Kanban UI"
    required_files:
      - taskboard/tests/test_ui_content.py
      - taskboard/templates/index.html
      - taskboard/static/app.js
      - taskboard/static/style.css
      - taskboard/tests/test_repository.py
      - taskboard/tests/test_api.py
    qa_verify_command: 'cd taskboard && python -m pytest -q tests'
    depends_on: [phase-1-app]
    file_dependencies:
      taskboard/tests/test_ui_content.py: [taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css]
  - id: phase-3
    title: "Filters, browser tests, and release check"
    spec_focus: "Filters, browser tests, and release check"
    required_files:
      - taskboard/package.json
      - taskboard/package-lock.json
      - taskboard/playwright.config.ts
      - taskboard/playwright/taskboard.spec.ts
    qa_verify_command: 'cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright'
    depends_on: [phase-2]
    file_dependencies:
      taskboard/playwright.config.ts: [taskboard/package.json]
      taskboard/playwright/taskboard.spec.ts: [taskboard/package.json, taskboard/package-lock.json, taskboard/playwright.config.ts, taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css]
```

Phase 1 is split exactly as SPEC requires to keep each first-delivery set
under ten files. Phase 1 core establishes packaging, schema, models,
repository, and repository tests. Phase 1 app establishes the runnable
application, initial page and static assets, fixtures, and API tests. Phase 2
extends those canonical files and adds the UI-content test for task and Kanban
behavior. Phase 3 adds the generated npm files and canonical browser harness
while completing filters and release verification. Later phases may modify
earlier-owned files but do not create duplicates.

## Requirements

### phase-1-core

The phase-1-core test deliverable includes explicit negative assertions in `taskboard/tests/test_repository.py` for overlong descriptions using the SPEC-defined description maximum, the project-name limit of 80, the task-title limit of 120, and unknown status/priority values; a passing test count without those assertions is insufficient.

Deliver package metadata, documentation, ignore rules, package marker, schema,
models, repository operations, and repository tests. Use idempotent DDL,
foreign keys, the tasks project index, busy_timeout 5000, UTC timestamps, and
parameterized writes. Verify the repository tests after dependencies are
already installed.

### phase-1-app

Deliver the app factory, health and project API, real page rendering, static
mounting, isolated fixtures, and API tests. The app contract is limited to
GET /api/health, GET /api/projects, POST /api/projects,
DELETE /api/projects/{project_id}, and the rendered page/static resources.
Do not add single-project retrieval or update methods. Verify the full pytest
gate and real project CRUD behavior.

### phase-2

Extend the canonical application in place with task repository operations,
task routes, validation, project selection, task creation/edit/delete, three
Kanban columns, move-forward behavior, and visible empty/error states. Add
taskboard/tests/test_ui_content.py and preserve all earlier assertions. The
gate must demonstrate real create, move, edit, and delete state changes.

### phase-3

Complete status and priority filters and full pytest coverage. Add the
Playwright manifest, generated lockfile, host configuration, and three
independent browser scenarios. Verify pytest and the already-installed
Playwright suite against the local server. Introduce no extra routes, aliases,
deployment mechanism, or out-of-scope dependency.

## Acceptance mapping

The architecture maps SPEC goals to ordered phase gates. Persistence,
constraints, timestamps, and cascade behavior are owned by
taskboard/db.py and taskboard/repository.py. Validation and JSON mapping are
owned by taskboard/models.py. Exact API behavior and application wiring are
owned by taskboard/main.py. Real markup and safe browser behavior are owned by
taskboard/templates/index.html, taskboard/static/app.js, and
taskboard/static/style.css. Repository, API, content, and browser tests provide
behavioral evidence for every milestone, with all planned files assigned to a
concrete delivery phase.
