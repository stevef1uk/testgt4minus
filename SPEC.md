# TaskBoard — Python Kanban MVP (Gas Town rig-flow test)

## 1. Goal

Implement a small, local-only task management web application called **TaskBoard**. A user can create projects, create tasks in a project, edit a task's title/description/priority, move tasks among three Kanban states, filter tasks, and delete tasks or projects. State is persisted in SQLite.

This specification deliberately sits between the Link Shelf MVP and FinAlly. Keep implementation small and literal: **Python + FastAPI + SQLite + server-rendered HTML + vanilla JavaScript**, no frontend build, no external service, and no authentication. The purpose is to exercise the Gas Town `rig-flow` architecture, planning, implementation, test_plan, test_review, and QA hand-offs in a moderately complex but reproducible project.

## 2. Fixed constraints

- Python >=3.11, target Python 3.12.
- Runtime dependencies: `fastapi`, `uvicorn`, `jinja2`; no ORM required.
- Test dependencies: `pytest`, `httpx`. Browser tests use Playwright through the host-network setup supported by Gas Town; do not create a second, independent containerized application.
- Use only Python's built-in `sqlite3` for persistence.
- Server listens on `127.0.0.1:8080` by default.
- No Dockerfile, Next.js, npm frontend compilation, SSE, WebSockets, schedulers, LLM calls, market data, background jobs, or external credentials.
- No auto-generated implementation artifacts checked in: `.venv/`, `*.db`, caches, `node_modules/`, or Playwright reports.
- The repository may initially contain only this SPEC.md; agents implement all other deliverables.
- Use explicitly defined routes and response shapes below; avoid additional architectures or features.

## 3. Project layout

The directory containing this `SPEC.md` is the rig/repository root.
`taskboard/` is the single Python project and workflow layout root. It contains
the package source, project metadata, documentation, tests, and Playwright
harness:

```text
SPEC.md
taskboard/
  pyproject.toml
  README.md
  .gitignore
  __init__.py
  main.py                 # create_app(db_path=None) and route registration
  db.py                   # connect, init_schema, DB path handling
  models.py               # validation and mapping helpers
  repository.py           # SQLite queries for projects and tasks
  package.json
  package-lock.json
  templates/
    index.html
  static/
    app.js
    style.css
  playwright/
    taskboard.spec.ts
  tests/
    conftest.py
    test_repository.py
    test_api.py
    test_ui_content.py
```

