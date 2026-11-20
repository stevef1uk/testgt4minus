# Phase 2 implementation plan: Tasks and Kanban UI

This phase implements the browser-facing taskboard UI and its phase-2 test
coverage. Keep the existing backend contracts intact. The required verification
command for every bead and for the phase is:
`cd taskboard && python -m pytest -q tests`

## Bead map

### te-xsd: taskboard/tests/conftest.py
- Scope: Provide the isolated pytest `client` fixture, using a temporary SQLite database, `TASKBOARD_DB_PATH`, reloaded `taskboard.main`, `create_app`, and FastAPI `TestClient`.
- Architecture: Architecture test-support section; fixture must isolate each test database and expose the application through the existing factory.
- Interfaces / Depends on: Exports pytest fixture `client`; depends on `taskboard/main.py` and its `create_app` factory (existing phase-1 provider).
- Consumed by: te-7yg (`taskboard/tests/test_repository.py`), te-oj5 (`taskboard/tests/test_api.py`), and the phase test suite.
- Acceptance: Tests receive a working TestClient backed by a fresh temporary database; the environment variable is set before application creation; application imports are reloaded so the fixture database is honored; teardown closes the client.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-2qb: taskboard/templates/index.html
- Scope: Build the semantic taskboard page, including project form region/form, project list, project filter, loading, empty, and error states, and links to the static assets.
- Architecture: UI template section; preserve the required element IDs and the `/static/app.js` and `/static/style.css` asset URLs.
- Interfaces / Depends on: Provides the HTML consumed by `taskboard/static/app.js` and asserted by te-zch; depends on the existing FastAPI template/static mounting.
- Consumed by: te-ms3, te-1vt, te-zch.
- Acceptance: Rendered page contains `project-form-region`, `project-form`, `project-list`, `project-filter`, `empty-state`, `loading-state`, and `error-state`; it loads both required static assets; controls are usable and labels/regions support the project/task workflow described by SPEC.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Style the taskboard layout as a responsive Kanban UI with project controls, columns/cards, form feedback, loading/empty/error states, and accessible focus/contrast treatment.
- Architecture: Static stylesheet section; selectors must target the template's stable regions and the classes used by the JavaScript renderer without changing API behavior.
- Interfaces / Depends on: Provides stylesheet at `/static/style.css`; depends on te-2qb's markup and te-ms3's rendered class structure.
- Consumed by: te-zch and browser-facing UI.
- Acceptance: Projects and task columns are visually grouped as a Kanban board; project/filter controls and state messages are styled; layout remains usable on narrow screens; no CSS requirement adds features outside SPEC.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-ms3: taskboard/static/app.js
- Scope: Implement client-side loading, project listing/filtering, project creation, task-board rendering, and UI state transitions against the existing `/api/projects` contract.
- Architecture: Static JavaScript section; use safe text rendering and replace children rather than injecting untrusted project/task values as HTML.
- Interfaces / Depends on: Provides browser module behavior and calls `/api/projects`; depends on te-2qb DOM IDs and existing API routes from `taskboard/main.py`.
- Consumed by: te-1vt's class hooks, te-zch, and the rendered page.
- Acceptance: Initial load requests and displays projects; filter updates the visible project set; project creation submits the form and refreshes visible data; loading, empty, and error states are represented; task columns/cards show the API data; code contains safe `textContent` rendering and `replaceChildren`, and uses `/api/projects`; failures are surfaced in the error region.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-zch: taskboard/tests/test_ui_content.py
- Scope: Add content-level regression tests for required template regions, static asset links, and safe/API-aware JavaScript behavior.
- Architecture: UI test section; tests inspect repository files directly and remain independent of a running server.
- Interfaces / Depends on: Reads te-2qb (`templates/index.html`) and te-ms3 (`static/app.js`); no new production exports.
- Consumed by: phase-2 acceptance and future UI regression checks.
- Acceptance: Assert the HTML contains all seven required IDs; assert `/static/app.js` and `/static/style.css` links; assert JavaScript contains `textContent`, `/api/projects`, and `replaceChildren`.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Preserve and complete repository-level tests for project/task persistence, ordering, filtering, and the phase-1 storage contract used by the UI.
- Architecture: Repository test section; exercise the public repository/database behavior rather than implementation details.
- Interfaces / Depends on: Depends on the existing `taskboard/repository.py`, `taskboard/models.py`, and `taskboard/db.py`; may use te-xsd's isolated fixture only where the architecture test setup requires it.
- Consumed by: te-oj5 and the full acceptance suite.
- Acceptance: Prove projects can be created and retrieved; task records and their project association persist; the documented ordering/filter behavior is stable; separate tests do not share database state; assertions match the SPEC's repository behavior without adding undocumented validation.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Test the HTTP API consumed by the new UI, including project listing/creation and the task/project response shape and documented failure responses.
- Architecture: API test section; use the isolated FastAPI client and assert status codes and JSON contracts from SPEC.
- Interfaces / Depends on: Depends on te-xsd's `client` fixture and existing `taskboard/main.py` routes, plus te-7yg's persistence contract.
- Consumed by: te-ms3 and phase-2 API/UI acceptance.
- Acceptance: Assert the SPEC routes accept valid project input and return the documented JSON; list responses reflect created projects and associated tasks; malformed or missing required input receives the documented client error; API responses are usable by the JavaScript without undocumented fields or route changes.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase acceptance

Run `cd taskboard && python -m pytest -q tests`. The phase passes only when
the complete suite is green and the UI tests demonstrate the required regions,
asset wiring, safe rendering, and `/api/projects` integration while repository
and API tests continue to prove the SPEC contracts.
