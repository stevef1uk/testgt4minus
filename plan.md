# Implementation plan

## Phase 2: Tasks and Kanban UI

The phase delivers the browser-facing TaskBoard shell and the phase-specific test
coverage. All acceptance is behavioral: tests must exercise the real FastAPI
application and real static/template files rather than merely checking that a
path exists. The phase gate is:

    cd taskboard && python -m pytest -q tests

## Bead map

### te-w1w: taskboard/tests/test_ui_content.py
- Scope: Keep focused content tests for the rendered template and browser bundle.
- Architecture: UI content checks in the phase-2 test layer; the template owns the
  required regions and static asset links, while app.js owns safe DOM rendering
  and project API usage.
- Interfaces / Depends on / Consumed by: Reads taskboard/templates/index.html,
  taskboard/static/app.js, and taskboard/static/style.css; no server symbol is
  imported. Depends on taskboard/templates/index.html and taskboard/static/app.js.
  Consumed by the phase verification command.
- Acceptance: Assert index.html contains the TaskBoard heading and the
  project-form-region, project-form, project-list, project-filter, empty-state,
  loading-state, and error-state IDs. Assert the form has the project input and
  submit controls required by the SPEC, and assert the page references exactly
  /static/app.js and /static/style.css. Assert app.js uses textContent and
  replaceChildren rather than unsafe HTML insertion, and contains the
  /api/projects integration used by the UI.
- Verify: cd taskboard && python -m pytest -q tests

### te-fzd: taskboard/templates/index.html
- Scope: Implement the complete single-page TaskBoard document and its project
  form, list, filtering, loading, empty, and error regions.
- Architecture: Jinja template and semantic UI regions defined for phase 2;
  static files are served at /static/app.js and /static/style.css.
- Interfaces / Depends on / Consumed by: Provides the HTML contract consumed by
  test_ui_content.py and app.js DOM selectors. Depends on the phase-2 static
  asset paths. Consumed by the application root response and test_ui_content.py.
- Acceptance: Render a page with visible TaskBoard heading; include all required
  IDs project-form-region, project-form, project-list, project-filter,
  empty-state, loading-state, and error-state; include the project name/title
  input and submit affordance; include filter controls and status messaging
  regions; load /static/app.js and /static/style.css with valid script/link
  elements. Do not put server-side project data or a second API contract in the
  template.
- Verify: cd taskboard && python -m pytest -q tests

### te-sxk: taskboard/static/app.js
- Scope: Implement browser behavior for loading, filtering, creating, and
  rendering projects through the existing API contract.
- Architecture: Vanilla browser module owns DOM event wiring, fetch calls to
  /api/projects, state/status updates, and safe project-card rendering.
- Interfaces / Depends on / Consumed by: Consumes the IDs exported by
  taskboard/templates/index.html and the project JSON/error contract exposed by
  the API. Depends on taskboard/templates/index.html and the API routes already
  implemented by earlier phases. Consumed by index.html and test_ui_content.py.
- Acceptance: On page load fetch the project collection; render returned project
  fields into the project list; submit the project form through the create
  endpoint and refresh/render the result; send the selected filter in the list
  request and update the visible list. Show loading, empty, and error regions in
  their corresponding states. Use textContent/createElement or replaceChildren
  for user-controlled values, never innerHTML for project data. Use the exact
  /api/projects route and handle the API's JSON error shape without inventing a
  second route.
- Verify: cd taskboard && python -m pytest -q tests

### te-rpb: taskboard/static/style.css
- Scope: Style the TaskBoard layout, form, project list/cards, filter, and state
  messages without changing behavior.
- Architecture: Static stylesheet paired with index.html's semantic regions.
- Interfaces / Depends on / Consumed by: Consumes the classes and IDs emitted by
  taskboard/templates/index.html; no Python or API dependency. Consumed by the
  browser root page and test_ui_content.py.
- Acceptance: Provide readable styling for the heading, project form, list/cards,
  filter controls, and loading/empty/error states; keep state regions
  distinguishable and the list usable at narrow widths; ensure the stylesheet
  is loadable from /static/style.css. Do not add a competing framework or
  alter the required DOM/API contract.
- Verify: cd taskboard && python -m pytest -q tests

### te-j3i: taskboard/tests/conftest.py
- Scope: Provide an isolated FastAPI TestClient fixture for every API and
  repository test.
- Architecture: pytest fixture sets TASKBOARD_DB_PATH to tmp_path, reloads
  taskboard.main, creates the application with that database path, and yields
  TestClient.
- Interfaces / Depends on / Consumed by: Provides the client fixture consumed
  by test_repository.py and test_api.py. Depends on taskboard.main.create_app
  and FastAPI TestClient. Consumed by the phase pytest command.
- Acceptance: Each test receives a fresh SQLite path under tmp_path; the
  environment variable is patched, taskboard.main is reloaded, and
  create_app(database_path) is used. The yielded client is entered and closed
  as a context manager, preventing state leakage between tests.
- Verify: cd taskboard && python -m pytest -q tests

### te-7yg: taskboard/tests/test_repository.py
- Scope: Test the repository's required CRUD and filtering behavior against an
  isolated database.
- Architecture: Repository tests cover schema initialization, project creation,
  retrieval, status updates, and status filtering from the phase contract.
- Interfaces / Depends on / Consumed by: Calls the repository functions and
  symbols defined by the earlier repository implementation, using the fixture
  from conftest.py. Consumed by the phase pytest command and test_api.py as
  behavioral evidence.
- Acceptance: Assert the schema/database is initialized in the configured
  temporary database; creating a project returns its identifier and persisted
  name/title/status/timestamps. Assert list returns persisted projects in the
  specified ordering, a status filter includes matching projects and excludes
  nonmatching projects, and updating a project changes its status while
  preserving its identity and other fields. Assert lookup of a missing project
  follows the SPEC's not-found result rather than fabricating a row.
- Verify: cd taskboard && python -m pytest -q tests

### te-c2c: taskboard/tests/test_api.py
- Scope: Exercise the exact HTTP contract for project listing, creation,
  updates, filtering, validation, and not-found responses.
- Architecture: FastAPI route tests use the isolated client and assert status
  codes, JSON fields, and documented error shapes, including query filtering.
- Interfaces / Depends on / Consumed by: Consumes the application returned by
  conftest.py's create_app fixture and the repository-backed routes; consumed
  by the phase pytest command.
- Acceptance: Assert GET /api/projects returns the documented collection JSON
  and fields. Assert POST /api/projects accepts a valid project payload and
  returns the documented success status and persisted fields. Assert the
  project update route returns the updated project, and GET filtering by the
  documented status/query parameter returns only matching projects. Assert
  malformed or missing required input returns the SPEC validation status and
  JSON error shape, and an unknown project returns the documented 404 and error
  body. Assert route responses do not leak HTML or traceback text.
- Verify: cd taskboard && python -m pytest -q tests

## Phase verification

Run exactly . The successful run must
cover the UI content assertions, isolated repository CRUD/filter assertions, and
the API's exact success, filtering, validation, and not-found response
contracts.

## Future considerations

Later phases may extend backend or deployment concerns; this phase does not add
routes, configuration, or behavior not specified by the active contract.
