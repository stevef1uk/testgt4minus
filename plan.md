# Implementation plan

## Delivery scope

Implement only the six `phase-1-app` paths. The phase gate for every bead and for the integrated change is:
`cd taskboard && python -m pytest -q tests`.
The implementation must remain within the SPEC contract: a runnable FastAPI taskboard, its browser shell/assets, and API tests/fixtures. Do not add later-phase files or features.

## Bead map

### tm-5dk: taskboard/main.py
- Scope: Own the runnable application factory, SQLite schema/connection behavior, HTML root wiring, and all phase-1 API behavior described in SPEC and architecture.
- Architecture: `architecture.md` application entrypoint/data-access section; expose `create_app(...)` and the FastAPI application used by the test fixture. Use the `TASKBOARD_DB_PATH` environment override and initialize the projects store before serving requests.
- Interfaces: `create_app(database_path: str | None = None)` returns the application; `GET /api/health` returns `200` and `{"status":"ok"}`; project routes are `GET /api/projects`, `POST /api/projects`, `GET /api/projects/{project_id}`, `PUT /api/projects/{project_id}`, and `DELETE /api/projects/{project_id}`.
- Depends on: <none>
- Consumed by: taskboard/tests/conftest.py; taskboard/tests/test_api.py; taskboard/templates/index.html (through the root page); taskboard/static/app.js (through the API contract).
- Acceptance:
  - A fresh database is created at the configured path and the health endpoint returns exactly `{"status": "ok"}`.
  - Project create then list returns the created project with its persisted identifier and submitted name/description; retrieving that identifier returns the same record.
  - Updating an existing project persists the changed fields and deleting it removes it from subsequent list/get results.
  - Missing project IDs produce HTTP 404 with the SPEC error JSON shape; malformed or missing required project data produces HTTP 400 with the SPEC validation error shape.
  - The root page is served successfully and exposes the template/static assets; requests use the configured database rather than a shared test database.

### tm-ff6: taskboard/tests/conftest.py
- Scope: Provide the isolated pytest `client` fixture and database lifecycle used by the phase API suite.
- Architecture: `architecture.md` testing/fixture section; fixture reloads `taskboard.main`, calls `create_app`, and uses FastAPI `TestClient`.
- Interfaces: pytest fixture `client` yields a `TestClient` backed by a per-test `TASKBOARD_DB_PATH`; fixture asserts the database is created and the health contract before yielding.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance:
  - Each test receives a temporary SQLite path and cannot leak project rows into another test.
  - Fixture setup proves `/api/health` responds 200 with exactly `{"status":"ok"}` before API cases execute.
  - The fixture closes the test client after each test and supports application reload with the environment override.

### tm-j2d: taskboard/tests/test_api.py
- Scope: Encode the SPEC’s observable API contract as executable tests, including success, validation, and not-found cases.
- Architecture: `architecture.md` API test matrix; tests consume the `client` fixture and assert status codes and complete response JSON, not merely file existence.
- Interfaces: tests exercise `/api/health`, `/api/projects`, and `/api/projects/{project_id}` using the HTTP verbs and payloads specified by SPEC.
- Depends on: taskboard/main.py; taskboard/tests/conftest.py
- Consumed by: phase verification (`cd taskboard && python -m pytest -q tests`)
- Acceptance:
  - Assert health status/body exactly, empty-project list behavior, and successful project create/list/get round trip.
  - Assert update changes persisted values and delete returns the specified success response followed by 404/not-found behavior.
  - Assert missing required name/invalid request payloads return 400 and the documented error JSON; assert unknown IDs return 404 and the documented error JSON for get/update/delete.
  - Tests use the phase gate command and pass against a fresh temporary database without relying on pre-existing files.

### tm-c2q: taskboard/templates/index.html
- Scope: Provide the single-page taskboard markup, project form/list container, and links to the static stylesheet and script.
- Architecture: `architecture.md` frontend template section; preserve the DOM hooks and form/control IDs consumed by `static/app.js`.
- Interfaces: root document includes the project creation form, project list/status regions, and `/static/style.css` plus `/static/app.js` references.
- Depends on: taskboard/main.py
- Consumed by: taskboard/static/app.js; browser response from `GET /`
- Acceptance:
  - Root HTML is valid and contains the visible taskboard heading, project name/description inputs, submit control, and project-list container required by SPEC.
  - The template references the application’s static CSS and JavaScript paths so the browser can load both assets.
  - Form and list identifiers match the selectors used by `app.js`, with no server-side feature or later-phase UI added.

### tm-rta: taskboard/static/app.js
- Scope: Implement the browser-side project load, create, update/delete interaction, rendering, and API error presentation required by SPEC.
- Architecture: `architecture.md` frontend JavaScript section; use the API paths/methods and template selectors defined there.
- Interfaces: browser code calls `GET /api/projects`, `POST /api/projects`, and the project-item update/delete endpoints; it updates the template’s list/status DOM.
- Depends on: taskboard/templates/index.html; taskboard/main.py
- Consumed by: taskboard/templates/index.html in the served browser page
- Acceptance:
  - On page load, fetch projects and render returned names/descriptions; an empty response renders the empty state required by SPEC.
  - Form submission sends the documented JSON fields to `POST /api/projects`, then refreshes or updates the visible list and clears the form on success.
  - Project controls issue the documented update/delete requests and reflect successful changes/removal without a full-page navigation.
  - Non-2xx API responses are surfaced in the page status area rather than silently treated as success.

### tm-2ob: taskboard/static/style.css
- Scope: Style the taskboard page, form, project list/cards, controls, status and empty states according to the architecture’s frontend layout.
- Architecture: `architecture.md` frontend CSS section; selectors correspond to the markup classes/IDs in `index.html` and the states rendered by `app.js`.
- Interfaces: stylesheet is served at `/static/style.css` and defines the page/container, form, list/card, action, status, and empty-state selectors used by the template/script.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html
- Acceptance:
  - The served stylesheet is loadable by the root page and styles the required project form and list/card layout.
  - Normal, empty, error/status, and project action-control states have readable, distinct presentation matching the SPEC’s basic UI contract.
  - CSS remains limited to the required taskboard presentation and does not require an unplanned frontend framework or build step.

## Verification

Run exactly: `cd taskboard && python -m pytest -q tests`. Confirm the root page and static assets are registered, then exercise the full API matrix above through the test suite.

## Future considerations

Later architecture phases may add additional persistence entities or deployment concerns; they are intentionally outside this phase and must not be implemented here.
