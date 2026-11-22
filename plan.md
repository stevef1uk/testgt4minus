# Implementation plan

Active phase: phase-1-app (foundation and runnable application). Implement only the six required paths below. The canonical phase verification command is `cd taskboard && python -m pytest -q tests`.

## Bead map

### tm-lro: taskboard/main.py
- Scope: Implement the FastAPI application factory, SQLite initialization, HTML/static mounting, health endpoint, and project CRUD API described by SPEC.
- Architecture: `taskboard/main.py` owns the application and persistence wiring for this phase; preserve the `create_app(database_path: str | None = None)` entry point and the SPEC route contract.
- Interfaces: provide `create_app(...)`; serve `GET /`, `GET /api/health`, and the documented `/api/projects` collection and `/api/projects/{project_id}` CRUD routes with JSON responses.
- Depends on: taskboard/templates/index.html; taskboard/static/app.js; taskboard/static/style.css
- Consumed by: taskboard/tests/conftest.py; taskboard/tests/test_api.py
- Acceptance: `GET /api/health` returns 200 and exactly `{"status":"ok"}`; `GET /` returns a real HTML page (not a placeholder) and serves the referenced assets; project creation persists the submitted project and returns the created record; collection reads return created projects; update changes the stored project; delete removes it; missing project operations return the SPEC status code and JSON error shape; malformed/invalid project input returns the SPEC client-error status without creating a record.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-c2q: taskboard/templates/index.html
- Scope: Provide the real Taskboard page structure and controls used by the API-backed client.
- Architecture: Template is the HTML shell owned by this bead and is rendered by `taskboard/main.py`; include the application mount point, project form/list UI, and static asset references required by SPEC.
- Interfaces: HTML document containing the Taskboard UI, with the JavaScript and stylesheet loaded through the app's `/static` routes.
- Depends on: <none>
- Consumed by: taskboard/main.py; taskboard/static/app.js
- Acceptance: `GET /` returns status 200, HTML content, a Taskboard heading/application container, project creation controls, and valid references to the app stylesheet and script; the page does not require a future-phase backend feature to render.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Implement the browser client for loading, creating, editing, and deleting projects through the documented API.
- Architecture: Own the page behavior and fetch calls; use the route paths and response fields defined by SPEC, and render success/error states into the template's UI.
- Interfaces: static browser script loaded by `index.html`; calls `GET/POST /api/projects`, `PUT /api/projects/{id}`, and `DELETE /api/projects/{id}`.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html; browser users of the runnable app
- Acceptance: on page load it requests the project collection and renders returned projects; submitting the form sends the documented project fields and displays the created project; edit and delete actions call the matching item routes and refresh the visible list; API failures surface an error message rather than silently reporting success.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Supply the page styling for the real Taskboard HTML and its project form/list, including readable success and error states.
- Architecture: Stylesheet is the static asset referenced by the template; keep selectors aligned with the template and client-generated project elements.
- Interfaces: `/static/style.css` asset consumed by `index.html`, with styles for the page, project controls/list, and visible error feedback.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html; browser users
- Acceptance: the stylesheet is served successfully from the app's static route, is referenced by the HTML page, and styles the rendered project form/list and error feedback without replacing the functional controls with a placeholder.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ff6: taskboard/tests/conftest.py
- Scope: Provide the pytest fixture that isolates the SQLite database per test and exposes a TestClient for the application.
- Architecture: Use `TASKBOARD_DB_PATH` and the application factory so tests exercise the same health and HTTP wiring as the runnable app.
- Interfaces: export the pytest `client` fixture; each fixture database is temporary and initialized before requests.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: the fixture sets a temporary database path, reloads/creates the application against that path, confirms initialization, yields a FastAPI TestClient, and proves health returns 200 with exactly `{"status":"ok"}`; do not use a nonexistent test module path as verification.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rmz: taskboard/tests/test_api.py
- Scope: Encode the phase's HTTP acceptance tests for health, page/assets, project CRUD, persistence, validation, and missing-resource errors.
- Architecture: Tests use the `client` fixture and assert the SPEC's routes, response payloads, and status/error codes rather than merely checking files exist.
- Interfaces: pytest tests consuming `client` from `taskboard/tests/conftest.py`.
- Depends on: taskboard/tests/conftest.py; taskboard/main.py; taskboard/templates/index.html
- Consumed by: phase verification and QA
- Acceptance: tests assert exact health JSON; a real HTML response and static assets; successful project create/list/update/delete round trips; deleted/missing IDs produce the documented error code and JSON; invalid payloads produce the documented validation code; and database isolation prevents cross-test state leakage.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase verification and review assertions

Run only `cd taskboard && python -m pytest -q tests`. Reviewers must confirm that the health JSON is exact, project CRUD is observable through HTTP, `/` is a real HTML page with working static references, and documented client-error codes/error payloads are asserted. Do not use `pytest taskboard/test_main.py` or collect `conftest.py` as a test module.

## Future considerations

Later phases may add functionality described elsewhere in architecture.md; this phase does not create beads for those paths.
