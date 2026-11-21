# Implementation plan

## Active phase

The active phase is `phase-1-app`, after the completed `phase-1-core`.
Implement exactly these six required paths: `taskboard/main.py`,
`taskboard/templates/index.html`, `taskboard/static/app.js`,
`taskboard/static/style.css`, `taskboard/tests/conftest.py`, and
`taskboard/tests/test_api.py`. The phase gate is
`cd taskboard && python -m pytest -q tests`. This phase delivers the
runnable app, health and project API, real HTML/static serving, and isolated
API tests; task routes, Kanban behavior, filters, and Playwright files belong
to later phases.

## Bead map

### tm-5dk: taskboard/main.py
- Scope: Implement `create_app(db_path: str | None = None) -> FastAPI`, module `app`, database-path selection, schema initialization, static mounting, index rendering, health, and project routes.
- Architecture: `taskboard/main.py` owns HTTP wiring and consumes `taskboard/db.py`, `taskboard/models.py`, and `taskboard/repository.py`; it must not contain SQL.
- Interfaces: `GET /api/health` returns 200 and `{"status":"ok"}`; `GET /api/projects` returns ID-ascending projects; `POST /api/projects` returns 201 or the SPEC 400 error; `DELETE /api/projects/{project_id}` returns 204 or 404; `GET /` serves HTML; `/static/app.js` and `/static/style.css` are mounted.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py
- Acceptance: A temporary SQLite path initializes on app creation; health JSON is exact; project names are validated, persisted, listed deterministically, and deleted with a bodyless 204; missing deletion returns the documented error object and 404; no task routes are added in this phase.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-c2q: taskboard/templates/index.html
- Scope: Provide the real TaskBoard HTML shell with heading, project form/list controls, message region, and canonical asset references.
- Architecture: The template owns semantic markup and is rendered by `taskboard/main.py`; browser behavior remains in `taskboard/static/app.js`.
- Interfaces: Include heading `TaskBoard`, project-name input, `Add project` button, project selector/list region, visible error/message region, `/static/app.js`, and `/static/style.css`.
- Depends on: taskboard/main.py
- Consumed by: taskboard/static/app.js, taskboard/tests/test_api.py
- Acceptance: `GET /` has `text/html` content type and real page content, not a placeholder; required project controls and stable selectors exist; both canonical static paths are referenced. Do not add later-phase task requirements.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Implement phase-1 project loading, creation, selection, supported deletion control, safe DOM rendering, and visible API errors.
- Architecture: Own browser state, fetch calls, event handlers, and DOM updates; use only the SPEC project routes and template selectors.
- Interfaces: Consume `GET`/`POST /api/projects` and `DELETE /api/projects/{project_id}`; render project names with `textContent`; refresh visible state after writes.
- Depends on: taskboard/templates/index.html, taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Initial load displays project data; creation and deletion refresh the project view and selection; API failures appear in the error region; the asset is nonempty and served at `/static/app.js`; no task/filter API is invented.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Style the phase-1 page shell, project form/list, controls, visible messages, and narrow-window layout.
- Architecture: Presentation only, targeting the semantic template and script selectors; no application logic.
- Interfaces: Provide usable page, project, button, selection, and error/message styles.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/tests/test_api.py
- Acceptance: `/static/style.css` returns nonempty content; project controls and messages remain readable on desktop and narrow windows; no later Kanban behavior is required.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ff6: taskboard/tests/conftest.py
- Scope: Provide the isolated pytest `client` fixture.
- Architecture: Use `tmp_path`, set `TASKBOARD_DB_PATH`, reload `taskboard.main`, call `create_app`, and yield FastAPI `TestClient`.
- Interfaces: Export fixture `client`; assert database creation and exact health response before yielding.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Every test receives a fresh temporary database and never touches runtime `taskboard.db`; startup succeeds; the fixture confirms HTTP 200 and `{"status":"ok"}`.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ssd: taskboard/tests/test_api.py
- Scope: Test the phase-1 public contract for health, projects, rendered HTML, and static assets.
- Architecture: Use the public HTTP surface and `client` fixture; assert state and content, not status codes alone.
- Interfaces: Consume `client` from `taskboard/tests/conftest.py` and routes from `taskboard/main.py`.
- Depends on: taskboard/tests/conftest.py, taskboard/main.py
- Consumed by: <none>
- Acceptance: Assert exact health JSON; initial empty list; trimmed project names; ascending list order; empty and overlong names rejected with 400 and `error`; create/list/delete round trip; 204 has no body; missing delete is 404; `/` contains `TaskBoard` and the project form; both static endpoints return 200 and nonempty content.
- Verify: `cd taskboard && python -m pytest -q tests`

## Integration and phase boundary

The entrypoint bead is ordered after the completed core exports. The fixture
depends on the app factory, and API tests depend on both. All six beads must
retain the module boundaries and exact SPEC routes, methods, status codes, and
JSON shapes. Do not implement later-phase task/Kanban/filter or Playwright
deliverables in this phase.
