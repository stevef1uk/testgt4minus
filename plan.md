# Phase-1 implementation plan

Implement only the six active-phase files. Preserve the repository layout and use the architecture as the source of truth. The polecat must run `cd taskboard && python -m pytest -q tests` after implementation.

## Bead map

### te-hky: taskboard/main.py
- Scope: Implement the runnable FastAPI application, SQLite-backed project persistence, static/template serving, and the health plus project HTTP endpoints described by SPEC.
- Architecture: `architecture.md` § `taskboard/main.py`; own `create_app(database_path: str | None = None)` and the application routes, with storage isolated behind the module's documented helpers.
- Interfaces: `create_app`; `GET /api/health`; `GET /api/projects`; `POST /api/projects`; `DELETE /api/projects/{project_id}`. JSON project records expose `id` and `name`; failures expose an `error` field.
- Depends on: taskboard/templates/index.html (te-fzd), taskboard/static/app.js (te-sxk), taskboard/static/style.css (te-rpb)
- Consumed by: taskboard/tests/conftest.py (te-j3i), taskboard/tests/test_api.py (te-c2c)
- Acceptance:
  - The app starts through the documented factory and serves the index page and static assets.
  - `GET /api/health` returns HTTP 200 and the exact SPEC health JSON.
  - A valid project create returns HTTP 201 with the expected `id` and `name`; list returns HTTP 200 in ascending ID order and reflects persistence.
  - Delete returns HTTP 204 with an empty body for an existing project; deleting a missing ID returns HTTP 404 with the documented error shape.
  - Missing, blank, and invalid project names return HTTP 400 with an `error` message, without creating a project.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-fzd: taskboard/templates/index.html
- Scope: Provide the server-rendered TaskBoard shell, project creation form, project selector/list region, status and error regions, and links to the static assets.
- Architecture: `architecture.md` § `taskboard/templates/index.html`; use the exact element IDs, classes, labels, and asset URLs required by SPEC.
- Interfaces: HTML elements and selectors consumed by `taskboard/static/app.js` (te-sxk), and stylesheet hooks consumed by `taskboard/static/style.css` (te-rpb); load `/static/app.js` and `/static/style.css`.
- Depends on: <none>
- Consumed by: taskboard/main.py (te-hky), taskboard/static/app.js (te-sxk), taskboard/static/style.css (te-rpb)
- Acceptance:
  - The root page contains the TaskBoard heading, project-name input, create control, project list/selector, and visible status/error areas.
  - The document exposes the exact IDs/data attributes expected by the JavaScript and includes the API-driven UI without embedding a second framework or build step.
  - The page references the application stylesheet and script at the paths served by the app.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-sxk: taskboard/static/app.js
- Scope: Implement the browser client for loading projects, creating projects, deleting the selected project, and presenting success/error status in the template's controls.
- Architecture: `architecture.md` § `taskboard/static/app.js`; plain browser JavaScript using the SPEC API paths and the template selectors.
- Interfaces: DOM event handlers and `fetch` calls for `GET /api/projects`, `POST /api/projects`, and `DELETE /api/projects/{project_id}`; update the template's project list/selector and status/error regions.
- Depends on: taskboard/templates/index.html (te-fzd)
- Consumed by: taskboard/templates/index.html (te-fzd)
- Acceptance:
  - Initial load requests projects and renders returned names/IDs in the project control.
  - Submitting a nonblank name sends JSON to the create endpoint, then refreshes the list and clears/displays the appropriate status.
  - Delete invokes the exact selected-project endpoint and refreshes the list on success.
  - Non-2xx responses and API `error` messages are shown in the designated error region; no framework or build tooling is introduced.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-rpb: taskboard/static/style.css
- Scope: Supply plain CSS for the TaskBoard shell, heading, form controls, project selector/list, status/error regions, and usable narrow-window layout.
- Architecture: `architecture.md` § `taskboard/static/style.css`; no framework, animation, icon library, or frontend build.
- Interfaces: selectors/classes used by taskboard/templates/index.html (te-fzd) and taskboard/static/app.js (te-sxk).
- Depends on: <none>
- Consumed by: taskboard/templates/index.html (te-fzd)
- Acceptance:
  - The stylesheet is nonempty and styles every named shell/form/project/status/error region from the template.
  - Controls remain readable and usable at narrow viewport widths through the architecture's responsive rules.
  - Styling remains plain CSS and does not require an additional dependency or build command.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-j3i: taskboard/tests/conftest.py
- Scope: Provide the pytest client fixture with an isolated temporary SQLite database and reload the application factory for each test.
- Architecture: `architecture.md` § `taskboard/tests/conftest.py`; preserve the validated fixture contract using `TASKBOARD_DB_PATH`, `importlib.reload`, and FastAPI `TestClient`.
- Interfaces: pytest fixture `client`, yielding a TestClient configured against a per-test `tmp_path` database.
- Depends on: taskboard/main.py (te-hky)
- Consumed by: taskboard/tests/test_api.py (te-c2c)
- Acceptance:
  - Each test receives a working client backed by a unique temporary database.
  - The fixture configures the database path before reloading `taskboard.main`, creates the app through `create_app`, and closes the client after use.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-c2c: taskboard/tests/test_api.py
- Scope: Add focused API tests that prove the SPEC contract against the shared isolated client fixture.
- Architecture: `architecture.md` § `taskboard/tests/test_api.py`; tests exercise `taskboard.main` through HTTP rather than private implementation details.
- Interfaces: pytest tests for health, project create/list/delete, validation, missing deletion, persistence, response status, JSON fields, and empty 204 body.
- Depends on: taskboard/tests/conftest.py (te-j3i), taskboard/main.py (te-hky)
- Consumed by: phase-1-app QA verification
- Acceptance:
  - Assert exact health JSON and HTTP status.
  - Assert a fresh list is `[]`, valid creation returns 201 and exact fields, list ordering is ascending, and deletion returns 204 with an empty body.
  - Assert invalid or blank names return 400 with an `error` message and missing deletion returns 404 with the same error shape.
  - Assert persistence by creating a project and observing it in a subsequent list request through the same client/database.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase verification
Run exactly: `cd taskboard && python -m pytest -q tests`. QA must confirm all tests pass and that the six active-phase paths exist with the interfaces and behavior above. Do not add later-phase files or features.

## Future considerations
None for this phase; later-phase work remains outside these six beads.
