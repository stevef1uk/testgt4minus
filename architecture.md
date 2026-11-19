# Architecture for testgt4m

layout_root: taskboard

## Overview

TaskBoard is the local-only Python 3.11+ Kanban MVP defined by SPEC. It uses
FastAPI, built-in sqlite3, Jinja2 server-rendered HTML, and vanilla
JavaScript. It has no authentication, ORM, external service, frontend build,
background jobs, WebSockets, scheduler, Docker application, or credentials.
The documented server listens on 127.0.0.1:8080.

Database selection is the explicit create_app argument, then a nonempty
TASKBOARD_DB_PATH value, then taskboard/taskboard.db. Repository operations
open and close connections individually. Every connection enables foreign keys
and busy_timeout 5000. Initialization uses idempotent DDL and writes use
explicit transactions. DDL belongs only to taskboard/db.py; SQL access belongs
only to taskboard/repository.py; pure validation and row mapping belong to
taskboard/models.py; HTTP routes and dependency wiring belong to
taskboard/main.py; and browser behavior belongs to taskboard/static/app.js.

## Planned file layout

Every concrete SPEC and workflow-profile deliverable is listed with the
required taskboard/ prefix.
- `taskboard/pyproject.toml` — setuptools metadata and runtime/test dependencies.
- `taskboard/README.md` — installation, server, pytest, and browser instructions.
- `taskboard/.gitignore` — database, environment, cache, node_modules, and report exclusions.
- `taskboard/__init__.py` — importable package marker and metadata.
- `taskboard/main.py` — create_app, module app, request parsing, routes, and serving.
- `taskboard/db.py` — SQLite path handling, connection configuration, and DDL.
- `taskboard/models.py` — enum values, validation, and row-to-JSON mapping.
- `taskboard/repository.py` — parameterized project/task queries and transactions.
- `taskboard/templates/index.html` — forms, selector, filters, columns, and state regions.
- `taskboard/static/app.js` — API calls, state, safe rendering, controls, and filters.
- `taskboard/static/style.css` — responsive layout, cards, forms, and visual states.
- `taskboard/tests/conftest.py` — isolated temporary database and client fixtures.
- `taskboard/tests/test_repository.py` — persistence, ordering, filtering, update, and cascade tests.
- `taskboard/tests/test_api.py` — exact API, validation, status, and response-shape tests.
- `taskboard/tests/test_ui_content.py` — root and static-content integration tests.
- `taskboard/package.json` — Playwright development dependency only.
- `taskboard/package-lock.json` — matching generated npm lockfile.
- `taskboard/playwright.config.ts` — canonical host-server test configuration.
- `taskboard/playwright/taskboard.spec.ts` — three independent browser scenarios.

## Module / bead ownership

| File | Owns exported surface | Must not define |
|---|---|---|
| `taskboard/db.py` | connect(db_path: str) -> sqlite3.Connection; init_schema(db_path: str) -> None | routes or application queries |
| `taskboard/models.py` | VALID_STATUSES; VALID_PRIORITIES; validate_project_name(name: str) -> str; validate_task_fields(...); project_from_row(row) -> dict; task_from_row(row) -> dict | SQLite I/O or FastAPI objects |
| `taskboard/repository.py` | ProjectRepository; TaskRepository; list_projects() -> list[dict]; create_project(name: str) -> dict; delete_project(project_id: int) -> bool; list_tasks(project_id: int, status: str | None = None, priority: str | None = None) -> list[dict]; create_task(...) -> dict; update_task(task_id: int, changes: dict) -> dict | None; delete_task(task_id: int) -> bool | HTML, routes, or request parsing |
| `taskboard/main.py` | create_app(db_path: str | None = None) -> FastAPI; module-level app | SQL statements or browser state |
| `taskboard/__init__.py` | package metadata only | duplicate app construction |
| `taskboard/templates/index.html` | semantic forms, selector, filters, columns, empty/error regions | database calls or inline application logic |
| `taskboard/static/app.js` | browser API, rendering, filtering, editing, moving, and deletion | server validation or raw user-content HTML |
| `taskboard/static/style.css` | responsive presentation and visual states | application data or JavaScript behavior |
| `taskboard/tests/conftest.py` | temporary-path app and client fixtures | production behavior |
| `taskboard/tests/test_repository.py` | repository and persistence assertions | HTTP or browser assertions |
| `taskboard/tests/test_api.py` | API contract assertions | repository implementation or browser assertions |
| `taskboard/tests/test_ui_content.py` | rendered page and asset assertions | persistence implementation |
| `taskboard/playwright.config.ts` | host URL and browser configuration | application behavior |
| `taskboard/playwright/taskboard.spec.ts` | browser acceptance scenarios and cleanup | application source |

