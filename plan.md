# Phase 2 implementation plan: Tasks and Kanban UI

Phase 2 extends the Phase 1 application in place. Implement only the seven
active-phase paths below; do not add alternate application modules or a server
entrypoint. Preserve all Phase 1 repository, project API, HTML, and static
asset behavior. The required gate is `cd taskboard && python -m pytest -q tests`.

## Bead map

### te-7yg: taskboard/tests/test_repository.py
- Scope: Extend repository coverage for task persistence and operations using the existing SQLite repository.
- Architecture: `taskboard/repository.py` owns parameterized task create, list, update, delete, and status-transition persistence; task rows retain project ownership and use the schema constraints from Phase 1.
- Interfaces: Exercise the repository's existing project and task operations as specified by `architecture.md`; verify returned task data, project association, edits, deletion, and status changes.
- Depends on: taskboard/tests/conftest.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Tests prove tasks can be created for a project, listed, edited, moved to the next Kanban status, and deleted; they prove persistence and project selection rather than only response shapes, and preserve the existing repository assertions.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Keep the isolated test application/database fixture usable for the expanded task and UI/API tests.
- Architecture: The fixture reloads `taskboard.main`, supplies a temporary `TASKBOARD_DB_PATH`, and yields a FastAPI `TestClient` against `create_app`.
- Interfaces: `client` pytest fixture; `taskboard.main.create_app` application factory.
- Depends on: `<none>`
- Consumed by: taskboard/tests/test_repository.py, taskboard/tests/test_api.py, taskboard/tests/test_ui_content.py
- Acceptance: Each test gets an isolated temporary database and a working application client; Phase 1 tests continue to pass without shared state.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Add API and end-to-end state-change assertions for task routes while retaining project and health coverage.
- Architecture: `taskboard/main.py` owns the task API, exact status codes, validation/errors, and database selection; routes follow the SPEC HTTP contract for task list/create/update/delete and move-forward.
- Interfaces: Exercise the SPEC task endpoints under `/api/projects/{project_id}/tasks` and the task update/delete and move-forward routes, with the exact JSON fields and statuses defined in SPEC.
- Depends on: taskboard/tests/conftest.py, te-xsd; taskboard/tests/test_repository.py, te-7yg
- Consumed by: `<none>`
- Acceptance: Tests create a project, create a task, list it, edit its title/details/priority as specified, move it forward through the three Kanban statuses, delete it, and assert each persisted state change; invalid payloads/project selection and missing resources produce the SPEC-mandated responses; health and project CRUD assertions remain green.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xa1: taskboard/templates/index.html
- Scope: Extend the real root page with project selection, task creation/edit controls, Kanban columns, and visible loading/empty/error regions.
- Architecture: `taskboard/templates/index.html` is the real HTML entrypoint mounted by the app and provides the stable IDs and controls consumed by `static/app.js` and UI-content tests.
- Interfaces: Root document; `/static/app.js` and `/static/style.css` asset references; project form/list/filter, task form/list, three Kanban status columns, and loading/empty/error elements required by SPEC.
- Depends on: `<none>`
- Consumed by: taskboard/static/app.js, taskboard/static/style.css, taskboard/tests/test_ui_content.py
- Acceptance: Root HTML contains project selection and task create/edit/delete UI, visibly labels the three Kanban columns, exposes a move-forward control, includes required empty/loading/error states, and loads the real static assets with the required accessible/stable selectors.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-h52: taskboard/static/app.js
- Scope: Implement browser behavior for project selection, task CRUD, Kanban rendering, and move-forward interactions against the Phase 2 API.
- Architecture: `taskboard/static/app.js` owns client-side fetch/render behavior and safe DOM updates for the routes and controls in the template; it must preserve project behavior and use the SPEC task/status model.
- Interfaces: Browser calls to the SPEC `/api/projects` and project-task routes; DOM handlers for project selection, task create/edit/delete, and move-forward; safe text rendering via the existing page regions.
- Depends on: taskboard/templates/index.html, te-xa1
- Consumed by: taskboard/tests/test_ui_content.py
- Acceptance: Selecting a project loads its tasks; create, edit, delete, and move-forward actions call the correct API and refresh visible state; tasks render in exactly the three status columns; empty, loading, and request-error states are visible; user-controlled values are inserted safely and required project behavior remains intact.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Style the task/project UI, Kanban layout, controls, and visible state regions without changing the API contract.
- Architecture: `taskboard/static/style.css` owns presentation for the real template, including the three-column Kanban view and responsive readable states.
- Interfaces: CSS selectors/classes emitted by `templates/index.html` and used by the task/project controls; no new route or dependency.
- Depends on: taskboard/templates/index.html, te-xa1
- Consumed by: `<none>`
- Acceptance: The page visibly presents three distinct Kanban columns, usable task/project forms and controls, and distinguishable loading, empty, and error states; the stylesheet is delivered by the real `/static/style.css` path and does not remove Phase 1 UI.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-uz4: taskboard/tests/test_ui_content.py
- Scope: Add static/content regression checks for the Phase 2 task and Kanban interface.
- Architecture: UI-content tests verify the canonical template and static files, while API tests verify runtime state changes; this file must remain focused on required visible structure and safe rendering.
- Interfaces: Reads `taskboard/templates/index.html`, `taskboard/static/app.js`, and `taskboard/static/style.css` from repository-relative paths.
- Depends on: taskboard/templates/index.html, te-xa1; taskboard/static/app.js, te-h52; taskboard/static/style.css, te-1vt
- Consumed by: `<none>`
- Acceptance: Assertions prove required project/task regions and controls exist, all three Kanban columns and empty/loading/error states are represented, real static asset links are present, task API route strings are used, and safe text rendering is used; the test suite remains compatible with Phase 1 assertions.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase acceptance and boundaries

The phase is complete only when the full pytest command passes and demonstrates real
create, move-forward, edit, and delete state changes. Task validation, project
selection, exact API responses, and visible UI states must match SPEC; do not add
filters, browser/Playwright infrastructure, extra routes, aliases, deployment
mechanisms, or unrelated dependencies (those belong to later phases).
