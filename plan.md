# Phase-2 implementation plan: Tasks and Kanban UI

## Scope and verification

Implement only the seven phase-2 required paths listed below. The UI must provide the project form/list/filter, explicit loading and error states, and the static assets needed by the taskboard page. The phase also carries the validated pytest fixtures and tests that define the repository/API contract; do not add later-phase backend or server-entrypoint files here. The polecat must run the phase verification from the working directory:
`cd taskboard && python -m pytest -q tests`

## Bead map

### te-w1w: taskboard/tests/test_ui_content.py
- Scope: Keep the focused UI-content tests that inspect the rendered template and JavaScript source.
- Architecture: Phase-2 UI verification; `taskboard/templates/index.html`, `taskboard/static/app.js`, and `taskboard/static/style.css` are the page assets.
- Interfaces / Depends on / Consumed by: Depends on taskboard/templates/index.html and taskboard/static/app.js; `<none>` exported. Consumed by the phase test command.
- Acceptance: Assert the template contains `project-form-region`, `project-form`, `project-list`, `project-filter`, `empty-state`, `loading-state`, and `error-state`; assert `/static/app.js` and `/static/style.css` are loaded; assert the app uses `textContent`, `replaceChildren`, and `/api/projects` rather than unsafe HTML rendering.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-fzd: taskboard/templates/index.html
- Scope: Build the accessible page shell and all required Kanban/project UI regions, with the form, filter, list, empty/loading/error states, and static asset references.
- Architecture: Phase-2 template ownership; the browser page is served from the template and references `/static/app.js` and `/static/style.css`.
- Interfaces / Depends on / Consumed by: Provides DOM IDs `project-form-region`, `project-form`, `project-list`, `project-filter`, `empty-state`, `loading-state`, and `error-state`; depends on no phase-2 implementation bead; consumed by taskboard/static/app.js and taskboard/tests/test_ui_content.py.
- Acceptance: The HTML includes a project creation form and project filter/list regions with the exact required IDs; it includes initially controllable empty, loading, and error elements; it loads `/static/app.js` and `/static/style.css`; controls have usable labels and the page remains a coherent no-data view.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-sxk: taskboard/static/app.js
- Scope: Implement client-side loading, rendering, filtering, and project-form behavior for the taskboard UI using the documented projects API.
- Architecture: Phase-2 browser behavior; client requests use `/api/projects`, and DOM updates use safe text rendering and replacement.
- Interfaces / Depends on / Consumed by: Provides browser behavior for the template IDs `project-form`, `project-list`, `project-filter`, `empty-state`, `loading-state`, and `error-state`; depends on taskboard/templates/index.html and the phase API contract exercised by taskboard/tests/test_api.py; consumed by taskboard/tests/test_ui_content.py and end users in the browser.
- Acceptance: Fetch and display projects from `/api/projects`; submit the project form through the documented API and refresh the list; filter visible projects from the filter control; show loading, empty, and error states at the appropriate times; render server-provided values with `textContent` and update collections with `replaceChildren`; do not introduce routes outside the SPEC.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-rpb: taskboard/static/style.css
- Scope: Style the page shell, project form, filter, project list/cards, and visible loading/empty/error states into a usable Kanban-oriented layout.
- Architecture: Phase-2 static presentation asset paired with `index.html`; no backend or additional configuration is owned here.
- Interfaces / Depends on / Consumed by: Provides `/static/style.css`; depends on the class/ID hooks in taskboard/templates/index.html; consumed by taskboard/tests/test_ui_content.py and the browser page.
- Acceptance: The stylesheet is loaded by the template; it visibly distinguishes form, filter, list, cards, loading, empty, and error regions; it supports a readable responsive layout without changing API behavior or requiring unlisted features.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-j3i: taskboard/tests/conftest.py
- Scope: Provide the isolated FastAPI test client fixture and temporary database setup used by phase tests.
- Architecture: Test support uses `TASKBOARD_DB_PATH`, reloads `taskboard.main`, calls `create_app`, and yields a `TestClient`.
- Interfaces / Depends on / Consumed by: Provides the pytest `client` fixture; depends on the phase-1 `taskboard.main.create_app` application factory and FastAPI test dependencies; consumed by taskboard/tests/test_api.py and taskboard/tests/test_repository.py.
- Acceptance: Each test receives a database under `tmp_path`; `TASKBOARD_DB_PATH` is set for the test; the application is reloaded and created with the temporary path; the fixture yields a working `TestClient` and closes it after use.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Preserve the repository contract tests supplied by the architecture for project/task persistence and ordering/filter behavior.
- Architecture: Repository tests exercise the documented phase-1 persistence interface through the isolated fixture; this bead adds no new production module.
- Interfaces / Depends on / Consumed by: Depends on taskboard/tests/conftest.py and the repository symbols defined by architecture; consumed by the phase test command and later implementation phases.
- Acceptance: Cover creation and retrieval of projects/tasks, stable identifiers and timestamps as specified, persistence across operations, and the documented filtering/order behavior; use the temporary database and assert the exact returned values required by SPEC, without adding unspecified error cases.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-c2c: taskboard/tests/test_api.py
- Scope: Preserve the HTTP contract tests for the project/task API used by the browser client.
- Architecture: API tests use the `client` fixture and the exact routes, methods, JSON fields, status codes, and response behavior specified in SPEC.
- Interfaces / Depends on / Consumed by: Depends on taskboard/tests/conftest.py and the phase-1 `taskboard.main.create_app`; consumed by taskboard/static/app.js and the phase test command.
- Acceptance: Exercise the documented project list/create and task/board endpoints, asserting exact HTTP methods and paths, successful status codes, JSON response shape, persistence between requests, and the specified validation responses; verify an empty project list is represented as required by SPEC.
- Verify: `cd taskboard && python -m pytest -q tests`

