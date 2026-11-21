# Implementation plan — phase-1-app

This plan covers only the six required files for the runnable application
subphase. The completed phase-1-core repository, models, and database modules
are prerequisites. Verification for this phase is exactly:
`cd taskboard && python -m pytest -q tests`.

## Bead map

### tm-j2d: taskboard/tests/test_api.py
- Scope: Integration tests for the phase-1 app, using the isolated client fixture.
- Architecture: `taskboard/tests/test_api.py` owns API assertions; phase-1-app
  routes are health and project CRUD plus rendered page/static resources.
- Interfaces: Assert `GET /api/health`, `GET /api/projects`,
  `POST /api/projects`, `DELETE /api/projects/{project_id}`, `GET /`,
  `/static/app.js`, and `/static/style.css`; project JSON is `id`, `name`,
  `created_at`.
- Depends on: taskboard/tests/conftest.py, taskboard/main.py
- Consumed by: <none>
- Acceptance: Prove health returns exactly `{"status":"ok"}`; project creation
  trims names and returns 201, listing is ascending and returns `[]` initially,
  and deletion returns 204 with no body and 404 for a missing project. Prove
  empty/invalid project names return the specified 400 error object. Prove the
  root is real HTML containing TaskBoard and the required basic page structure,
  and both canonical static responses are nonempty with appropriate content.
  Do not test single-project GET/PUT routes or a project description field.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ff6: taskboard/tests/conftest.py
- Scope: Isolated pytest `client` fixture for the FastAPI application.
- Architecture: Set `TASKBOARD_DB_PATH` to a `tmp_path` database, reload
  `taskboard.main`, call `create_app`, and yield a FastAPI `TestClient`.
- Interfaces: Fixture supplies an app backed by an explicit temporary path and
  performs a health smoke assertion of status 200 and exact
  `{"status":"ok"}` before yielding.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Every test gets an independent database; schema initialization
  succeeds; the fixture never uses runtime `taskboard.db`; and the health
  bootstrap assertion is exact.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-5dk: taskboard/main.py
- Scope: Implement `create_app(db_path: str | None = None) -> FastAPI`,
  module-level `app`, schema startup, project routes, root rendering, and
  StaticFiles mounting.
- Architecture: `taskboard/main.py` owns HTTP wiring and resolves explicit
  db_path, then nonempty `TASKBOARD_DB_PATH`, then the taskboard.db fallback.
  It must not contain SQL or browser state.
- Interfaces: Export `create_app` and `app`. Implement exactly
  `GET /api/health` (200 exact object), `GET /api/projects` (200 array),
  `POST /api/projects` (201 project), `DELETE /api/projects/{project_id}`
  (204 empty body), `GET /`, `/static/app.js`, and `/static/style.css`.
  Application errors are the specified 400/404 error objects; malformed integer
  paths retain FastAPI 422. No single-project GET or PUT route is added.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py
- Acceptance: App startup initializes the selected database and stores its path
  in app state; repository operations persist project create/list/delete
  behavior and preserve exact project JSON shape. Root serves real HTML and
  static assets through canonical paths. DELETE is bodyless 204, missing
  projects are 404, and invalid names are 400. The module-level app supports
  the documented uvicorn import.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-c2q: taskboard/templates/index.html
- Scope: Provide the real server-rendered TaskBoard page shell and semantic
  controls required by the current and later UI phases.
- Architecture: Own semantic forms, selectors, columns, and message regions;
  reference canonical static assets and contain no database calls or inline
  application logic.
- Interfaces: Include the `TaskBoard` heading, project creation input and
  Add project control, project selector/list, task form hooks, priority
  control, visible To Do/Doing/Done headings, empty-state and error regions,
  and canonical `/static/app.js` and `/static/style.css` references.
- Depends on: taskboard/main.py
- Consumed by: taskboard/main.py, taskboard/tests/test_api.py
- Acceptance: `GET /` returns content type text/html and real non-placeholder
  markup containing the heading, project form, task form, three column headings,
  and visible message regions. Required element IDs/hooks are consistent with
  the script, and no project description field is invented.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Provide the vanilla browser module for loading projects and the basic
  project-selection/page behavior, with hooks ready for the canonical board.
- Architecture: Browser behavior belongs only in this file; use the documented
  API paths and safe DOM text insertion, without server validation logic.
- Interfaces: Use `/api/projects` for initial listing and project creation;
  handle project selection/deletion controls and the page error region. Use
  `textContent` for user-provided values and reference template hooks.
- Depends on: taskboard/main.py, taskboard/templates/index.html
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Initial load renders the project list or empty state, Add project
  submits the documented `{"name": ...}` payload, project selection updates
  the visible selection, and API failures appear in the error region. User
  content is not inserted as raw HTML; no nonexistent project GET/PUT endpoint
  or description payload is used.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Style the real TaskBoard shell, forms, project controls, board columns,
  empty state, and error state with nonempty canonical CSS.
- Architecture: Presentation belongs only in this stylesheet and must support
  the template's semantic structure without changing API behavior.
- Interfaces: Provide selectors for the heading, forms, project selector,
  controls, task-board columns, cards, empty state, error region, and a usable
  narrow-window layout.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/main.py, taskboard/tests/test_api.py
- Acceptance: `/static/style.css` returns 200, a CSS content type, and nonempty
  content. Styles match the template hooks, visibly distinguish the three
  columns and error/empty regions, and introduce no framework or build step.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase verification

Run only `cd taskboard && python -m pytest -q tests` after dependencies are
already installed. The phase must preserve the completed repository contract,
the exact project API scope, and the route exclusions stated in architecture.
