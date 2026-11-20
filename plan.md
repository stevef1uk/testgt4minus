# Implementation plan

## Scope and verification

This plan covers only the active delivery phase `phase-1-app` and its six
required paths. The completed `phase-1-core` package, database, models, and
repository are dependencies but are not re-planned here. This phase delivers a
runnable FastAPI application with health and project endpoints, a real HTML
shell, static asset mounting, an isolated test fixture, and black-box API
coverage. Task behavior beyond the project/app foundation is deferred to later
phases. The exact phase gate is:

`cd taskboard && python -m pytest -q tests`

The implementation must preserve the SPEC route spellings, status codes,
JSON error shape, database-path selection, and package boundaries. No Docker,
frontend build, alternate routes, or unrelated features are in scope.

## Bead map

### te-hky: taskboard/main.py
- Scope: Implement `create_app(db_path: str | None = None) -> FastAPI`, module-level `app`, schema initialization, static mounting, root rendering, health, and the phase-1 project API routes.
- Architecture: `taskboard/main.py` owns HTTP routes and dependency wiring; it stores the selected database path in app state and delegates SQL and mapping to the completed core modules.
- Interfaces: Export `create_app(db_path: str | None = None) -> FastAPI`; expose `app`; provide GET `/`, GET `/api/health`, GET `/api/projects`, POST `/api/projects`, and DELETE `/api/projects/{project_id}` with SPEC response codes and shapes.
- Depends on: taskboard/db.py; taskboard/models.py; taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py (te-j3i); taskboard/tests/test_api.py (te-c2c)
- Acceptance: explicit `db_path` wins over `TASKBOARD_DB_PATH`, with the documented repository-root fallback; startup initializes the schema; `/` returns real HTML with `text/html`; `/static/app.js` and `/static/style.css` are served; health returns exactly `{"status":"ok"}`; project list is ID-ascending; valid creation returns 201; invalid names return 400 with `{"error": ...}`; missing deletion returns 404 and successful deletion returns an empty 204 response.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-rpb: taskboard/static/style.css
- Scope: Provide the presentation layer for the phase-1 TaskBoard shell and stable selectors needed by the template and future browser behavior.
- Architecture: CSS owns responsive presentation, forms, project/task regions, controls, and visual state classes; it contains no application data or JavaScript behavior.
- Interfaces: Define presentation selectors for the template, including the page shell, forms, project list/selected state, task regions, columns, cards, controls, empty/error regions, and completed/hidden state classes where present.
- Depends on: <none>
- Consumed by: taskboard/templates/index.html (te-fzd); taskboard/static/app.js (te-sxk)
- Acceptance: the stylesheet is nonempty and reachable at `/static/style.css`; it makes the heading, forms, lists, controls, and shell usable on narrow and desktop windows; selected and completed states are visibly distinguishable; it adds no framework, animation, or unrelated feature.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-fzd: taskboard/templates/index.html
- Scope: Implement the real server-rendered TaskBoard page and the stable DOM contract for the project shell and later task controls.
- Architecture: The template owns semantic markup only: page heading, project creation form/list/selection, task area, filters, Kanban headings, empty/error regions, and references to mounted static assets.
- Interfaces: Provide the IDs, classes, and data attributes consumed by `taskboard/static/app.js` (te-sxk); load `/static/style.css` and `/static/app.js`; include `TaskBoard`, an Add project control, and the documented project/task regions.
- Depends on: taskboard/main.py (te-hky)
- Consumed by: taskboard/static/app.js (te-sxk); taskboard/tests/test_api.py (te-c2c)
- Acceptance: GET `/` contains real HTML rather than a placeholder, the `TaskBoard` heading, a project name input and `Add project` button, project selection/list markup, task form markup, visible `To Do`, `Doing`, and `Done` headings, status/priority filter controls, and usable empty/error regions; user content is not pre-rendered as unsafe HTML.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-sxk: taskboard/static/app.js
- Scope: Implement the vanilla browser client foundation that loads projects, renders project selection, submits project creation/deletion, and exposes the DOM hooks for the later task UI.
- Architecture: Browser behavior belongs exclusively here; use the SPEC API paths and JSON fields, bind to template selectors, and use safe DOM APIs for user-provided text.
- Interfaces: Call GET/POST/DELETE `/api/projects` routes from the SPEC; bind to selectors exported by `taskboard/templates/index.html` (te-fzd); update selected project state and visible error messages after operations.
- Depends on: taskboard/main.py (te-hky); taskboard/templates/index.html (te-fzd); taskboard/static/style.css (te-rpb)
- Consumed by: taskboard/templates/index.html (te-fzd); taskboard/tests/test_api.py (te-c2c)
- Acceptance: initial load requests and displays the project list; adding a project sends the documented payload and refreshes selection; deleting the selected project uses the documented API and refreshes the view; API failures appear in the visible error area; rendering uses `textContent` for user-provided values and introduces no framework or speculative feature.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-j3i: taskboard/tests/conftest.py
- Scope: Provide an isolated pytest `client` fixture for the runnable app.
- Architecture: Use `tmp_path`, set `TASKBOARD_DB_PATH`, reload `taskboard.main` when needed, call the public app factory, and yield a FastAPI `TestClient`.
- Interfaces: Export the pytest fixture `client`, consumed by `taskboard/tests/test_api.py` (te-c2c).
- Depends on: taskboard/main.py (te-hky)
- Consumed by: taskboard/tests/test_api.py (te-c2c)
- Acceptance: every test receives a fresh temporary SQLite database; the client is usable; environment and database state do not leak between tests; the fixture never rewrites the runtime database or implements production behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-c2c: taskboard/tests/test_api.py
- Scope: Add deterministic black-box tests for the active runnable-app contract using the `client` fixture.
- Architecture: Test through HTTP against `taskboard/main.py`; cover the phase-1 health/project/root/static behavior without duplicating repository internals or claiming later task-phase requirements.
- Interfaces: Use fixture `client` from `taskboard/tests/conftest.py` (te-j3i) and exercise the exact phase-1 routes owned by `taskboard/main.py` (te-hky).
- Acceptance: assert exact health JSON; root status, HTML content type, `TaskBoard` heading, project form, and all three column headings; assert both static assets return 200 and nonempty content; assert project create/list/delete round-trip, ascending IDs, 201/204 behavior, empty 204 body, invalid project names as 400 error JSON, and missing-project deletion as 404; tests use no network and leave no persistent runtime database.
- Verify: `cd taskboard && python -m pytest -q tests`

## Delivery order

Implement `taskboard/main.py` against the completed core first. Implement
`taskboard/static/style.css` and `taskboard/templates/index.html` as the
same-tier shell assets without a dependency edge between them. Then wire
`taskboard/static/app.js`, followed by the isolated fixture and API tests.
This ordering is acyclic and matches the architecture file dependencies.

## Future considerations

Task CRUD, Kanban transitions, editing/deletion controls, filters, and
Playwright scenarios are later-phase work and must not be added to this
phase's acceptance criteria.