Repositories return the exact SPEC project and task JSON shapes. Names and
titles are trimmed and length-checked, descriptions are strings of at most
1000 Unicode code points, status and priority use the specified enums, IDs
sort ascending, timestamps carry explicit UTC offsets, and the
taskboard/tasks project_id foreign key cascades project deletion. SQL writes
are parameterized.

## HTTP + entrypoint integration

The exact routes are GET /api/health, GET and POST /api/projects, DELETE /api/projects/{project_id}, GET and POST /api/projects/{project_id}/tasks, PATCH and DELETE /api/tasks/{task_id}, GET /, and GET /static/app.js and /static/style.css. Health and lists return 200, creates 201, updates 200, and deletes 204 with an empty body. Application errors are {"error":"human-readable message"} with 400 or 404; malformed integer paths retain FastAPI 422 behavior.

create_app stores the selected path in app state, initializes the schema, and
passes that path to repositories rather than using a mutable global
connection. It mounts taskboard/static and renders taskboard/templates/index.html
as HTML. The module app supports
python -m uvicorn taskboard.main:app --host 127.0.0.1 --port 8080.
Creation ignores unknown properties and applies task defaults. PATCH accepts a
nonempty subset of title, description, priority, and status without project
reassignment. List filters validate independently and combine with AND.

## Unit tests

taskboard/tests/test_repository.py covers idempotent initialization, empty
lists, ascending IDs, defaults, UTC timestamps, status and priority filters
including conjunction, partial updates preserving omitted values, and project
cascade deletion. taskboard/tests/test_api.py covers exact health JSON,
project/task round trips, all specified 400 and 404 cases, invalid lengths and
enums, empty PATCH rejection, empty arrays, bodyless 204 deletes, composed
filters, and ID ordering. taskboard/tests/conftest.py supplies a fresh
temporary database per test and never touches taskboard/taskboard.db.
taskboard/tests/test_ui_content.py checks real TaskBoard HTML, both forms, all
three headings, and nonempty static responses.

## Integration and testing

Commands run from taskboard/. Ensure Python and Node dependencies are installed
before test review; test-review commands must not install packages. Phase 1 runs only the repository/API
pytest verification command. Phase 2 runs python -m pytest -q tests. Phase 3
runs the pytest suite and
./node_modules/.bin/playwright test --config playwright.config.ts playwright
against an already-running server at 127.0.0.1:8080. Browser assertions inspect real
task text and state changes, not placeholders or status codes alone. Unique
project names and cleanup make scenarios independent.

## E2E / integration testing

Only taskboard/playwright.config.ts and
taskboard/playwright/taskboard.spec.ts are canonical browser files. The
configuration targets the existing host server and creates no second
application or container. The scenarios check the real heading and columns,
create and move a task from todo through doing to done and delete it, and
filter two differently prioritized tasks before restoring both. Done cards
hide or disable Move forward.

## Delivery phases

```yaml
delivery_phases:
  - id: phase-1-core
    title: "Foundation and projects: core"
    spec_focus: Foundation and projects
    required_files:
      - taskboard/pyproject.toml
      - taskboard/README.md
      - taskboard/.gitignore
      - taskboard/__init__.py
      - taskboard/db.py
      - taskboard/models.py
      - taskboard/repository.py
      - taskboard/tests/test_repository.py
    qa_verify_command: "cd taskboard && python -m pytest -q tests/test_repository.py"
    depends_on: []
    file_dependencies:
      taskboard/repository.py: [taskboard/db.py, taskboard/models.py]
      taskboard/tests/test_repository.py: [taskboard/db.py, taskboard/models.py, taskboard/repository.py]
  - id: phase-1-app
    title: "Foundation and projects: runnable app"
    spec_focus: Foundation and projects
    required_files:
      - taskboard/main.py
      - taskboard/templates/index.html
      - taskboard/static/app.js
      - taskboard/static/style.css
      - taskboard/tests/conftest.py
      - taskboard/tests/test_api.py
    qa_verify_command: "cd taskboard && python -m pytest -q tests"
    depends_on: [phase-1-core]
    file_dependencies:
      taskboard/main.py: [taskboard/db.py, taskboard/models.py, taskboard/repository.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css]
      taskboard/tests/conftest.py: [taskboard/main.py]
      taskboard/tests/test_api.py: [taskboard/tests/conftest.py, taskboard/main.py]
  - id: phase-2
    title: Tasks and Kanban UI
    spec_focus: Tasks and Kanban UI
    required_files:
      - taskboard/tests/test_ui_content.py
      - taskboard/templates/index.html
      - taskboard/static/app.js
      - taskboard/static/style.css
      - taskboard/tests/conftest.py
      - taskboard/tests/test_repository.py
      - taskboard/tests/test_api.py
    qa_verify_command: "cd taskboard && python -m pytest -q tests"
    depends_on: [phase-1-app]
    file_dependencies:
      taskboard/tests/test_ui_content.py: [taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css]
  - id: phase-3
    title: Filters, browser tests, and release check
    spec_focus: Filters, browser tests, and release check
    required_files:
      - taskboard/package.json
      - taskboard/package-lock.json
      - taskboard/playwright.config.ts
      - taskboard/playwright/taskboard.spec.ts
    qa_verify_command: "cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright"
    depends_on: [phase-2]
    file_dependencies:
      taskboard/playwright.config.ts: [taskboard/package.json]
      taskboard/playwright/taskboard.spec.ts: [taskboard/package.json, taskboard/package-lock.json, taskboard/playwright.config.ts, taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css]
```

