# Phase-1-app implementation plan

This phase implements only the six required files for the runnable app and
project API. It depends on the completed phase-1-core package, database,
models, and repository. The exact verification command is:
`cd taskboard && python -m pytest -q tests`

## Bead map

### tm-5dk: taskboard/main.py
- Scope: Implement `create_app(db_path: str | None = None) -> FastAPI`, module-level `app`, schema startup, static mounting, HTML rendering, health route, project list/create/delete routes, and app-scoped database path.
- Architecture: Follow architecture.md §Module / bead ownership and §phase-1-app. HTTP routes in this phase are exactly GET `/api/health`, GET `/api/projects`, POST `/api/projects`, DELETE `/api/projects/{project_id}`, GET `/`, `/static/app.js`, and `/static/style.css`; do not add task routes in this phase.
- Interfaces: Export `create_app` and `app`; use the existing db/model/repository APIs from phase-1-core; return exact health JSON, project JSON, 201 creates, 204 empty deletes, and specified 400/404 error objects.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/templates/index.html, taskboard/tests/conftest.py, taskboard/tests/test_api.py
- Acceptance: `create_app` honors explicit db path then nonempty `TASKBOARD_DB_PATH`; startup initializes the selected database; health returns exactly `{"status":"ok"}`; project listing is ID ascending; valid project creation trims names and returns 201; invalid names return 400 with `error`; missing deletion returns 404; successful deletion has no body; GET `/` is real HTML and static assets are served.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-c2q: taskboard/templates/index.html
- Scope: Provide the real Phase-1 TaskBoard HTML shell with heading, project creation form, project selector/list, selected-project region, and static asset references.
- Architecture: Follow architecture.md §Planned file layout, §Module / bead ownership, and §phase-1-app; this phase supplies the basic page prerequisite, while task controls may be extended later without a second page.
- Interfaces: Provide semantic HTML and stable project-page hooks for app.js; link `/static/style.css` and `/static/app.js`; do not embed database calls or inline application logic.
- Depends on: taskboard/main.py
- Consumed by: taskboard/static/app.js, taskboard/static/style.css, taskboard/tests/test_api.py
- Acceptance: GET `/` contains heading `TaskBoard`, an Add project input/button, a project selection/list region, a selected-project status/empty region, and the exact static links; response content type is `text/html`.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Implement the Phase-1 browser behavior for loading projects, creating a project, selecting a project, deleting a selected project with `window.confirm`, and visible API error reporting.
- Architecture: Follow architecture.md §Module / bead ownership and the Phase-1 portion of §phase-1-app; use the exact project API paths and safe DOM APIs.
- Interfaces: Consume the template hooks and `/api/projects` plus `/api/projects/{project_id}` DELETE; use `textContent` for server/user text and do not invent task behavior required only by later phases.
- Depends on: taskboard/main.py, taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html, end-user browser
- Acceptance: initial load fetches projects and renders names; Add project sends the documented payload and refreshes selection; selecting a project records the active project; delete confirms, calls the documented route, and refreshes the list; empty project state and API errors are visible rather than silently swallowed.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Style the Phase-1 page, project form/list, selected-project region, buttons, empty state, error area, and basic narrow-window layout.
- Architecture: Follow architecture.md §Module / bead ownership and the template’s semantic hooks; do not add unsupported application behavior.
- Interfaces: Supply the stylesheet linked by index.html and selectors used by the Phase-1 DOM; preserve room for later Kanban extensions.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html, taskboard/static/app.js
- Acceptance: the TaskBoard heading, project controls, selected-project area, empty state, errors, and focus/disabled states are readable and usable; layout remains usable in a narrow window; stylesheet is nonempty and served at `/static/style.css`.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ff6: taskboard/tests/conftest.py
- Scope: Provide isolated pytest client setup using a temporary SQLite path and the application factory.
- Architecture: Follow architecture.md §Unit tests and §phase-1-app; tests must not touch runtime `taskboard.db`.
- Interfaces: Export the pytest `client` fixture using `tmp_path`, `TASKBOARD_DB_PATH`, `importlib.reload`, and FastAPI `TestClient`; assert health response exactly.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: every test gets a fresh database; the selected file is created; fixture startup proves GET `/api/health` returns 200 and exactly `{"status":"ok"}`; TestClient lifecycle is closed cleanly.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ssd: taskboard/tests/test_api.py
- Scope: Write substantive Phase-1 API tests for health, project CRUD, validation, ordering, missing resources, empty arrays, bodyless deletes, HTML, and static delivery.
- Architecture: Follow architecture.md §Unit tests, §Integration and testing, and §phase-1-app; exercise public HTTP behavior through the conftest client rather than repository internals.
- Interfaces: Test the routes and response shapes owned by taskboard/main.py; do not require task routes or Phase-2/3 files.
- Depends on: taskboard/main.py, taskboard/tests/conftest.py
- Consumed by: phase-1-app verification gate
- Acceptance: assertions prove exact health JSON; initial projects are `[]`; POST trims valid names and returns the documented project object/201; list preserves ID order; empty and invalid names return the documented 400 error shape; DELETE returns 204 with empty body and subsequent list is empty; missing project deletion returns 404; GET `/` contains real TaskBoard HTML and both static resources return 200 with nonempty content.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase acceptance

All six beads must preserve the phase-1-core module boundaries and use the
real exported symbols from architecture.md. No task CRUD, Kanban behavior,
filters, repository rewrites, Playwright files, or deployment artifacts are
part of this phase. Completion requires all Phase-1 app tests to pass with
the exact command above and requires real rendered HTML rather than a
placeholder response.
