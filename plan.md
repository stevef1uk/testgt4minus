# Implementation plan

## Active phase

This plan covers only delivery phase `phase-1-app` (runnable app), after
`phase-1-core`. Implement exactly the six required paths below. The phase
verification command is:

`cd taskboard && python -m pytest -q tests`

Phase-1-app must provide the initial runnable application and project
functionality. Task-management behavior, Kanban interactions, and filters are
later-phase extensions and are not acceptance criteria for this plan.

## Bead map

### te-hky: taskboard/main.py
- Scope: Build the FastAPI application factory, module-level app, schema
  initialization wiring, health endpoint, project endpoints, root template
  response, and `/static` mounting.
- Architecture: Follow architecture.md “HTTP + entrypoint integration” and
  the `taskboard/main.py` module-ownership row. Export
  `create_app(db_path: str | None = None) -> FastAPI` and retain the documented
  `app = create_app()` entrypoint.
- Interfaces: Provide `GET /api/health` returning exactly
  `{"status":"ok"}`, `GET /api/projects`, `POST /api/projects` returning 201,
  `DELETE /api/projects/{project_id}` returning 204, `GET /`, and static
  serving for `/static/app.js` and `/static/style.css`. Use the selected
  database path through app state and repository operations, not a mutable
  global connection.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py,
  taskboard/templates/index.html
- Acceptance: `create_app` accepts an explicit temporary database path and
  initializes it; health JSON and status are exact; project creation trims and
  persists valid names; project listing is JSON and ordered by ID; missing
  project deletion returns the documented error response; successful deletion
  has status 204 and no body; `/` returns real HTML and both static assets are
  reachable. Preserve FastAPI's default 422 behavior for malformed integer
  paths.

### te-fzd: taskboard/templates/index.html
- Scope: Create the real phase-1 TaskBoard HTML shell with project creation,
  project selection/list region, and the initial page regions required for the
  runnable app.
- Architecture: Follow the template ownership row in architecture.md:
  semantic markup only, no database calls or inline application logic. The
  document is rendered by `taskboard/main.py` and references the canonical
  `/static/app.js` and `/static/style.css` assets.
- Interfaces: Provide the `TaskBoard` heading, project-name input, `Add
  project` button, project selector/list container, and stable semantic
  elements for JavaScript to populate projects. Include the phase-1 page shell
  without inventing alternate routes or a second page.
- Depends on: taskboard/main.py (te-hky), taskboard/static/app.js (te-sxk), taskboard/static/style.css (te-rpb)
- Consumed by: taskboard/main.py and browser users
- Acceptance: A GET `/` response contains a non-placeholder HTML document, the
  `TaskBoard` heading, project form/control, and project region; it loads both
  canonical static files; it uses native HTML and contains no server-side
  database code or raw user-data injection.

### te-sxk: taskboard/static/app.js
- Scope: Supply the phase-1 vanilla JavaScript needed to load, display, create,
  select, and delete projects through the documented project API.
- Architecture: Follow the `taskboard/static/app.js` ownership row. Use the
  template's stable elements and exact `/api/projects` routes; do not add task,
  filter, or alternate navigation behavior before its owning phase.
- Interfaces: Own page initialization, project-list rendering, project-create
  submission, project selection state, and project-delete requests. Consume
  the project controls and regions from `index.html`.
- Depends on: taskboard/main.py (te-hky)
- Consumed by: taskboard/templates/index.html (te-fzd)
- Acceptance: Loading the page requests projects and renders returned names;
  adding a valid project sends the documented payload and refreshes visible
  state; deleting the selected project uses confirmation and refreshes the
  selection; API failures are shown in the page's visible error region rather
  than silently treated as success. User-provided project text is inserted
  safely with `textContent` or equivalent DOM APIs.

### te-rpb: taskboard/static/style.css
- Scope: Provide the phase-1 presentation for the TaskBoard shell, project
  controls, project list, buttons, error region, and narrow-window usability.
- Architecture: Follow the stylesheet ownership row in architecture.md:
  plain static CSS only, with no application data or JavaScript behavior.
- Interfaces: Style the selectors/classes supplied by the canonical template
  and provide readable layout and visible controls without requiring a build
  step.
- Depends on: <none>
- Consumed by: taskboard/templates/index.html (te-fzd) and browser users
- Acceptance: The rendered phase-1 page has readable project/form regions,
  visible buttons and errors, and remains usable on a narrow viewport. The
  stylesheet is nonempty, served at `/static/style.css`, and introduces no
  framework or out-of-scope visual feature.

### te-j3i: taskboard/tests/conftest.py
- Scope: Provide the isolated pytest `client` fixture for API integration
  tests.
- Architecture: Follow the conftest ownership row: use `tmp_path`, set
  `TASKBOARD_DB_PATH`, reload `taskboard.main`, call `create_app` with the
  temporary path, and yield FastAPI `TestClient` in a context manager.
- Interfaces: Export the pytest `client` fixture consumed by
  `taskboard/tests/test_api.py`.
- Depends on: taskboard/main.py (te-hky)
- Consumed by: taskboard/tests/test_api.py (te-c2c)
- Acceptance: Every test receives a working isolated client and temporary
  SQLite file; no test touches the runtime database; startup and shutdown are
  exercised; fixture state does not leak between tests.

### te-c2c: taskboard/tests/test_api.py
- Scope: Write substantive phase-1 API and rendered-content tests against the
  public TestClient, following TDD and the SPEC contract.
- Architecture: Follow the API-test ownership row and the SPEC API/content
  test contract; assert behavior through HTTP rather than private internals.
- Interfaces: Test the public health, project CRUD, root HTML, and static asset
  responses provided by `taskboard/main.py`.
- Depends on: taskboard/tests/conftest.py (te-j3i), taskboard/main.py (te-hky)
- Consumed by: <none>
- Acceptance: Assertions prove exact health JSON; project create/list/delete
  round trips, ascending IDs, trimming, 400 invalid names, 404 missing
  deletion, and bodyless 204 success; empty project lists serialize as `[]`;
  root HTML contains the real TaskBoard heading and project form; both static
  responses are 200 and nonempty. Tests run with
  `cd taskboard && python -m pytest -q tests`.

## Dependency and verification notes

The dependency graph is acyclic: the app depends on phase-1-core, the
fixture depends on the app, and API tests depend on the fixture. The template
references both static assets, but the static files do not depend on the
template; this avoids a template/CSS or template/JavaScript dependency cycle.
The polecat must follow the TDD red-green-refactor sequence and run the exact
phase verification command after implementation. Do not add phase-2 task
routes or phase-3 browser manifests to this bead set.
