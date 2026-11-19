# Implementation plan

## Scope and verification

This phase delivers the runnable Taskboard web application on top of the completed
SQLite model/repository foundation. Implement only the six active-phase paths below;
later UI/browser and packaging paths remain out of scope. The polecat must preserve
the existing repository interfaces and use the application contract in SPEC.md.
Required verification is `cd taskboard && python -m pytest -q tests`.

## Bead map

### te-hit: taskboard/main.py
- Scope: Build the FastAPI application factory, configure the database from
  `TASKBOARD_DB_PATH` (and the explicit factory path used by tests), serve the
  index template/static assets, and expose the SPEC task CRUD HTTP API.
- Architecture: architecture.md, application entrypoint section; this module owns
  `create_app` and the HTTP route handlers and translates repository records to
  JSON.
- Interfaces: `create_app(database_path: str | None = None)` returns the FastAPI
  application; provide the SPEC routes for listing tasks, creating a task,
  partially updating a task, deleting a task, and serving `/`. Preserve the
  documented JSON field names, status/filter query parameters, HTTP methods, and
  success status codes.
- Depends on: taskboard/models.py, taskboard/repository.py, taskboard/db.py
  (completed foundation)
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py,
  taskboard/templates/index.html, taskboard/static/app.js
- Acceptance: a TestClient can create, list, update, and delete tasks through the
  exact SPEC `/api/tasks` routes; list filtering and conjunction behavior match
  the repository contract; responses contain stable IDs, UTC timestamps, defaults,
  and the documented validation/error status; `/` returns the index template and
  static resources are reachable.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-2qb: taskboard/templates/index.html
- Scope: Provide the complete single-page taskboard markup, semantic task form,
  filter controls, task list container, edit/delete controls, and links to the
  application stylesheet and script.
- Architecture: architecture.md UI template section; IDs/classes and data
  attributes are the DOM contract consumed by app.js and asserted by tests.
- Interfaces: expose the SPEC-required page title, task input fields, filter
  controls, submit button, task-list/status containers, and static asset links;
  keep the exact selectors named in the architecture.
- Depends on: taskboard/main.py
- Consumed by: taskboard/static/app.js, taskboard/static/style.css,
  taskboard/tests/test_api.py
- Acceptance: GET `/` renders a non-empty HTML document containing the required
  form and filter elements, task list target, accessible labels, and references
  to `/static/app.js` and `/static/style.css`; no server-side feature outside
  the SPEC is added.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-ms3: taskboard/static/app.js
- Scope: Implement the browser client for loading tasks, submitting new tasks,
  applying the documented filters, editing completion/title data, deleting
  tasks, and rendering the returned task collection into the template.
- Architecture: architecture.md frontend behavior section; use the template's
  selectors and the SPEC API routes rather than duplicating persistence logic.
- Interfaces: issue fetch requests to the exact SPEC `/api/tasks` endpoints with
  the documented query/body fields; bind the template form, filter, edit, and
  delete controls and render IDs, titles, statuses, and timestamps.
- Depends on: taskboard/main.py, taskboard/templates/index.html
- Consumed by: taskboard/tests/test_api.py, taskboard/static/style.css
- Acceptance: initial load displays API tasks; create, filter, update, and delete
  actions issue the correct HTTP method/path and refresh visible state; empty
  results and API failures produce the SPEC-required visible state; rendering
  does not invent routes or unsupported fields.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Style the page shell, form, filter row, task cards/list, status
  indicators, action controls, and responsive layout using the template classes.
- Architecture: architecture.md stylesheet section; selectors must correspond to
  the HTML contract and support the documented completed/pending presentation.
- Interfaces: define the classes and layout rules referenced by
  `taskboard/templates/index.html` and `taskboard/static/app.js`, including
  visible completed-task and empty-list states.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/main.py, browser/UI assertions in later phases
- Acceptance: the stylesheet is served successfully, contains rules for the
  required page/form/list/filter/action selectors, and visually distinguishes
  task status without requiring a new dependency or unrequested theme feature.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Supply the isolated pytest `client` fixture for API tests, using a
  temporary SQLite database and reloading the application after setting
  `TASKBOARD_DB_PATH`.
- Architecture: architecture.md test-fixture section; tests must exercise the
  public FastAPI app without sharing state between cases.
- Interfaces: provide pytest fixture `client` yielding a FastAPI
  `TestClient` created from `taskboard.main.create_app`.
- Depends on: taskboard/main.py, taskboard/db.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: each test receives an isolated temporary database, the environment
  variable is honored, and the fixture cleans up the TestClient context after
  yielding; do not add global or production persistence changes.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Add the phase API contract tests using the client fixture, covering
  page/static serving and the full task lifecycle plus filters and validation.
- Architecture: architecture.md API test section; assertions must be black-box
  HTTP assertions against SPEC routes and payloads.
- Interfaces: tests use the `client` fixture and the public `create_app` behavior;
  cover exact verbs, paths, request fields, response fields, and status codes
  specified in SPEC.md.
- Depends on: taskboard/tests/conftest.py, taskboard/main.py
- Consumed by: phase QA verification
- Acceptance: tests prove empty listing, creation with defaults and UTC timestamp,
  ascending IDs, conjunction filters, partial update, cascade deletion, index
  rendering, static asset responses, and the SPEC-defined invalid-request
  behavior; assertions must fail if route names, JSON keys, or status codes drift.
- Verify: `cd taskboard && python -m pytest -q tests`

## Definition of done

All six beads are implemented with no stubs or unrelated features, the API and
page use the completed core repository rather than a second data model, and the
exact phase command passes.
