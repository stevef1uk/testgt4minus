# Implementation plan — phase-1-app (runnable app and project API)

## Phase context

Active phase: `phase-1-app`. Delivers the app factory, health and project API
routes, real rendered HTML page, static mounting, isolated pytest fixtures, and
API tests, on top of the already-delivered phase-1-core files (`taskboard/db.py`,
`taskboard/models.py`, `taskboard/repository.py`, `taskboard/tests/test_repository.py`),
which are dependency inputs, not beads of this phase.

Phase verification (exact command for test-review and QA):

    cd taskboard && python -m pytest -q tests

Every bead closes only after this gate passes. No bead is verified by
file-existence checks (`test -f`, `test -s`); acceptance asserts real behavior.

## Bead map

### tm-dv3: taskboard/main.py
- Scope: `create_app(db_path: str | None = None) -> FastAPI` plus module-level
  `app = create_app()`. HTTP routes are exactly the SPEC table: GET /api/health,
  GET /api/projects, POST /api/projects, DELETE /api/projects/{project_id}, plus
  the root browser route from SPEC section 6 that renders
  taskboard/templates/index.html as text/html. Mounts the taskboard/static
  directory through FastAPI StaticFiles so GET /static/app.js and
  GET /static/style.css serve the real files. DB path resolution: explicit
  argument, then nonempty TASKBOARD_DB_PATH environment variable, then
  taskboard.db; schema initialized at startup; selected path stored on
  app.state. No single-project GET or PUT route; no SQL statements in main.py.
- Architecture: architecture.md "Module / bead ownership" and "HTTP + entrypoint integration".
- Interfaces: exports create_app and app; uses db.py init_schema/connect, models.py validators, repository.py ProjectRepository.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py (phase-1-core, delivered).
- Consumed by: taskboard/tests/conftest.py (tm-ff6), taskboard/tests/test_api.py (tm-rmz).
- Verify: cd taskboard && python -m pytest -q tests
- Acceptance:
  - GET /api/health returns 200 with exact body {"status":"ok"}.
  - POST /api/projects {"name":"Demo"} returns 201 with project JSON (id, name, created_at); GET /api/projects returns 200 array ordered by id ASC, [] when empty.
  - DELETE /api/projects/{project_id} returns 204 with empty body; unknown id returns 404 {"error": ...}.
  - POST /api/projects with empty/whitespace name or name over 80 chars returns 400 {"error": ...}.
  - The root browser route returns 200 text/html real TaskBoard page; GET /static/app.js and GET /static/style.css return 200 with nonempty bodies.

### tm-c2q: taskboard/templates/index.html
- Scope: Jinja2 single-page shell: TaskBoard heading, project-creation input with Add project button, project selector/list region, task form region (title, description, priority select low/medium/high, Add task button), three column headings To Do / Doing / Done, status and priority filter dropdowns, delete-project control, empty-state and visible error regions. No inline application logic or database calls.
- Architecture: architecture.md "Planned file layout"; SPEC.md section 6 UI requirements.
- Interfaces: rendered by taskboard/main.py; element ids/classes consumed by taskboard/static/app.js and later test_ui_content.py.
- Depends on: <none> (wired through tm-dv3).
- Consumed by: taskboard/main.py (tm-dv3).
- Verify: cd taskboard && python -m pytest -q tests
- Acceptance:
  - The root browser route returns this template rendered as text/html, not a placeholder.
  - Rendered HTML contains TaskBoard heading, project form, task form, and all three column headings To Do, Doing, Done.

### tm-rta: taskboard/static/app.js
- Scope: vanilla browser JS served at GET /static/app.js. Phase-1 scope: fetch /api/projects on load and populate the project selector, create a project via POST /api/projects from the project form, delete the selected project using window.confirm then DELETE /api/projects/{id}, show API errors in the visible error area, show empty-state when no projects. Uses textContent for user-provided text; no raw innerHTML.
- Architecture: architecture.md "Module / bead ownership" (app.js owns loading, creating, safe rendering).
- Interfaces: loaded by taskboard/templates/index.html; calls tm-dv3 API routes; extended in phase-2/3.
- Depends on: taskboard/main.py (tm-dv3), taskboard/templates/index.html (tm-c2q).
- Consumed by: taskboard/tests/test_api.py (tm-rmz) via the /static/app.js response assertion.
- Verify: cd taskboard && python -m pytest -q tests
- Acceptance:
  - GET /static/app.js returns 200 with nonempty JavaScript body.
  - Project list populates from /api/projects; Add project creates a project; empty-state and error regions are driven by this script.

