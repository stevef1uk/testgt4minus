# Implementation plan

## Active phase

Phase `phase-1-app` delivers only the six required files below, building on
the completed foundation core. The exact verification command is:
`cd taskboard && python -m pytest -q tests`. This phase implements the
runnable FastAPI app, basic server-rendered page, static assets, isolated
fixture, and project API only. It must not add task routes, single-project
GET, or PUT/update routes.

## Bead map

### tm-lro: taskboard/main.py
- Scope: Implement `create_app(db_path: str | None = None) -> FastAPI`,
  module-level `app`, schema initialization, HTML rendering, static mounting,
  health, and project collection/create/delete HTTP wiring.
- Architecture: `taskboard/main.py` owns HTTP wiring and app state; use the
  existing db/models/repository modules from phase-1-core and the exact
  architecture route set.
- Interfaces: export `create_app(...)` and `app`; provide `GET /`,
  `GET /api/health`, `GET /api/projects`, `POST /api/projects`, and
  `DELETE /api/projects/{project_id}`. Serve `/static/app.js` and
  `/static/style.css`. Do not provide single-project GET or PUT.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py
- Acceptance: health returns exactly `{"status":"ok"}` with 200; project list
  is an ID-ascending JSON array; valid creation returns 201 and persists the
  project; invalid names return the specified 400 error object; deletion
  returns 204 with no body and missing deletion returns 404. `/` is real
  HTML and static assets are nonempty and reachable. No unsupported update
  route is registered.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-c2q: taskboard/templates/index.html
- Scope: Create the real foundational TaskBoard HTML shell with heading,
  project creation form, project list/empty-state regions, and asset links.
- Architecture: Own semantic markup and selectors consumed by `app.js`;
  render through `main.py`, with no inline database or application logic.
- Interfaces: HTML page loaded by `GET /`; reference `/static/style.css` and
  `/static/app.js`; expose project form/list and feedback selectors.
- Depends on: <none>
- Consumed by: taskboard/main.py, taskboard/static/app.js
- Acceptance: rendered HTML has the `TaskBoard` heading, usable project name
  input and `Add project` control, project list/empty-state container, and
  valid stylesheet/script references. It is not a placeholder and does not
  claim task or project-edit functionality in this phase.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Implement the phase-1 browser client for loading, creating, rendering,
  and deleting projects through the allowed API.
- Architecture: Own browser behavior and safe DOM rendering; align selectors
  with `index.html` and use the SPEC JSON contract.
- Interfaces: issue `GET /api/projects`, `POST /api/projects`, and
  `DELETE /api/projects/{project_id}` requests; provide initialization and
  project form/delete handlers. Do not call PUT or single-project GET.
- Depends on: taskboard/templates/index.html, taskboard/main.py
- Consumed by: taskboard/templates/index.html, browser users
- Acceptance: page load displays the project collection; valid submission
  sends the project name and displays the created project; delete uses the
  project-id DELETE route and refreshes selection/list state; empty and API
  error feedback is visible; user content is inserted safely with
  `textContent` or equivalent DOM APIs.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Style the foundational page, project form/list, empty state, controls,
  and visible feedback responsively.
- Architecture: Own presentation for selectors in `index.html` and the
  client-generated project elements; contain no application behavior.
- Interfaces: serve as `/static/style.css` and define styles consumed by the
  template and `app.js`.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html, browser users
- Acceptance: asset is nonempty and served successfully; the TaskBoard
  heading, project controls/list, empty state, and success/error feedback are
  readable and usable on narrow windows. No edit/update UI is introduced.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ff6: taskboard/tests/conftest.py
- Scope: Provide the isolated pytest `client` fixture using a temporary
  SQLite path and the application factory.
- Architecture: Follow the fixture ownership in architecture.md; set
  `TASKBOARD_DB_PATH`, reload/create the app against the temporary database,
  and use FastAPI `TestClient`.
- Interfaces: export a `client` fixture for `test_api.py`; verify database
  initialization and exact health response before yielding.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: each fixture uses a distinct `tmp_path` database, does not touch
  runtime `taskboard.db`, creates the schema through `create_app`, and asserts
  health status 200 with exactly `{"status":"ok"}`.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rmz: taskboard/tests/test_api.py
- Scope: Test the active phase's public HTTP contract for health, rendered
  page/assets, project create/list/delete, validation, persistence, and
  missing-resource behavior.
- Architecture: Use the shared `client` fixture and assert real response
  payloads, status codes, bodylessness, and database-visible state.
- Interfaces: consume `client` from `taskboard/tests/conftest.py` and routes
  owned by `taskboard/main.py`.
- Depends on: taskboard/tests/conftest.py, taskboard/main.py
- Consumed by: phase verification and QA
- Acceptance: tests prove exact health JSON; real HTML with `TaskBoard`,
  project controls, and static assets; empty list then valid project
  create/list round trip in ID order; trimmed/empty and overlong names follow
  SPEC validation; delete returns 204 with an empty body and removes the
  project; missing delete returns 404 with `{"error": ...}`. Tests must not
  require or assert project GET-by-ID or PUT/update behavior, which are
  forbidden in this phase.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase boundary

Do not create or modify beads for phase-1-core, phase-2, or phase-3 files.
Later phases may extend these canonical files, but this plan owns only the
phase-1-app acceptance listed above.
