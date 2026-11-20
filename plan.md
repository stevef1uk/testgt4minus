# Implementation plan

## Active phase: phase-1-app

This plan covers only the six first-delivery files owned by the runnable-app
subphase. The completed phase-1-core files are dependencies and must not be
rewritten. Task CRUD, Kanban behavior, filtering, and browser E2E belong to
later phases; this phase proves the health/project API and the real basic page
and static delivery required by the phase gate.

## Verification contract

Run exactly:
`cd taskboard && python -m pytest -q tests`

The test suite must use an isolated temporary SQLite path and must preserve the
phase-1-core repository assertions. Do not install dependencies during
verification.

## Bead map

### te-hky: taskboard/main.py
- Scope: Implement the FastAPI application factory, module-level `app`, schema
  initialization wiring, static mounting, root template response, health route,
  and project list/create/delete routes for this phase.
- Architecture: architecture.md “Module / bead ownership” and “HTTP +
  entrypoint integration”; `create_app(db_path: str | None = None) -> FastAPI`
  owns dependency wiring and must not contain SQL.
- Interfaces: export `create_app(db_path: str | None = None) -> FastAPI` and
  module-level `app`; implement GET `/api/health`, GET `/api/projects`,
  POST `/api/projects`, DELETE `/api/projects/{project_id}`, GET `/`, and
  mounted `/static/app.js` and `/static/style.css` using the exact SPEC
  methods, response codes, and `{ "error": ... }` application errors.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py,
  taskboard/templates/index.html, taskboard/static/app.js,
  taskboard/static/style.css
- Acceptance: explicit `db_path` wins, then nonempty `TASKBOARD_DB_PATH`, and
  the documented fallback is used; startup initializes the schema; health
  returns exactly `{"status":"ok"}`; project create trims/validates names and
  returns 201; list is JSON ordered by ID; missing delete returns the specified
  404 error and successful delete is bodyless 204; root is real HTML and static
  assets are served nonempty. Do not add task routes in this phase.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-fzd: taskboard/templates/index.html
- Scope: Create the real basic server-rendered TaskBoard page required by the
  phase, with project creation/listing structure and the initial page regions
  needed for later extension.
- Architecture: architecture.md “Module / bead ownership”; template is served
  by `main.py`, uses semantic HTML, and references the canonical static paths.
- Interfaces: page heading `TaskBoard`, project creation input and `Add
  project` button, project selector/list region, and links to
  `/static/style.css` and `/static/app.js`; include a real taskboard shell
  rather than placeholder text.
- Depends on: taskboard/main.py
- Consumed by: taskboard/static/app.js, taskboard/static/style.css,
  taskboard/tests/test_api.py
- Acceptance: GET `/` contains the heading and a real project form/page shell,
  has content type `text/html`, references both canonical assets, and contains
  no database calls or inline server/application logic. Full task form,
  columns, filters, and task controls are later-phase extensions, not this
  bead's acceptance.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-sxk: taskboard/static/app.js
- Scope: Supply the initial vanilla-JavaScript asset and wire only the basic
  project-facing page behavior needed by this phase.
- Architecture: architecture.md browser ownership; browser behavior belongs in
  this file and must use the API contract and template selectors.
- Interfaces: load `/api/projects`, submit project creation to
  `/api/projects`, render project names using safe DOM APIs, and expose the
  initial project selection behavior without introducing a framework.
- Depends on: taskboard/main.py, taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html, browser/client checks
- Acceptance: the served script is nonempty real JavaScript; it can populate
  the project list from the API and add a project through the documented POST
  payload; project/user-visible text uses `textContent` rather than raw
  user-content HTML; API errors reach the page's visible error region. Task
  editing, movement, and filters are later-phase behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-rpb: taskboard/static/style.css
- Scope: Provide the basic TaskBoard presentation and responsive page layout
  for the real template and controls.
- Architecture: architecture.md stylesheet ownership; styles must target the
  canonical template and remain plain CSS.
- Interfaces: selectors for the page shell, heading, project form/list,
  controls, content regions, and visible error/empty states.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html and browser presentation
- Acceptance: the root page is readable and usable on desktop and narrow
  windows; project controls and status/error regions are visually distinct;
  the stylesheet is nonempty and has no frontend build or unrelated framework.
  Kanban-column styling is deferred until the task UI phase.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-j3i: taskboard/tests/conftest.py
- Scope: Provide the shared isolated FastAPI client fixture for API tests.
- Architecture: architecture.md test ownership; tests must never touch the
  runtime database and must construct the app through its public factory.
- Interfaces: pytest fixture `client` yielding `TestClient` for a temporary
  `tmp_path / "taskboard.sqlite3"` database, with `TASKBOARD_DB_PATH` set and
  the reloaded `create_app` application selected.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: each test gets an isolated database; schema setup occurs through
  `create_app`; the fixture supports multiple requests in one test so project
  create/list/delete persistence can be asserted; no production behavior is
  implemented in the fixture.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-c2c: taskboard/tests/test_api.py
- Scope: Add substantive API integration tests for the phase-1-app contract,
  using the shared isolated client.
- Architecture: architecture.md “Unit tests” and “phase-1-app” requirement;
  assertions cover HTTP behavior rather than repository implementation.
- Interfaces: pytest tests use the `client` fixture and exact SPEC paths,
  payloads, JSON shapes, status codes, and response bodies.
- Depends on: taskboard/tests/conftest.py, taskboard/main.py
- Consumed by: phase-1-app verification and later regression phases
- Acceptance: tests assert exact health JSON; project create/list/delete
  round-trip and ascending IDs; trimmed names; empty/invalid project names
  return application-level 400 errors; missing project deletion returns 404;
  successful delete has status 204 and an empty body; GET `/` returns real
  TaskBoard HTML with project form and both static assets; static GETs return
  200 and nonempty content. Tests do not require task routes, task UI, or
  browser automation in this phase.
- Verify: `cd taskboard && python -m pytest -q tests`

## Future considerations

Task repository/API operations, complete task form and Kanban columns,
editing/move/delete controls, filters, content tests, and Playwright scenarios
are owned by later delivery phases and are intentionally excluded here.
