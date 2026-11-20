# Implementation plan

## Active phase and verification

This plan covers only delivery subphase `phase-1-app` (Foundation and
projects: runnable app). It implements the six active required paths and
extends the completed core phase; it does not create beads or acceptance work
for Phase 2 task/Kanban behavior or Phase 3 browser tooling. The exact phase
gate is:

`cd taskboard && python -m pytest -q tests`

The implementation must preserve the core repository contract while making a
real runnable FastAPI application. Acceptance is based on SPEC.md and
architecture.md § phase-1-app: exact health response, project CRUD, selected
database wiring, real root HTML, and mounted static assets. The API tests must
use an isolated temporary database and substantive state assertions.

## Bead map

### te-hky: taskboard/main.py
- Scope: Implement `create_app(db_path: str | None = None) -> FastAPI`, module-level `app`, app-state database-path wiring, schema initialization, Jinja template rendering, static mounting, and the Phase-1 project/health HTTP routes.
- Architecture: architecture.md § HTTP + entrypoint integration and § phase-1-app. Keep DDL in `taskboard/db.py`, SQL in `taskboard/repository.py`, and route/dependency wiring here.
- Interfaces: Export `create_app(db_path: str | None = None) -> FastAPI` and module-level `app`; implement `GET /api/health` returning exactly `{"status":"ok"}`, `GET /api/projects`, `POST /api/projects` with 201, `DELETE /api/projects/{project_id}` with 204, `GET /`, and mounted `/static/app.js` and `/static/style.css`. Application errors use the SPEC `{"error":"..."}` format with 400/404; malformed integer paths retain FastAPI 422.
- Depends on: taskboard/db.py; taskboard/models.py; taskboard/repository.py; taskboard/templates/index.html; taskboard/static/app.js; taskboard/static/style.css
- Consumed by: taskboard/tests/conftest.py; taskboard/tests/test_api.py
- Acceptance: Explicit `db_path` wins, then nonempty `TASKBOARD_DB_PATH`, then the documented fallback; app initialization creates the schema and stores the selected path without a shared mutable connection. Health JSON is exact. Project creation trims and validates names, returns the repository project shape with 201, listing is ascending by ID, deletion returns empty 204 and 404 for a missing project, and root/static responses are real and accessible. Do not add task routes in this phase.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-fzd: taskboard/templates/index.html
- Scope: Provide the real Phase-1 server-rendered TaskBoard page shell and project-oriented controls that can be extended in later phases.
- Architecture: architecture.md § Planned file layout, module/bead ownership, and § phase-1-app. The template is served by `GET /` and references canonical static assets.
- Interfaces: HTML document consumed by `taskboard/main.py`; reference `/static/app.js` and `/static/style.css`; include the visible `TaskBoard` heading, project creation form/control, and a project selector/list region. Keep markup extensible for later task UI without implementing database calls or inline application logic.
- Depends on: <none>
- Consumed by: taskboard/main.py; taskboard/tests/test_api.py
- Acceptance: `GET /` returns content type HTML containing a real TaskBoard page rather than a placeholder, a project form/control, and both canonical static references. The page is valid enough for the Phase-1 content assertions and does not claim unsupported Phase-2 task behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-sxk: taskboard/static/app.js
- Scope: Supply the Phase-1 browser asset served from the canonical static directory; establish the basic project-page client hook without introducing out-of-phase task/Kanban features.
- Architecture: architecture.md § Browser client and § phase-1-app; browser behavior belongs in this file and user content must later be rendered safely.
- Interfaces: Static asset available at `GET /static/app.js`, referenced by `taskboard/templates/index.html`, and valid JavaScript. Any Phase-1 project-page wiring must use the documented `/api/projects` contract; no alternate API paths.
- Depends on: <none>
- Consumed by: taskboard/templates/index.html
- Acceptance: StaticFiles serves a nonempty JavaScript response with 200. The asset does not require a frontend build, framework, or external service, and does not invent task routes before their owning phase.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-rpb: taskboard/static/style.css
- Scope: Supply the Phase-1 real page styling asset, including readable layout and project form/list presentation while remaining extensible for later Kanban work.
- Architecture: architecture.md § Static styling and § phase-1-app; styling remains separate from application data and JavaScript behavior.
- Interfaces: Static asset available at `GET /static/style.css` and referenced by `taskboard/templates/index.html`; provide selectors for the Phase-1 page shell and controls.
- Depends on: <none>
- Consumed by: taskboard/templates/index.html
- Acceptance: StaticFiles serves nonempty CSS with 200, and the stylesheet supports a usable real TaskBoard page without replacing controls or adding out-of-scope dependencies.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-j3i: taskboard/tests/conftest.py
- Scope: Implement the isolated FastAPI test client fixture for Phase-1 API tests.
- Architecture: architecture.md § Unit tests and module/bead ownership. Use the validated temporary-path pattern: `tmp_path / "taskboard.sqlite3"`, `TASKBOARD_DB_PATH`, reload of `taskboard.main`, `create_app(str(database_path))`, and `TestClient`.
- Interfaces: Export pytest fixture `client` yielding a FastAPI `TestClient`; each test receives a fresh temporary SQLite database and exercises the real app routes.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Tests never touch the runtime database, the fixture initializes the app against the temporary path, and the yielded client can test health, project CRUD, root HTML, and static delivery.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-c2c: taskboard/tests/test_api.py
- Scope: Write meaningful Phase-1 API and app-content regression tests, following TDD and covering only the runnable app/project contract owned by this phase.
- Architecture: architecture.md § Unit tests, § Integration and testing, and § phase-1-app. Tests assert real responses and persisted state rather than placeholders or status-only checks.
- Interfaces: Pytest tests consume fixture `client` and assert the HTTP contracts for `GET /api/health`, `GET/POST/DELETE /api/projects`, `GET /`, and `/static/app.js` plus `/static/style.css`.
- Depends on: taskboard/tests/conftest.py; taskboard/main.py; taskboard/templates/index.html; taskboard/static/app.js; taskboard/static/style.css
- Consumed by: <none>
- Acceptance: Assert exact health JSON; create at least two projects and prove returned IDs and ascending list order; prove names are trimmed and invalid empty names return application-level 400; delete returns 204 with no body and a subsequent missing-project delete returns 404; assert root HTML contains `TaskBoard`, the project form/control, and real static references; assert both static assets return 200 and nonempty content. Do not test task routes, filters, Kanban movement, or Playwright in this phase.
- Verify: `cd taskboard && python -m pytest -q tests`

## Dependency and delivery boundaries

The six beads extend the completed `phase-1-core` exports in order: the app
entrypoint consumes database, model, and repository behavior; its fixture
consumes the app; and API tests consume the fixture and real HTTP boundary.
The template and static assets are prerequisites of root serving and are
tested through that boundary. Later phases may extend these canonical files,
but this phase must not add task repository operations, task API routes,
Kanban interactions, filter controls, Playwright files, or alternate paths.
