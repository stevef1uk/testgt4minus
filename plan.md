# Implementation plan

## Active phase

`phase-1-app` delivers the runnable FastAPI app and its initial HTML/static
shell plus isolated API tests. Implement only the six required files below.
The authoritative phase gate is:

`cd taskboard && python -m pytest -q tests`

The app bead is sequenced after the template/assets it serves, and the test
beads follow the fixture and application contract. This avoids cyclic
dependencies while preserving the architecture's module boundaries.

## Bead map

### te-fzd: taskboard/templates/index.html
- Scope: Create the real server-rendered TaskBoard shell for the Phase 1 project experience.
- Architecture: `architecture.md` § Planned file layout, Module / bead ownership, and HTTP + entrypoint integration.
- Interfaces: Provide semantic project creation controls, project selection/list region, task form shell, empty/error regions, and the static asset references used by the page; Phase 1 must visibly include the TaskBoard heading and real project-facing page.
- Depends on: `<none>`
- Consumed by: taskboard/static/app.js; taskboard/static/style.css; taskboard/main.py; taskboard/tests/test_api.py
- Acceptance: `GET /` can render this real template with heading `TaskBoard`; the page contains project creation input and `Add project` button, project selector/list region, task-form shell, and visible `To Do`, `Doing`, and `Done` column headings; it references `/static/app.js` and `/static/style.css`; it is not a placeholder.
- Verify: `test -s taskboard/templates/index.html`

### te-sxk: taskboard/static/app.js
- Scope: Provide the vanilla browser client scaffold consumed by the template, including project loading and project CRUD interactions needed in Phase 1.
- Architecture: `architecture.md` § Module / bead ownership and E2E / integration testing; browser behavior belongs only here.
- Interfaces: Use the template's DOM hooks; call `GET /api/projects`, `POST /api/projects`, and `DELETE /api/projects/{project_id}`; render user-provided values safely with `textContent`; expose the taskboard interaction hooks that later phases extend.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html; taskboard/main.py
- Acceptance: The non-empty script loads projects on page load, permits adding a project, selecting a project, and deleting a selected project with `window.confirm`; it uses the exact project API paths, displays API errors visibly, and does not inject user content as raw `innerHTML`. It must not invent routes or external dependencies.
- Verify: `test -s taskboard/static/app.js`

### te-rpb: taskboard/static/style.css
- Scope: Style the initial page shell, project controls, task-board regions, forms, columns, empty/error states, and narrow layouts.
- Architecture: `architecture.md` § Module / bead ownership; presentation belongs only here.
- Interfaces: Define selectors/classes used by `index.html` for the page shell, project controls, task form, Kanban columns, task regions, status states, and responsive layout.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html; taskboard/main.py
- Acceptance: The stylesheet is non-empty, is served as a real static asset, styles the heading/forms/project area and all three visible columns, and keeps the page usable at narrow widths without animation or framework dependencies.
- Verify: `test -s taskboard/static/style.css`

### te-hky: taskboard/main.py
- Scope: Implement `create_app`, module-level `app`, schema startup, static/template serving, health route, and Phase 1 project API routes.
- Architecture: `architecture.md` § HTTP + entrypoint integration and Module / bead ownership.
- Interfaces: Export `create_app(db_path: str | None = None) -> FastAPI` and module-level `app`; implement exactly `GET /api/health`, `GET /api/projects`, `POST /api/projects`, `DELETE /api/projects/{project_id}`, `GET /`, and static `/static/app.js` and `/static/style.css` mounting. Pass the selected database path to repositories and preserve the documented `TASKBOARD_DB_PATH` precedence.
- Depends on: taskboard/templates/index.html; taskboard/static/app.js; taskboard/static/style.css; taskboard/db.py; taskboard/models.py; taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py; taskboard/tests/test_api.py
- Acceptance: `create_app` initializes the selected SQLite schema and stores its path in app state; health returns exactly `{"status":"ok"}` with 200; project listing is an ID-ascending JSON array; valid project creation returns 201 and trimmed names; invalid names return `{"error":...}` with 400; missing deletion returns 404; successful deletion returns 204 with no body; root returns real HTML and static files are non-empty; malformed integer paths retain 422.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-j3i: taskboard/tests/conftest.py
- Scope: Supply isolated pytest application/client fixtures for API tests.
- Architecture: `architecture.md` § Module / bead ownership and Unit tests.
- Interfaces: Export the pytest `client` fixture; use `tmp_path / "taskboard-test.db"`, set `TASKBOARD_DB_PATH` before reloading `taskboard.main`, construct `create_app` with the isolated path, yield a FastAPI `TestClient`, and close it.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Each test receives a fresh temporary database and never touches runtime `taskboard.db`; the environment override is applied before app construction; the yielded client can call health, project, root, and static routes; teardown closes the client. This is fixture infrastructure, not a test module, so no pytest test count is required.
- Verify: `test -s taskboard/tests/conftest.py`

### te-c2c: taskboard/tests/test_api.py
- Scope: Add substantive HTTP contract tests for the active Phase 1 app and projects behavior.
- Architecture: `architecture.md` § Unit tests and Requirements § phase-1-app, using the shared client fixture.
- Interfaces: Test only the public HTTP interface with the exact paths, methods, response shapes, and status codes from SPEC.md.
- Depends on: taskboard/tests/conftest.py; taskboard/main.py; taskboard/templates/index.html; taskboard/static/app.js; taskboard/static/style.css
- Consumed by: `<none>`
- Acceptance: Tests assert exact health JSON; project create/list/delete round trip and ascending IDs; trimmed names; empty/overlong names rejected with 400 and error JSON; missing project deletion returns 404; successful delete has status 204 and empty body; root contains real `TaskBoard` HTML, project controls, and Kanban headings; both static endpoints return 200 and non-empty content; no test merely asserts status 200 or imports a module.
- Verify: `cd taskboard && python -m pytest -q tests`

## Integration and dependency contract

The entrypoint owns `create_app` and imports the already-delivered database,
models, and repository modules from phase-1-core. It mounts the static directory,
renders `taskboard/templates/index.html`, and registers only the SPEC routes.
The template is implemented before the assets and entrypoint; `app.js` and
`style.css` consume template hooks but do not import each other. The entrypoint
then wires the template/assets and project repository into FastAPI. The fixture
reloads the entrypoint against a temporary database, and API tests consume the
fixture through HTTP. Task CRUD, filters, and richer Kanban behavior are
intentionally deferred to later phases.

## Definition of done

All six active-phase files are substantive and located at their exact
`taskboard/` paths. The full command
`cd taskboard && python -m pytest -q tests` passes, proving health, project
CRUD, real rendered HTML, static delivery, validation, and isolated database
behavior. No future-phase files or out-of-scope features are added.