### tm-2ob: taskboard/static/style.css
- Scope: plain CSS served at GET /static/style.css: page layout, forms, project selector, column/card styling, error and empty-state regions, usable at desktop and narrow-window widths. No frameworks or animations.
- Architecture: architecture.md "Planned file layout" (`taskboard/static/style.css`).
- Interfaces: linked by taskboard/templates/index.html; carries no application behavior.
- Depends on: <none>.
- Consumed by: taskboard/templates/index.html (tm-c2q).
- Verify: cd taskboard && python -m pytest -q tests
- Acceptance:
  - GET /static/style.css returns 200 with nonempty CSS body.
  - Responsive rules keep the layout usable at narrow widths.

### tm-ff6: taskboard/tests/conftest.py
- Scope: pytest fixtures only (not a collected test file). The `client` fixture points TASKBOARD_DB_PATH at `tmp_path / "taskboard-test.db"` so tests never touch the runtime taskboard.db, builds the app with create_app from taskboard.main, asserts the temp database file exists, and yields a fastapi.testclient.TestClient only after GET /api/health returns 200 {"status":"ok"}.
- Architecture: architecture.md "Unit tests" (explicit temporary database; prevents use of the runtime database).
- Interfaces: exports the `client` fixture.
- Depends on: taskboard/main.py (tm-dv3).
- Consumed by: taskboard/tests/test_api.py (tm-rmz).
- Verify: cd taskboard && python -m pytest -q tests
- Acceptance:
  - Fixture database lives under tmp_path; the runtime taskboard.db is untouched.
  - Fixture health check asserts exact {"status":"ok"} before yielding.
  - Defines no test functions; pytest collects it as fixtures only.

### tm-rmz: taskboard/tests/test_api.py
- Scope: API contract tests on the conftest `client` fixture covering SPEC section 7 API tests 1-8: health, project round trip, validation failures, 404/400 behavior, empty lists, bodyless deletes, composed filters, ID ordering.
- Architecture: architecture.md "Unit tests" (exact health JSON, round trips, validation failures, empty arrays, bodyless deletes, composed filters, ID ordering).
- Interfaces: uses the `client` fixture from taskboard/tests/conftest.py; exercises routes from taskboard/main.py.
- Depends on: taskboard/tests/conftest.py (tm-ff6), taskboard/main.py (tm-dv3).
- Consumed by: phase gate `cd taskboard && python -m pytest -q tests`; extended in phase-2.
- Verify: cd taskboard && python -m pytest -q tests
- Acceptance (behavioral assertions, no existence-only checks):
  - Health returns exact {"status":"ok"} with 200.
  - Project round trip: POST 201 with object shape, GET list ordered by ascending id, DELETE 204 with empty body, repeat DELETE returns 404.
  - Empty or whitespace-only project name returns 400 {"error": ...}.
  - GET /api/projects on a fresh database returns 200 with body [].
  - The root browser route returns 200 HTML containing the TaskBoard heading, project form, and the three column headings To Do, Doing, Done.
  - GET /static/app.js and GET /static/style.css return 200 with nonempty content.

## Ordering

tm-dv3 -> tm-c2q, tm-rta, tm-2ob -> tm-ff6 -> tm-rmz. Phase gate:
`cd taskboard && python -m pytest -q tests`.

## Out of scope (YAGNI)

Task/Kanban routes and UI behavior are phase-2; filters, Playwright, and npm
files are phase-3. No auth, no drag-and-drop, no routes beyond the SPEC table,
no deployment artifacts in this phase.
