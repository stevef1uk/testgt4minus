# TaskBoard phase-1-app implementation plan

## Scope and verification

This plan covers only the active `phase-1-app` delivery subphase and its six
required files. It depends on the completed foundation exports in
`taskboard/db.py`, `taskboard/models.py`, and `taskboard/repository.py`; later
phase files are not assigned here. The exact phase gate is:

    cd taskboard && python -m pytest -q tests

Implementation must follow SPEC.md and architecture.md, preserve the canonical
`taskboard/` layout, use isolated temporary SQLite databases in tests, and
avoid placeholder HTML, assets, routes, or unrequested features.

## Bead map

### tm-5dk: taskboard/main.py
- Scope: Implement `create_app(db_path: str | None = None) -> FastAPI`, module-level `app`, database resolution, schema initialization, HTTP routes, template rendering, and static mounting.
- Architecture: This file owns HTTP wiring only; it consumes `taskboard/db.py`, `taskboard/models.py`, and `taskboard/repository.py`, stores the selected path in app state, and uses per-operation repository connections.
- Interfaces: Export `create_app(db_path: str | None = None) -> FastAPI` and `app`. Register exactly GET `/api/health`, GET/POST `/api/projects`, DELETE `/api/projects/{project_id}`, GET/POST `/api/projects/{project_id}/tasks`, PATCH/DELETE `/api/tasks/{task_id}`, GET `/`, and the two canonical static paths.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py
- Acceptance: Health is exactly `{"status":"ok"}`. Project and task operations return documented fields, ordering, defaults, status codes, filters, partial PATCH behavior, 400/404 error objects, and bodyless 204 deletes. Invalid writes do not persist; malformed integer paths remain 422; root is real HTML and assets have correct media types; selected temporary DB state never touches runtime `taskboard.db`.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-c2q: taskboard/templates/index.html
- Scope: Provide the real server-rendered TaskBoard page shell and controls.
- Architecture: Own semantic forms, selectors, columns, message regions, and asset references; no database access or inline application logic.
- Interfaces: Include `TaskBoard`, project name input and `Add project`, project selector, task title/description/priority controls and `Add task`, status and priority filters, `To Do`, `Doing`, and `Done` columns, empty/error regions, project-delete control, and canonical app.js/style.css references.
- Depends on: <none>
- Consumed by: taskboard/main.py, taskboard/static/app.js, taskboard/tests/test_api.py
- Acceptance: GET `/` returns non-placeholder `text/html` containing every required control, low/medium/high priority options, all three column headings, and empty/error regions. The structure provides DOM targets for safe user-content rendering.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Implement vanilla browser state, API calls, project selection and deletion, task lifecycle, filters, Kanban rendering, and move-forward behavior.
- Architecture: Own browser interactions and safe DOM rendering; use the exact API routes and template controls, without server validation or persistence code.
- Interfaces: Call project/task GET, POST, PATCH, and DELETE endpoints; render cards into the three status columns; provide add/edit/delete/move, filter/reset, empty-state, and visible-error interactions.
- Depends on: taskboard/templates/index.html, taskboard/main.py
- Consumed by: taskboard/tests/test_api.py; later taskboard/tests/test_ui_content.py
- Acceptance: Load and select projects, create tasks, edit title/description/priority, move todo→doing→done, delete tasks/projects, and refresh after writes. Filters pass query parameters and exclude cards; done tasks hide/disable move; errors are visible; user text uses `textContent`, not unsafe raw HTML.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Implement canonical TaskBoard presentation for forms, filters, cards, columns, messages, and narrow windows.
- Architecture: Own presentation selectors for the HTML and JavaScript only; contain no application data or behavior.
- Interfaces: Provide nonempty CSS served at `/static/style.css`, including three-column Kanban layout, task/card/form/filter styling, visible states, and responsive rules.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/main.py, taskboard/tests/test_api.py; later taskboard/tests/test_ui_content.py
- Acceptance: StaticFiles returns 200 with `text/css` and a nonempty body. Selectors support all required controls, columns, cards, messages, and usable narrow-window layout without out-of-scope features.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ff6: taskboard/tests/conftest.py
- Scope: Provide the shared isolated FastAPI TestClient fixture.
- Architecture: Own the `client` pytest fixture; use `tmp_path`, `TASKBOARD_DB_PATH`, the exported `create_app`, and a real TestClient context.
- Interfaces: Export fixture `client`, configured with a temporary SQLite path, and assert the exact health response before yielding.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Each test gets fresh temporary state, startup creates its database, health is exactly `{"status":"ok"}`, and runtime `taskboard.db` is neither selected nor modified. No mocked application or global connection is used.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ssd: taskboard/tests/test_api.py
- Scope: Write substantive phase-1 integration tests for health, project API, initial task/API contract, root, static assets, validation, errors, and isolation.
- Architecture: Own API assertions and consume the fixture; tests exercise routes from `taskboard/main.py`, not production implementation.
- Interfaces: Consume `client` from `taskboard/tests/conftest.py`; exercise exact nested project/task routes and malformed integer paths.
- Depends on: taskboard/tests/conftest.py, taskboard/main.py
- Consumed by: phase-1-app verification
- Acceptance: Assert exact health JSON; project and task round trips, ascending IDs, defaults, AND-composed filters, empty arrays, bodyless 204 deletes, and correct content types. Cover trimmed/empty/null/overlong values, invalid enums, empty PATCH, missing resources, 400/404 `{"error": ...}`, malformed-path 422, non-persistence of invalid writes, and isolation from runtime `taskboard.db`.
- Verify: `cd taskboard && python -m pytest -q tests`

## Delivery boundary

Phase-1-core files are dependencies only. Phase 2 adds
`taskboard/tests/test_ui_content.py` and extends the canonical UI/API files.
Phase 3 adds the Playwright package, lockfile, config, and browser spec.
Those later deliverables are intentionally excluded from this active plan.
