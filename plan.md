# Phase 1 app implementation plan

This phase delivers the runnable taskboard web application on top of the completed core
repository layer. Implement only the six active-phase paths below. Preserve the model and
repository contracts from phase 1 core; do not add later-phase features.

## Verification contract

From the rig working directory, run exactly:
`cd taskboard && python -m pytest -q tests`
The suite must exercise the Flask app through its test client, use an isolated temporary
database, and pass without requiring a separately running server. Acceptance is concrete:
the app imports and starts, serves the HTML shell and static assets, exposes the specified
project/task JSON operations, persists changes through the repository, returns JSON with
appropriate success/error status codes, and renders the board with the returned data.

## Bead map

### te-hit: taskboard/main.py
- Scope: Implement the application entry point, Flask app construction, template/static
  configuration, and the phase-1 project/task HTTP API described by SPEC.
- Architecture: Own the runnable Flask application and route wiring; use the existing
  `taskboard.db`, `taskboard.models`, and `taskboard.repository` contracts rather than
  duplicating persistence logic.
- Interfaces: Export the Flask application object/factory required by the tests and provide
  the SPEC routes for listing/creating projects and listing/creating/updating/deleting
  tasks. JSON request and response shapes must match SPEC, including ids, names, titles,
  descriptions, status, project association, and validation/error responses.
- Depends on: phase-1 core `taskboard/db.py`, `taskboard/models.py`, and
  `taskboard/repository.py`.
- Consumed by: `taskboard/tests/conftest.py`, `taskboard/tests/test_api.py`, and the
  browser assets through the documented HTTP routes.
- Acceptance: importing the module succeeds; GET `/` renders `index.html`; static files
  load; project creation and listing persist and return JSON; task creation, listing,
  update, and deletion use the repository and return the SPEC status codes; malformed or
  missing required input returns the specified client error without corrupting data.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-2qb: taskboard/templates/index.html
- Scope: Create the board page template and its semantic controls/containers.
- Architecture: Own the HTML shell served by `/`, including project selection, task
  creation/edit controls, task list/board container, and links to the static stylesheet
  and JavaScript module.
- Interfaces: Provide the DOM ids/classes and form fields consumed by
  `taskboard/static/app.js`, and load the app stylesheet and script using Flask static
  URLs.
- Depends on: `taskboard/main.py` route serving; consumed by `taskboard/static/app.js`
  and browser-level assertions in `taskboard/tests/test_api.py`.
- Acceptance: response to `/` contains the board shell, project/task controls and
  required script/style references; controls expose the fields named by SPEC and are
  usable without server-side template errors.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-ms3: taskboard/static/app.js
- Scope: Implement the browser client for loading projects/tasks and submitting the
  board's create, edit, status, and delete actions.
- Architecture: Own fetch-based interaction with the SPEC API routes and rendering the
  returned project/task data into the template's DOM.
- Interfaces: Use the exact HTTP paths and JSON field names from SPEC; bind to the
  template controls, refresh displayed data after mutations, and display the task
  title/description/status and project context.
- Depends on: `taskboard/templates/index.html` and `taskboard/main.py`; consumed by
  the rendered board.
- Acceptance: initial load fetches projects and tasks; selecting a project displays its
  tasks; submit/edit/delete actions send the documented methods and payloads; successful
  responses update the visible board; non-success responses are surfaced to the user
  rather than silently treated as success.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Provide the board presentation and responsive layout required by the SPEC.
- Architecture: Own styling for the page shell, project navigation, task cards/list,
  task form, status controls, and visible feedback states.
- Interfaces: Define the selectors/classes used by `index.html` and `app.js`; do not
  require additional backend endpoints or configuration.
- Depends on: `taskboard/templates/index.html`; consumed by the browser page.
- Acceptance: the stylesheet is served from the app static path, references no missing
  required assets, and gives the project/task controls, cards, status, and errors the
  distinct layout/visibility required by SPEC.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Configure pytest fixtures for an isolated application/client and temporary
  database for API tests.
- Architecture: Own test setup/teardown only; fixtures must construct the real app and
  initialize the repository schema without changing production behavior.
- Interfaces: Export the pytest fixtures consumed by `taskboard/tests/test_api.py`,
  including the application test client and isolated persistence context named by the
  architecture.
- Depends on: `taskboard/main.py` and phase-1 core database/repository modules;
  consumed by `taskboard/tests/test_api.py`.
- Acceptance: every test receives an isolated temporary store, the client can request
  `/`, setup is repeatable, and test data cannot leak between test cases.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Add the phase-1 API and app contract tests, using the real Flask client and
  fixtures.
- Architecture: Test the SPEC HTTP contract rather than implementation details.
- Interfaces: Exercise the exact project and task route paths, methods, JSON payloads,
  response fields, and status codes defined in SPEC.
- Depends on: `taskboard/tests/conftest.py` and all production app/template/static
  beads; validates `taskboard/main.py`.
- Acceptance: tests prove the index and static resources are available; project create
  and list work; task create/list/update/delete work and persist; project/task
  association and required fields are returned; invalid payloads receive the specified
  error response; and deletion removes the task from subsequent listing.
- Verify: `cd taskboard && python -m pytest -q tests`

## Delivery boundaries

Do not implement files belonging to later phases, add undocumented endpoints, or add
configuration and error behavior not required by SPEC. The existing core deviations
accepted by QA remain unchanged.
