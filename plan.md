# Phase-1-app implementation plan

This plan covers exactly the six first-delivery files owned by active phase-1-app. It builds on phase-1-core's completed package, SQLite schema, models, and repository. Do not add phase-2 task/Kanban behavior, phase-3 filters, or Playwright files. The single phase gate is `cd taskboard && python -m pytest -q tests`.

## Bead map

### te-hky: taskboard/main.py
- Scope: Implement the runnable FastAPI application factory, module-level `app`, schema initialization, static/template serving, health route, and project CRUD routes.
- Architecture: `architecture.md` § Requirements `phase-1-app`, § Module / bead ownership, and § HTTP + entrypoint integration for `taskboard/main.py`.
- Interfaces: Export `create_app(db_path: str | None = None) -> FastAPI` and module-level `app`; register `GET /api/health` returning `200 {"status":"ok"}`, `GET /api/projects` returning projects ordered by `id ASC`, `POST /api/projects` returning `201` project JSON, `DELETE /api/projects/{project_id}` returning `204` with an empty body, `GET /` returning HTML, and mounted `/static/app.js` and `/static/style.css`.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py (te-j3i), taskboard/tests/test_api.py (te-c2c)
- Acceptance: Resolve an explicit `db_path`, then nonempty `TASKBOARD_DB_PATH`, then the canonical repository-root-relative `taskboard/taskboard.db`; initialize the schema and pass the selected path to repository operations. Health JSON must be exact. Project listing must be `[]` initially and ascending by ID. Creation must trim and enforce the SPEC project-name rules, return exact project fields and status 201, and preserve data for later requests. Existing deletion must be 204 with no body; missing deletion must be 404 with `{"error": ...}`. Application-level invalid names must be 400 with the error shape; malformed integer paths retain FastAPI 422. Root and static responses must serve the real phase files.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-fzd: taskboard/templates/index.html
- Scope: Create the real server-rendered phase-1 TaskBoard page: heading, project creation form, project selector/list region, empty/error/status regions, and static asset links.
- Architecture: `architecture.md` § Planned file layout, § Module / bead ownership, and Requirements `phase-1-app`; use the SPEC § Application and UI contract without implementing later task controls.
- Interfaces: Semantic HTML consumed by `taskboard/main.py` and selectors/hooks consumed by `taskboard/static/app.js` (te-sxk) and `taskboard/static/style.css` (te-rpb); reference `/static/app.js` and `/static/style.css`.
- Depends on: <none>
- Consumed by: taskboard/main.py (te-hky), taskboard/static/app.js (te-sxk), taskboard/static/style.css (te-rpb)
- Acceptance: `GET /` can render this file as non-placeholder HTML with heading `TaskBoard`, a project-name input, an `Add project` button, a project selector/list, and visible empty/error areas. IDs and classes used by the phase-1 JavaScript and CSS must exist and be consistent. Keep markup server-rendered and vanilla; do not add task forms, Kanban columns, filters, or phase-3 browser harness requirements.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-sxk: taskboard/static/app.js
- Scope: Implement only phase-1 browser behavior for loading projects, creating a project, selecting/displaying projects, deleting the selected project, and showing API errors.
- Architecture: `architecture.md` § Module / bead ownership for `taskboard/static/app.js`; consume the exact project routes in SPEC § API contract.
- Interfaces: Browser code issues `GET /api/projects`, `POST /api/projects` with `{"name": ...}`, and `DELETE /api/projects/{project_id}`; it binds to the template's project controls and updates project, empty, status, and error regions.
- Depends on: taskboard/templates/index.html (te-fzd), taskboard/main.py (te-hky)
- Consumed by: taskboard/templates/index.html (te-fzd)
- Acceptance: On page load, fetch and render project names/IDs in ascending API order; a valid form submission sends JSON, refreshes the list, and clears the input; selecting a project updates the selected state; deletion uses the exact selected-project path and refreshes selection. Non-2xx responses display the API `error` text in the visible error area. Use vanilla JS and safe text insertion; do not implement task creation, Kanban movement, filters, or raw user-content HTML.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-rpb: taskboard/static/style.css
- Scope: Provide plain responsive CSS for the phase-1 TaskBoard shell, project form/list/selector, controls, empty state, status, and error regions.
- Architecture: `architecture.md` § Module / bead ownership for `taskboard/static/style.css` and the phase-1 application/UI requirements.
- Interfaces: Define selectors used by `taskboard/templates/index.html` (te-fzd) and updated by `taskboard/static/app.js` (te-sxk); no application data or JavaScript behavior.
- Depends on: taskboard/templates/index.html (te-fzd)
- Consumed by: taskboard/templates/index.html (te-fzd), taskboard/main.py (te-hky) through static serving
- Acceptance: The served stylesheet is nonempty, styles all named phase-1 regions and controls, remains usable at narrow widths, and requires no framework, build, animation, or extra dependency. Do not style or claim phase-2 Kanban/filter behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-j3i: taskboard/tests/conftest.py
- Scope: Provide the isolated pytest `client` fixture for API tests.
- Architecture: `architecture.md` § Module / bead ownership for `taskboard/tests/conftest.py` and the validated temporary-database fixture contract.
- Interfaces: Export pytest fixture `client`; use `tmp_path / "taskboard.sqlite3"`, set `TASKBOARD_DB_PATH`, reload `taskboard.main`, call `create_app(str(database_path))`, and yield a FastAPI `TestClient`.
- Depends on: taskboard/main.py (te-hky)
- Consumed by: taskboard/tests/test_api.py (te-c2c)
- Acceptance: Every test gets a fresh isolated SQLite path and a schema-initialized app; the client is closed after use; no test touches runtime `taskboard/taskboard.db`. The fixture must exercise the public app factory rather than private repository internals.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-c2c: taskboard/tests/test_api.py
- Scope: Add black-box HTTP tests for the active phase's health and project API contract, using only the `client` fixture.
- Architecture: `architecture.md` § Unit tests and Requirements `phase-1-app`; align assertions with SPEC § API contract and project JSON.
- Interfaces: Consume `client` from `taskboard/tests/conftest.py` and public routes from `taskboard/main.py`; do not test repository implementation or later browser behavior.
- Depends on: taskboard/tests/conftest.py (te-j3i), taskboard/main.py (te-hky)
- Consumed by: phase-1-app verification and QA
- Acceptance: Assert exact health status/body; fresh projects are `[]`; valid creates return 201 with exact `id`, trimmed `name`, and `created_at`; multiple projects list in ascending ID order; persistence appears in a subsequent list request; existing delete is 204 with empty body; missing delete is 404 with an `error`; missing, blank, overlong, and non-string project names produce 400 with an `error` and no unintended record.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase verification

Run exactly `cd taskboard && python -m pytest -q tests`. The phase is complete only when the API assertions pass and the root/static responses are real, served files. Phase-1-core files are dependencies, not additional active beads; phase-2 and phase-3 files and behavior remain out of scope.