```

All paths in this specification are relative to the rig/repository root; run
project commands from `taskboard/`. Do not create another Python project at the
repository root. Configure the editable package so `taskboard.main` imports
correctly from the `taskboard/` working directory during tests and from the
repository root when starting the documented server command. Application code
lives under `taskboard/`; unit and browser tests live under
`taskboard/tests/`. Tests import `create_app` from `taskboard.main`. Put all
table DDL in `db.py`, all SQL data access in `repository.py`, all HTTP routes in
`main.py`, and all browser interactions in `static/app.js`. `models.py` holds
shared pure validation functions and row-to-JSON mapping helpers. Configure
setuptools to map the `taskboard` package to the project root and include
`templates/*.html` and `static/*` as package data. Avoid circular imports.

The only canonical Playwright paths are
`taskboard/playwright.config.ts` and
`taskboard/playwright/taskboard.spec.ts`. A host integration-test
scaffolder may seed these files, but Phase 3 must leave a
`taskboard/package.json` with `@playwright/test` as a development dependency
and a matching `taskboard/package-lock.json`. They are test-runner files only:
do not add application build scripts, duplicate config/spec files, path
aliases, symlinks, or wrapper deliverables to satisfy a generated profile.
Preserve a generated canonical config when present; otherwise create the
minimal compatible config in Phase 3. Do not create a second, containerized
application.

## 4. Data model and invariants

SQLite file is `taskboard.db` in the current working directory by default. Tests pass an explicit temporary file path. Each connection enables `PRAGMA foreign_keys = ON`; configure SQLite `busy_timeout` to 5000 ms. Initialize the schema once during app startup, using `CREATE TABLE IF NOT EXISTS`. There are no migrations in this MVP.

### projects

| Column | Type | Rules |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | NOT NULL, non-empty after trim, max 80 characters |
| created_at | TEXT | NOT NULL, UTC ISO 8601 timestamp |

Project names need not be unique.

### tasks

| Column | Type | Rules |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| project_id | INTEGER | NOT NULL, FOREIGN KEY REFERENCES projects(id) ON DELETE CASCADE |
| title | TEXT | NOT NULL, trimmed, 1–120 characters |
| description | TEXT | NOT NULL DEFAULT '', max 1000 characters |
| status | TEXT | NOT NULL, one of `todo`, `doing`, `done`, default `todo` |
| priority | TEXT | NOT NULL, one of `low`, `medium`, `high`, default `medium` |
| created_at | TEXT | NOT NULL, UTC ISO 8601 timestamp |
| updated_at | TEXT | NOT NULL, UTC ISO 8601 timestamp |

Create appropriate index on `tasks.project_id`. Task order within a status column is ascending ID; no drag-and-drop or custom ranking.

### Validations and rules

- Trim surrounding whitespace for project name and task title. Reject empty values after trim.
- Character lengths refer to Python Unicode code points (`len`), not UTF-8 bytes.
- Description is retained verbatim except it must be a string of at most 1000 characters; `null` and missing descriptions become `""` only on task creation.
- Reject unknown status/priority values with HTTP 400.
- Tasks always belong to an existing project. Creating a task with a non-existent project ID returns 404.
- Deleting a project cascades to its tasks.
- A missing project or task returns 404. A malformed integer path returns the framework's 422; no custom handler required.
- All timestamps have explicit UTC timezone (`Z` or `+00:00`). Tests must not assert exact wall-clock time.
- All write actions use parameterized SQL; never interpolate request data into SQL text.

## 5. API contract

The JSON error format for application-level 400/404 errors is `{ "error": "human-readable message" }`. FastAPI's default `422` response is permitted for schema/type validation failures. IDs are positive integers.

| Method | Path | Success response | Failure |
|---|---|---|---|
| GET | `/api/health` | 200 `{"status":"ok"}` | — |
| GET | `/api/projects` | 200 JSON array of projects ordered by `id ASC` | — |
| POST | `/api/projects` | 201 project object | 400 invalid name |
| DELETE | `/api/projects/{project_id}` | 204 empty body | 404 missing |
| GET | `/api/projects/{project_id}/tasks` | 200 array of matching tasks ordered by `id ASC` | 404 project missing; 400 invalid filter |
| POST | `/api/projects/{project_id}/tasks` | 201 task object | 404 project missing; 400 invalid fields |
| PATCH | `/api/tasks/{task_id}` | 200 updated task object | 404 missing; 400 invalid fields |
| DELETE | `/api/tasks/{task_id}` | 204 empty body | 404 missing |

### Project JSON

`{"id":1,"name":"Demo","created_at":"2026-01-01T00:00:00+00:00"}`

Project POST payload: `{"name":"Demo"}`. Unknown properties may be ignored.

### Task JSON

`{"id":1,"project_id":1,"title":"Build API","description":"Details","status":"todo","priority":"high","created_at":"2026-01-01T00:00:00+00:00","updated_at":"2026-01-01T00:00:00+00:00"}`

Task POST payload: `{"title":"Build API","description":"Details","priority":"high"}`. Optional description defaults to `""`, priority defaults to `medium`, and status is always `todo` on create. Extra properties may be ignored. Do not accept client-provided IDs or timestamps.

Task PATCH payload: any nonempty subset of `title`, `description`, `priority`, `status`. Missing fields remain unchanged. Explicit `null` is invalid for the fields being patched. Reject an empty PATCH payload with HTTP 400. Do not expose project reassignment in PATCH.

Task list accepts optional query parameters `status` and `priority`. Each must be a valid enum value when provided. Both filters combine with AND. An unfiltered list returns all tasks in the project; empty lists serialize as `[]`.

## 6. Application and UI contract

`taskboard.main.create_app(db_path: str | None = None) -> FastAPI` creates a working app with schema initialized for the selected database path. If `db_path` is None, use environment variable `TASKBOARD_DB_PATH` if present and nonempty, otherwise `taskboard.db`. Do not use an in-memory SQLite database in tests because each new connection would lose its schema.

Run with:

```bash
python -m uvicorn taskboard.main:app --host 127.0.0.1 --port 8080
```

Export a module-level `app = create_app()` for this command. HTTP handlers obtain the selected DB path from `app.state` (or an app-scoped dependency), not a mutable global DB connection. Connections open and close per repository operation; transaction boundaries for writes are explicit.

### Browser routes

- `GET /`: 200 server-rendered `taskboard/templates/index.html` containing a real TaskBoard page, not a fallback placeholder. Return content type `text/html`.
- `GET /static/app.js` and `GET /static/style.css`: serve the real files through FastAPI's StaticFiles.

### UI requirements

- Page heading `TaskBoard`.
- A project creation input and `Add project` button.
- A project selector/list populated by `/api/projects` on page load; selecting a project shows its tasks.
- Within a selected project, a task form: title required, optional description, priority select (`low`, `medium`, `high`), `Add task` button.
- Three visible Kanban columns headed `To Do`, `Doing`, and `Done`.
- Each task card shows title and priority and has `Move forward` (todo→doing→done), `Edit`, and `Delete` controls. For `done` cards, hide or disable `Move forward`.
- `Edit` lets the user update title, description, or priority using plain browser controls. The status is changed through Move forward only in the UI; API still supports direct status PATCH.
- Two filter dropdowns for status (`all`, `todo`, `doing`, `done`) and priority (`all`, `low`, `medium`, `high`); selecting a filter refreshes list using API query parameters; filtered-out cards are not rendered.
- Delete project control, with standard `window.confirm`, removes the selected project and its tasks and refreshes selection.
- Show an empty-state message when there are no projects and when a selected project has no matching tasks.
- Show API error messages in a visible error area; do not silently swallow errors.
- Use `textContent` for task titles and descriptions when inserting user-provided text. Do not inject user content as raw `innerHTML`.
- Vanilla JS, plain CSS, native HTML forms; no drag-and-drop, frameworks, icon libraries, charts, or animations required. Desktop and narrow-window layouts should remain usable.

## 7. Testing contract

Write meaningful pytest tests. Use `tmp_path / "taskboard-test.db"` per test, and FastAPI `TestClient` or HTTPX ASGI transport. Ensure tests do not touch the runtime `taskboard.db`.

### Repository tests (`taskboard/tests/test_repository.py`)

1. New database has empty projects, schema is idempotent.
2. Create and list projects in deterministic ascending ID order.
3. Create tasks with default status/priority and valid timestamps.
4. Filter by status, priority, and both together.
5. Patch title, description, priority, status and preserve omitted fields.
6. Deleting a project cascades to its tasks.

### API tests (`taskboard/tests/test_api.py`)

1. Health endpoint gives exact JSON response.
2. Project create/list/delete round trip.
3. Task create/list/patch/delete round trip.
4. Reject empty project name and empty task title.
5. Reject bad status, bad priority, too-long title and description.
6. Return 404 for missing project/task and 400 for empty task PATCH.
7. Validate `[]` response for empty lists, and no body for 204 deletes.
8. Check both query filters compose with AND and preserve ID order.

### Content integration tests (`taskboard/tests/test_ui_content.py`)

1. `GET /` returns real HTML with the heading `TaskBoard`, project form, task form, and all three column headings.
2. `GET /static/app.js` and `/static/style.css` return 200 and nonempty content.

### Browser E2E (Playwright)

Minimum three scenarios, in `taskboard/playwright/taskboard.spec.ts`:

1. First load displays the real TaskBoard heading and all three column headings.
2. Create a project and task through the browser; verify task title in `To Do`; click `Move forward` and verify it appears in `Doing`; move again and verify `Done`; delete the task and verify it disappears.
3. Create two tasks with different priorities, filter to `high`, verify only the high-priority task is visible; reset filter and verify both return.

Playwright scenarios must use unique project names and must not rely on previous test runs or test order. If the project runs against a persistent local server, test setup must delete the projects it creates before and after each scenario (using the API or UI). Assertions must inspect real task content, not just HTTP 200 or visibility of a placeholder element.

**Browser interaction rule**: At least one mandatory E2E test must drive a real user action in the browser — click a button, submit a form, select an option, or type into an input — and assert the resulting DOM state or API state change (for example: create project, create task, click `Move forward`, then verify the task appears in `Doing`; filter to `high`, then verify other tasks are absent). A static page loaded with `page.goto` plus heading/content assertions alone does **not** satisfy this SPEC. QA must reject `all_passed` when this interaction-and-state-change evidence is missing.

## 8. Delivery phases and dependencies

Implement the following three feature phases in order. The Foundation and
projects phase is divided into two dependent delivery subphases because its
complete first-delivery file set exceeds the hard limit of 10 files per
delivery phase. Every delivery subphase must own at most 10 unique files;
never omit a required output to meet the limit. Keep the two foundation
subphases sequential so the second builds on the package, database, models,
and repository established by the first. Later feature phases may extend
files already delivered, but each canonical file has only one first-delivery
owner.

### Phase 1 — Foundation and projects

Required outputs: `taskboard/pyproject.toml`, package layout, `db.py`,
project repository operations, `main.py` with `create_app`, health and project
API routes, a real basic HTML page and static mounting, `taskboard/README.md`,
and foundational pytest tests. The HTML template and both static assets are
created in this phase because `main.py` mounts and serves them; Phase 2 extends
their behavior rather than introducing those prerequisites later.

#### Delivery subphase 1a — Foundation core

First-delivery owner: exactly these eight canonical files:
`taskboard/pyproject.toml`, `taskboard/README.md`, `taskboard/.gitignore`,
`taskboard/__init__.py`, `taskboard/db.py`, `taskboard/models.py`,
`taskboard/repository.py`, and `taskboard/tests/test_repository.py`.
Implement package metadata and documentation, schema and connection setup,
validation/data mapping, project repository operations, and repository tests.
Ensure Python test dependencies are installed before test review. Test-review
commands must run tests only and must not install packages. This subphase verifies with
`python -m pytest -q tests/test_repository.py`.

#### Delivery subphase 1b — Runnable app and project API

Depends on delivery subphase 1a. First-delivery owner: exactly these six
canonical files: `taskboard/main.py`,
`taskboard/templates/index.html`, `taskboard/static/app.js`,
`taskboard/static/style.css`, `taskboard/tests/conftest.py`, and
`taskboard/tests/test_api.py`. Implement `create_app`, health and project API
routes, real basic HTML and static mounting, and isolated API test fixtures.
Pass the full Phase 1 test gate:

Exit criteria:

```bash
cd taskboard
python -m pytest -q tests
```

Ensure the package and test dependencies are installed before test review;
the test-review command itself must not install packages.
All Phase 1 tests pass; `GET /api/health` returns exact JSON;
create/list/delete project works; GET `/` returns real HTML. No task UI is
required yet. Both delivery subphases together own 14 first-delivery files,
split 8 and 6; each stays within the 10-file limit. All files are created
once and may be extended in later phases.

### Phase 2 — Tasks and Kanban UI

Required outputs: task repository operations, task API routes, validation, project selection, task creation/edit/delete, completed Kanban columns and move-forward behavior, and expanded pytest repository/API/UI-content coverage. Extend the Phase 1 template and static assets in place; do not introduce a second page or a new file layout.

Phase 2 adds `taskboard/tests/test_ui_content.py` and extends the Phase 1
application and test files in place. Its outputs do not introduce duplicate
copies or alternate paths for files already owned by Phase 1.

Exit criteria: `cd taskboard && python -m pytest -q tests` passes; a user can create a project and task, move it from todo to doing to done, edit it, and delete it via the real browser UI.

### Phase 3 — Filters, browser tests, and release check

Required outputs: status/priority filters, complete pytest coverage, Playwright scenarios under `taskboard/playwright/`, README test and run instructions, and final smoke QA.

Phase 3 adds `taskboard/package.json`, `taskboard/package-lock.json`,
`taskboard/playwright.config.ts`, and
`taskboard/playwright/taskboard.spec.ts`; it extends the existing UI, tests,
and README at their canonical paths.

Ensure Node dependencies are installed before test review. With the server
already running on `127.0.0.1:8080`, verify Phase 3 with
`cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`.
No features or dependencies outside this specification are introduced.

### Suggested bead decomposition (planner guidance)

The Planner may adapt bead IDs but should preserve clear ownership boundaries and the dependency ordering:

| Bead | Responsibility | Depends on |
|---|---|---|
| B1 | Packaging, schema, app factory and health route | None |
| B2 | Project repository and API, pytest | B1 |
| B3 | Real HTML shell, static serving, content tests | B1 |
| B4 | Task repository and validation, pytest | B2 |
| B5 | Task API and API tests | B4 |
| B6 | Project selection, creation/deletion browser UI | B2, B3 |
| B7 | Kanban task creation, editing, transitions, deletion UI | B5, B6 |
| B8 | Filters and filtered-content tests | B5, B7 |
| B9 | Playwright end-to-end tests, README and QA fixes | B8 |

Do not create beads that independently rewrite `main.py`, `db.py`, or `index.html` at the same time without an explicit dependency and integration sequence. The implementation agent should integrate the files incrementally and keep existing tests green.

## 9. Workflow integration notes

This repository is an external test rig for the Gas Town `rig-flow` workflow, not a place to implement Gas Town itself.

- Architect: write `architecture.md`, preserving the fixed module boundaries, data model, API contract, and dependency flow.
- Planner: write `plan.md`, create executable implementation beads mapped to the phases above, and identify the per-phase verify command.
- Tester `test_plan`: write `TEST_PLAN.md`, mapping each active-phase acceptance requirement to concrete pytest and, where applicable, Playwright tests and bead IDs.
- Polecat: implement and commit the actual code and tests; never mark a feature done without a runnable assertion.
- Tester `test_review`: run the active-phase verify command and confirm the planned tests exist with substantive assertions.
- QA: smoke-test real API behavior and rendered browser content, including a real control interaction plus DOM/API state-change assertion, and report failures with the relevant file and bead ID.
- When `layout_root` is a subdirectory such as `taskboard`, paths in the
  architecture's machine-readable `delivery_phases` ownership and
  `file_dependencies` mappings must include that prefix (for example,
  `taskboard/templates/index.html`). Assign every canonical profile deliverable
  to its first phase; dependency keys must be owned by that phase.
- The Foundation and projects SPEC phase maps to the ordered architecture
  delivery subphases `phase-1-core` and `phase-1-app`, both with
  `spec_focus: Foundation and projects`; the app subphase depends on the core
  subphase. Each delivery phase may own no more than 10 unique files.
- If a verification step fails, repair within the current phase. Do not replace failed tests with assertions that merely check status 200 or placeholder content.

Run all project commands from `taskboard/`. Phase 1a verifies with
`python -m pytest -q tests/test_repository.py`; Phase 1b and Phase 2 verify
with `python -m pytest -q tests`; Phase 3 verifies with
`python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`
against the already running server. Install Python and Node dependencies in
project setup, not during test review. A generated workflow profile must use
the exact canonical paths above, preserve this feature-phase ordering and
the two ordered Phase 1 delivery subphases, assign each newly introduced
deliverable to its first required phase, and not invent path aliases or move
prerequisites to a later phase. If the profile disagrees with this SPEC,
correct or regenerate the profile before design validation; do not change the
architecture to match a conflicting profile.

## 10. Definition of done

1. Fresh checkout with Python 3.11+ installs from `taskboard/` with `python -m pip install -e '.[test]'`.
2. `python -m pytest -q tests` passes from `taskboard/` and asserts real domain state changes.
3. `python -m uvicorn taskboard.main:app --host 127.0.0.1 --port 8080` starts the web app with no environment keys or manual schema steps.
4. GET `/` renders real UI, not a placeholder; static assets are accessible.
5. Users can create/delete projects and create/edit/move/filter/delete tasks from the UI.
6. Data persists across server restarts; deleting a project deletes its tasks.
7. Browser E2E tests at `taskboard/playwright/` pass against the running app; no E2E test depends on order or pre-existing projects. At least one test clicks/submits/types into a real control and asserts the resulting DOM/API state change; static page-load/content assertions alone are insufficient.
8. The orchestrated workflow reports completion only after phase tests and final QA pass, including browser interaction evidence.

## 11. Explicitly out of scope

Accounts, login, teams, task assignees, file uploads, comments, due dates, drag-and-drop, notifications, audit logs, analytics charts, real-time streams, cloud deployment, external APIs, AI/chat functionality, Dockerized application deployment, and production-grade access control.
