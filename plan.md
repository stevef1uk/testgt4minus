# Implementation plan

## Active phase: phase-1-app

This phase delivers the runnable Taskboard application layer and its browser assets/tests. Scope is limited to the six active-phase paths; backend, frontend, and later-phase paths in architecture.md are not implemented here. The implementation must preserve the validated core data/schema behavior and use the existing project-local test command.

## Bead map

### tm-5dk: taskboard/main.py
- Scope: Implement the FastAPI application factory and the runnable Taskboard HTTP layer, using the completed core persistence behavior and serving the template/static assets from the documented locations.
- Architecture: architecture.md sections for `taskboard/main.py`, application factory, API routes, and static/template serving; follow the SPEC HTTP/API contract and data shapes exactly.
- Interfaces / Depends on: Provide the documented `create_app(...)` application factory and the health, project, and task route handlers specified by SPEC/architecture. Depends on `taskboard/tests/conftest.py` only as a consumer fixture contract and on the completed core storage modules described by architecture.md.
- Consumed by: `taskboard/tests/conftest.py`, `taskboard/tests/test_api.py`, and the browser assets through the documented HTTP endpoints.
- Acceptance:
  - A fresh application created by the documented factory initializes a database-backed app and responds to `GET /api/health` with HTTP 200 and `{"status":"ok"}`.
  - The documented project and task endpoints accept the SPEC request payloads, persist records, and return the specified status codes, JSON fields, and identifiers; subsequent reads return the created data.
  - Project/task listing and lookup behavior, including the SPEC empty-result behavior and not-found behavior, matches the architecture contract.
  - The app renders the index template and exposes the static JavaScript/CSS paths needed by the UI; the API and page work with a database path supplied through the documented configuration.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ff6: taskboard/tests/conftest.py
- Scope: Supply the pytest client fixture used by the API tests, with an isolated temporary SQLite database for every test.
- Architecture: architecture.md testing section and the fixture contract in the SPEC delivery requirements.
- Interfaces / Depends on: Export the pytest `client` fixture. Depends on `taskboard/main.py` and its documented `create_app` factory; consumed by `taskboard/tests/test_api.py`.
- Consumed by: `taskboard/tests/test_api.py`.
- Acceptance:
  - Each test receives a fresh database path through `TASKBOARD_DB_PATH`, reloads the application against that path, and gets a usable FastAPI `TestClient`.
  - The fixture proves startup by asserting the database exists and `GET /api/health` returns 200 with exactly `{"status":"ok"}`.
  - No test uses state left by another test.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-j2d: taskboard/tests/test_api.py
- Scope: Implement API and page-level tests that prove the phase-1 app contract rather than merely exercising implementation details.
- Architecture: architecture.md test plan and the SPEC endpoint/response table.
- Interfaces / Depends on: Consume the `client` fixture from `taskboard/tests/conftest.py` and the public HTTP contract from `taskboard/main.py`; no private persistence implementation is required.
- Consumed by: CI acceptance for this phase.
- Acceptance:
  - Tests cover health success and the index page response, including the expected HTML/static integration.
  - Tests cover the SPEC project and task create/list/read/update/delete flows, request validation, response status codes, and response JSON fields.
  - Tests verify relationships and ordering/filter behavior required by SPEC, plus the documented empty and missing-resource responses.
  - The complete suite passes with isolated temporary databases.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-c2q: taskboard/templates/index.html
- Scope: Build the single-page Taskboard markup, including the project/task controls, lists, forms, identifiers, and script/style references required by the SPEC UI.
- Architecture: architecture.md template ownership and SPEC browser behavior.
- Interfaces / Depends on / Consumed by: Depends on the API paths and JSON shapes owned by `taskboard/main.py`; consumed by `taskboard/static/app.js` and the browser via the index route.
- Acceptance:
  - The rendered page contains the documented project and task sections, creation controls, task fields, and empty-state containers.
  - Element IDs/classes and form controls match the JavaScript selectors and support selecting a project, creating a project/task, and displaying returned records.
  - The template references the phase-owned stylesheet and JavaScript at the documented static paths and does not require an unlisted framework or endpoint.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Implement the browser-side Taskboard flow using the public API: load data, render projects/tasks, submit forms, and reflect success/error states required by SPEC.
- Architecture: architecture.md frontend behavior and endpoint integration sections.
- Interfaces / Depends on / Consumed by: Depends on the DOM contract in `taskboard/templates/index.html` and the documented API routes/JSON from `taskboard/main.py`; consumed by the index page.
- Acceptance:
  - On page load the script requests the documented project/task resources and renders the returned records into the matching template containers.
  - Project and task form submissions send the SPEC payloads and refresh or update the visible lists without a full-page navigation.
  - Selecting a project scopes the displayed tasks as specified; empty results and API failures are represented using the template's documented UI state.
  - JavaScript uses only the phase-owned DOM elements and API paths, with no invented backend contract.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Provide the documented responsive visual layout and states for the Taskboard page, forms, project/task lists, controls, and empty/error messaging.
- Architecture: architecture.md stylesheet ownership and SPEC UI requirements.
- Interfaces / Depends on / Consumed by: Depends on the class/id contract in `taskboard/templates/index.html`; consumed by that template and the browser.
- Acceptance:
  - The page has distinct project and task regions, readable controls/forms, visible selected/empty/error states, and the responsive layout required by SPEC.
  - Styles target the template's actual selectors and load without external assets or unrequested configuration.
  - The stylesheet preserves usable presentation for the documented create/select interactions on narrow and wide viewports.
- Verify: `cd taskboard && python -m pytest -q tests`

## Verification and boundaries

The phase gate is exactly `cd taskboard && python -m pytest -q tests`. Do not add later-phase modules or unrequested features. Acceptance is satisfied only when the API tests and the complete existing test suite pass and all six paths are present at their exact required locations.

## Future considerations

Later delivery phases may add paths listed in architecture.md outside this phase. They are intentionally excluded from these beads and from this plan.
