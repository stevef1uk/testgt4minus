# Implementation plan

This phase delivers the runnable Taskboard web application on top of the completed
core persistence layer. Implement only the six active-phase paths below; preserve
the validated core behavior and keep all runtime paths relative to `taskboard/`.
The required verification command for every bead is:
`cd taskboard && python -m pytest -q tests`.

## Bead map

### te-hky: taskboard/main.py
- Scope: Provide the FastAPI application factory and the HTTP/UI integration described by SPEC and architecture, using the existing SQLite-backed project/task store rather than duplicating persistence logic.
- Architecture: `taskboard/main.py` owns application construction, the `/` HTML response, static-file mounting, and the project/task JSON routes in the SPEC HTTP table. Preserve the documented `create_app(...)` entry point and the existing database-path/environment behavior.
- Interfaces: Export the architecture-defined `create_app(database_path=None)` application factory; expose the configured FastAPI application and the exact SPEC routes for listing/creating/deleting projects and listing/creating/updating/deleting tasks, including the documented query filtering.
- Depends on: <none> (consume the completed core implementation already present in the repository).
- Consumed by: taskboard/tests/conftest.py (te-j3i), taskboard/tests/test_api.py (te-c2c), taskboard/templates/index.html (te-fzd), taskboard/static/app.js (te-sxk).
- Acceptance: the root page renders successfully and serves the UI; API responses use the SPEC status codes and JSON shapes; project and task CRUD, required-field validation, project filtering, task filtering, and cascading deletion remain functional; timestamps are UTC as specified; the app serves the static assets without changing the core contract.

### te-fzd: taskboard/templates/index.html
- Scope: Implement the complete single-page markup required by the SPEC, with semantic project/task sections, controls, forms, and stable selectors for the JavaScript behavior.
- Architecture: Template ownership is the browser shell returned by `/`, including project creation, project selection/filtering, task creation/editing, completion controls, deletion controls, and the status/filter UI named by SPEC.
- Interfaces: Provide the exact DOM IDs/classes/data attributes consumed by `taskboard/static/app.js` (te-sxk), and load the application stylesheet and script from the mounted static paths.
- Depends on: taskboard/main.py (te-hky) for the rendered route and static mounting; taskboard/static/style.css (te-rpb) for presentation.
- Consumed by: taskboard/static/app.js (te-sxk); browser/UI assertions in taskboard/tests/test_api.py (te-c2c).
- Acceptance: response HTML contains the project and task forms, project list, task list, task status/filter controls, and the documented edit/delete affordances; form labels and controls are usable; assets resolve at the paths expected by the app; no unrelated UI feature is added.

### te-sxk: taskboard/static/app.js
- Scope: Implement the browser client that loads data, renders projects and tasks, submits the forms, applies the documented filters, and updates/deletes records through the API.
- Architecture: Own the single-page event handlers and rendering described in the architecture, using the HTTP endpoints and JSON fields from the SPEC rather than embedding server-side state.
- Interfaces: Call the exact project/task API paths and methods from the SPEC; bind to the selectors exported by `taskboard/templates/index.html` (te-fzd); update the DOM and selected project/filter state after successful operations.
- Depends on: taskboard/main.py (te-hky) for API routes and response shapes; taskboard/templates/index.html (te-fzd) for DOM contract; taskboard/static/style.css (te-rpb) for state classes.
- Consumed by: taskboard/templates/index.html (te-fzd); taskboard/tests/test_api.py (te-c2c) where the UI shell/assets are asserted.
- Acceptance: initial load displays projects and tasks; selecting a project and task status filter changes the visible list; create, edit/complete, and delete actions send the documented requests and refresh the relevant view; validation failures are surfaced in the UI; no speculative client-side features are introduced.

### te-rpb: taskboard/static/style.css
- Scope: Supply the architecture-defined layout and visual states for the taskboard shell, forms, project/task lists, filters, completed tasks, and action controls.
- Architecture: This file owns presentation only; it must support the template selectors and state classes without moving behavior into CSS or adding a framework.
- Interfaces: Define selectors/classes used by `taskboard/templates/index.html` (te-fzd) and `taskboard/static/app.js` (te-sxk), including the documented completed/selected/hidden states.
- Depends on: taskboard/templates/index.html (te-fzd) for markup selectors.
- Consumed by: taskboard/templates/index.html (te-fzd) and taskboard/static/app.js (te-sxk).
- Acceptance: the stylesheet is served by the app, styles the documented controls and lists, visibly distinguishes selected project and completed tasks, and provides the responsive/layout rules required by SPEC; keep it free of application logic and unrelated design systems.

### te-j3i: taskboard/tests/conftest.py
- Scope: Provide the pytest fixture that isolates each test database and creates the application through the architecture-defined factory.
- Architecture: Use a temporary SQLite path, set `TASKBOARD_DB_PATH`, reload `taskboard.main` as needed for environment isolation, and yield a FastAPI `TestClient` for the complete test suite.
- Interfaces: Export the pytest `client` fixture consumed by taskboard/tests/test_api.py (te-c2c).
- Depends on: taskboard/main.py (te-hky).
- Consumed by: taskboard/tests/test_api.py (te-c2c).
- Acceptance: each test receives an independent database; the fixture yields a usable client; environment/database state does not leak between tests; setup uses only the public app factory and does not rewrite production data.

### te-c2c: taskboard/tests/test_api.py
- Scope: Add the phase-1-app black-box tests that prove the runnable app and its UI/API integration against the SPEC.
- Architecture: Test through the `client` fixture and the documented HTTP contract; retain coverage of validation, CRUD, filtering, cascading deletion, and UTC timestamps while adding root/static and app-level integration checks.
- Interfaces: Import/use the `client` fixture from taskboard/tests/conftest.py (te-j3i) and exercise the exact routes owned by taskboard/main.py (te-hky).
- Depends on: taskboard/tests/conftest.py (te-j3i); taskboard/main.py (te-hky).
- Consumed by: phase verification and QA.
- Acceptance: tests assert the root page is rendered, CSS/JS assets are reachable, project creation/listing/deletion works, task creation/update/completion/deletion works, invalid payloads return the SPEC responses, project and status filters select the expected records, deleting a project removes its tasks, and returned timestamps are UTC-formatted. Tests must assert real response content and remain deterministic with no network dependency.
- Verify: `cd taskboard && python -m pytest -q tests`

## Cross-file delivery order

Implement the application contract first, then the template and stylesheet selectors,
then the browser behavior, then the isolated fixture and black-box tests. Before
handoff, run the exact verification command above from the `taskboard` directory
and confirm that all six paths are present, non-stubbed, and covered by the bead map.

## Future considerations

None for this phase. Features not stated in SPEC are intentionally out of scope.