The machine-readable contract uses repository-root taskboard/ paths,
matching the workflow profile and planned layout. The Foundation and projects
SPEC phase is implemented in two dependent subphases to respect the ten-file
limit: phase-1-core owns the package metadata, documentation, database,
models, repository, and repository tests; phase-1-app owns the runnable app,
HTML/static assets, fixtures, and API tests. Both retain the original SPEC
focus. tasks-and-kanban-ui owns `taskboard/tests/test_ui_content.py`; and
filters-browser-tests-and-release-check owns
`taskboard/playwright/taskboard.spec.ts` (with its configuration and npm
manifests). Phase-1-app creates the initial runnable foundation and verifies
the repository and API tests. Phase 2 extends those canonical files in place
and adds the content test for task and Kanban behavior. Phase 3 adds the
Playwright manifest, generated lockfile, configuration, and scenarios while
completing filters. The graph is acyclic, each profile deliverable has an
explicit phase owner, and each dependency key is owned by its declaring phase.

**Delivery ownership cross-check**

The foundation-and-projects SPEC scope is split between phase-1-core and phase-1-app. Together they own the package metadata, documentation, ignore rules, package marker, app, database, models, repository, template, static assets, fixtures, and repository/API tests. The tasks-and-kanban-ui phase owns the newly introduced `taskboard/tests/test_ui_content.py` and extends the already-owned application files in place; it does not create alternate copies. The filters-browser-tests-and-release-check phase owns `taskboard/package.json`, `taskboard/package-lock.json`, `taskboard/playwright.config.ts`, and `taskboard/playwright/taskboard.spec.ts`. Its browser spec consumes the existing application and canonical static paths. Thus every literal profile required_files entry has exactly one first-delivery phase owner, while later phases may extend earlier-owned files as required by SPEC.

## Requirements

### phase-1-core

Deliver package metadata, documentation, ignore rules, package marker, schema,
models, repository, and repository tests. Use idempotent DDL, foreign keys,
busy_timeout 5000, UTC timestamps, projects and tasks tables, the
taskboard/tasks project_id index, and parameterized writes. Install the package
and run the isolated repository tests.

### phase-1-app

Deliver the app factory, health/project routes, real root HTML/static mounting,
fixtures, and API tests. Verify exact health JSON, project CRUD, real HTML, and
static delivery while preserving the Phase-1-core repository tests.

### phase-2

Extend the Phase 1 application in place with task repository operations,
task routes, validation, project selection, task creation/edit/delete,
three Kanban columns, move-forward behavior, and visible empty/error states.
Add taskboard/tests/test_ui_content.py and preserve all Phase 1 assertions.
The phase gate proves real create, move, edit, and delete state changes.

### phase-3

Complete status and priority filters and full pytest coverage. Add the
Playwright manifest, matching generated lockfile, host configuration, and
three independent scenarios under taskboard/playwright/. Ensure Node
dependencies are installed before test review; the release verification runs pytest and
the specified already-installed Playwright suite against 127.0.0.1:8080. No
extra routes, aliases, deployment mechanism, or
out-of-scope dependency is introduced.

## Acceptance mapping

The architecture maps every SPEC goal to ordered phase gates. SQLite
persistence, schema invariants, and cascade behavior are owned by
taskboard/db.py and taskboard/repository.py. Validation and JSON mapping are
isolated in taskboard/models.py. Exact routes, status codes, errors, database
selection, and app wiring are owned by taskboard/main.py. Real markup and
safe browser behavior are owned by taskboard/templates/index.html,
taskboard/static/app.js, and taskboard/static/style.css. Repository, API,
content, and browser tests provide behavioral evidence. Every profile path is
listed with taskboard/ prefix, ownership is explicit, dependencies are
ordered, and forbidden scope is absent.