## Integration and sequencing

Implement the fixture/tests and template contracts before relying on browser behavior: `index.html` establishes DOM hooks, `app.js` consumes them, and `style.css` decorates them. The API and repository tests remain contract tests for the already-owned backend interfaces; do not create backend files in phase-2. Run the single stated pytest command after all seven paths are present.

## Phase-2 concrete acceptance checklist

The active gate is exactly `cd taskboard && python -m pytest -q tests`. Acceptance is limited to phase-2 extensions of the phase-1 application and its seven required paths. The root page must remain real HTML with the `TaskBoard` heading, project creation form, task form, and visible `To Do`, `Doing`, and `Done` headings. The project selector/list is populated by `GET /api/projects`; selecting a project loads its tasks. A user can create a task with title, description, and low/medium/high priority, see it in the correct Kanban column, edit title/description/priority, move it todo→doing→done, and delete it. A done task hides or disables Move forward. Project deletion uses `window.confirm`, removes its tasks, and refreshes selection. Empty project/task collections show an empty-state message, while failed API operations show a visible error state.

The API and repository tests must preserve all phase-1 assertions while proving the phase-2 task contract: task defaults and timestamps; status and priority filtering, including AND composition and ascending ID order; partial PATCH updates preserving omitted fields; validation of empty/overlong title and description and invalid enums; missing project/task 404s; empty PATCH 400; task create/list/update/delete round trips; project cascade deletion; empty arrays; and bodyless 204 responses. The UI-content tests must assert the root response contains TaskBoard, both project/task forms, all three column headings, and the required state regions, and must assert both static assets return nonempty content. User-provided task title and description must be inserted with `textContent`, never raw `innerHTML`; the JavaScript must use the exact documented `/api/projects` and project-scoped task routes. No filters, Playwright files, package files, alternate routes, backend files, or other phase-3 work belongs in this phase.

## Delivery order and dependency edges

`taskboard/tests/conftest.py` supplies an isolated temporary database and client for `taskboard/tests/test_repository.py` and `taskboard/tests/test_api.py`. Those tests exercise the existing phase-1 factory/repository while specifying the task extension. `taskboard/templates/index.html` owns the DOM hooks and forms; `taskboard/static/app.js` consumes those hooks and the API; `taskboard/static/style.css` styles the hooks and visible states. `taskboard/tests/test_ui_content.py` verifies the template and static assets. Implement tests before production extensions per the TDD standard, then run the exact phase gate above. All seven beads remain one bead per required path and no additional bead is introduced.
