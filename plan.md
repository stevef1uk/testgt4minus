# Implementation plan

## Active phase

Phase `phase-1-app` implements the runnable FastAPI application on top of the
completed core phase. The required verification is exactly:
`cd taskboard && python -m pytest -q tests`.
Only the six active-phase paths below are assigned here. Core repository and
model files are consumed as completed dependencies; later UI-content and
Playwright work is out of scope.

## Bead map

### te-1vt: taskboard/static/style.css
- Scope: Provide the stylesheet for the task board page, including the layout, project controls, board columns, cards, and the visible empty/loading/error states required by the page.
- Architecture: Static presentation asset owned by this phase; `main.py` serves it through the application’s static mount and `index.html` loads it.
- Interfaces: CSS selectors/classes used by `taskboard/templates/index.html`; no Python or JavaScript exports.
- Depends on: `<none>`
- Consumed by: `taskboard/main.py`; `taskboard/templates/index.html`
- Acceptance: The stylesheet is available at `/static/style.css`; the rendered page has the project/sidebar and board layout, usable form/control styling, and readable status/error/empty states without adding features outside SPEC.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-2qb: taskboard/templates/index.html
- Scope: Implement the server-rendered single-page shell with the project creation form, project list, board container, and the DOM hooks used by the client script.
- Architecture: Template owned by this phase; it is rendered by `main.py` and references `/static/style.css` and `/static/app.js`.
- Interfaces: HTML element IDs/classes and form controls consumed by `taskboard/static/app.js`; links to the two static asset URLs; no file dependency on `app.js` (the script is a runtime asset, not a build/input dependency).
- Depends on: `<none>`
- Consumed by: `taskboard/main.py`; `taskboard/static/app.js` consumes its DOM contract at runtime
- Acceptance: `GET /` returns the template with the required title, project form, project list/selection area, board columns, and static asset references; all JavaScript query targets exist and are semantic/usable.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-ms3: taskboard/static/app.js
- Scope: Implement browser behavior for loading projects, creating a project, selecting a project, and rendering the API result into the template’s project and board regions.
- Architecture: Client asset owned by this phase; it calls the phase-1 project API exposed by `main.py` and is loaded by `index.html`.
- Interfaces: Browser-side DOM event handlers and `fetch` calls for the SPEC project endpoints; consumes the IDs/classes and form controls defined in `taskboard/templates/index.html`; no exported Python symbols.
- Depends on: `<none>` (the HTML is a runtime DOM contract, not a file dependency)
- Consumed by: `taskboard/templates/index.html` loads `/static/app.js`; `taskboard/main.py` serves the static directory
- Acceptance: On page load the script requests the project list and renders it; submitting the project form sends the required create request and refreshes the list; project selection updates the selected state/board; failed requests show the prescribed visible error rather than silently failing.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-hit: taskboard/main.py
- Scope: Build the FastAPI application, configure the database path and completed repository/model dependencies, mount static files, render `/`, and implement the SPEC project API with its exact response shapes and status behavior.
- Architecture: Application entrypoint owns `create_app`, route registration, template/static wiring, and translation between HTTP payloads and repository operations.
- Interfaces: `create_app(database_path: str | None = None)` application factory; `GET /` HTML response; the SPEC-defined project list/create/select API routes and their JSON contracts; static files under `/static`.
- Depends on: `taskboard/db.py`, `taskboard/models.py`, `taskboard/repository.py` (completed phase); `taskboard/templates/index.html`; `taskboard/static/app.js`; `taskboard/static/style.css`
- Consumed by: `taskboard/tests/conftest.py`, `taskboard/tests/test_api.py`
- Acceptance: The factory can create an isolated app using `TASKBOARD_DB_PATH` or its explicit path; startup initializes the existing schema/repository layer; `GET /` renders successfully; project list and creation endpoints persist and return the required fields; duplicate/invalid input produces the SPEC-required error status and body; static assets are served at their declared URLs.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Provide the pytest `client` fixture with a temporary SQLite database, environment isolation, module reload, and a TestClient for the application factory.
- Architecture: Test support owned by this phase and deliberately isolates each test from repository data.
- Interfaces: pytest fixture named `client`, yielding a FastAPI `TestClient`.
- Depends on: `taskboard/main.py`
- Consumed by: `taskboard/tests/test_api.py`
- Acceptance: Each test receives a fresh temporary database; `TASKBOARD_DB_PATH` is set before importing/reloading the app; the fixture yields a usable client and closes it after the test.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Add API and page contract tests proving the runnable app behavior against the isolated `client` fixture.
- Architecture: API test coverage owned by this phase; tests are the executable evidence for the SPEC project and application requirements.
- Interfaces: pytest tests use the `client` fixture and public HTTP routes only; no implementation internals are asserted as an API.
- Depends on: `taskboard/tests/conftest.py`, `taskboard/main.py`
- Consumed by: phase-1-app verification and QA
- Acceptance: Tests prove `GET /` returns HTML and references the static assets; project listing returns the required empty and populated JSON shape; project creation accepts valid data and persists it; the required validation/duplicate failure status and response are asserted; repeated requests demonstrate database isolation through the fixture.
- Verify: `cd taskboard && python -m pytest -q tests`

## Dependency and scope notes

The active file dependency graph is acyclic: static/template inputs and the
completed core are consumed by `main.py`; the test fixture consumes the app;
the API tests consume the fixture and app. `app.js` may query template DOM hooks
at runtime, but must not declare `index.html` as a file dependency. Do not add
task CRUD, Kanban behavior, filters, content tests, package manifests, or
browser tests in this phase; those belong to later phases.
