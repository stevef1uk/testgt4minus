# Phase 2 Implementation Plan — Tasks and Kanban UI

## Scope and verification

This plan covers only the active `phase-2` required files. Phase 1 already
owns the package, database foundation, project application, template, static
assets, fixture, repository tests, and API tests; this phase extends those
canonical files in place and adds the UI-content test. The implementation must
follow SPEC.md and architecture.md exactly: task SQL remains in the repository,
validation remains in models, HTTP routes remain in main, and browser behavior
remains in static/app.js. Do not add alternate pages, route aliases, or files
from phase 3.

The phase gate is exactly:

    cd taskboard && python -m pytest -q tests

The gate must demonstrate real task state changes, not merely nonempty files.
All tests must continue to use isolated temporary SQLite databases.

## Bead map

### te-fzd: taskboard/templates/index.html
- Scope: Extend the existing real TaskBoard page with the phase-2 project/task controls and Kanban regions.
- Architecture: `taskboard/templates/index.html` owns semantic forms, project selector/list, filters, three columns, and loading/empty/error regions; it contains no database calls or inline application logic.
- Interfaces: Provides the DOM regions and controls consumed by `taskboard/static/app.js`, including project creation, project selection/deletion, task creation/editing/deletion, status columns headed To Do, Doing, and Done, and visible feedback regions.
- Depends on: `<none>` for file ownership; preserve phase-1 page and static links.
- Consumed by: `taskboard/static/app.js`; `taskboard/tests/test_ui_content.py`.
- Acceptance: Root HTML contains heading `TaskBoard`, project creation input and `Add project`, project selector/list and delete control, task title/description/priority form and `Add task`, status and priority filter controls, three visible columns, and explicit loading, empty, and error regions. It loads `/static/app.js` and `/static/style.css`, uses native HTML controls, and does not embed user data or inline JavaScript.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-rpb: taskboard/static/style.css
- Scope: Extend presentation for the task form, project controls, task cards, Kanban columns, and feedback states.
- Architecture: `taskboard/static/style.css` owns responsive presentation only; it does not contain application data or behavior.
- Interfaces: Styles the semantic regions/classes emitted by `taskboard/templates/index.html` and rendered by `taskboard/static/app.js`.
- Depends on: `taskboard/templates/index.html`.
- Consumed by: the rendered TaskBoard page and `taskboard/tests/test_ui_content.py`.
- Acceptance: Controls and task cards are readable and usable; To Do, Doing, and Done are visually distinct columns; cards expose title and priority styling; loading, empty, and error states remain visible and distinguishable; desktop and narrow-window layouts remain usable. No drag-and-drop, animation, framework, or inline-style requirement is introduced.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-sxk: taskboard/static/app.js
- Scope: Implement phase-2 browser state, API calls, safe rendering, project selection, task lifecycle controls, and Kanban movement.
- Architecture: `taskboard/static/app.js` owns browser API calls and DOM behavior. Task routes are project-scoped: `GET/POST /api/projects/{project_id}/tasks`, `PATCH/DELETE /api/projects/{project_id}/tasks/{task_id}`; project routes are `/api/projects` and `/api/projects/{project_id}`.
- Interfaces: Consumes the controls from `taskboard/templates/index.html`; calls the exact SPEC routes; renders project and task JSON into the page; uses `textContent` and DOM replacement rather than raw user-content HTML.
- Depends on: `taskboard/templates/index.html`, `taskboard/static/style.css`, and the existing `taskboard.main` API.
- Consumed by: `taskboard/tests/test_ui_content.py` and the real browser UI.
- Acceptance: On load, fetch and render projects and select a project; create and delete projects; create tasks with title, description, and priority; render tasks in To Do/Doing/Done; edit title/description/priority; delete tasks; move todo→doing→done through Move forward and hide/disable it for done. Show loading, selected-project empty, no-project empty, and visible API-error states. Preserve user text with `textContent`/`replaceChildren`; never inject user input as raw `innerHTML`. Keep API errors visible and use only SPEC behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-j3i: taskboard/tests/conftest.py
- Scope: Preserve and extend isolated pytest application fixtures for repository/API phase-2 tests.
- Architecture: `taskboard/tests/conftest.py` supplies a temporary `TASKBOARD_DB_PATH`, reloads `taskboard.main`, calls `create_app`, and yields a FastAPI `TestClient`.
- Interfaces: Exports the `client` pytest fixture consumed by `taskboard/tests/test_repository.py` and `taskboard/tests/test_api.py`.
- Depends on: existing `taskboard.main.create_app`; `tmp_path` and pytest.
- Consumed by: `taskboard/tests/test_repository.py`, `taskboard/tests/test_api.py`.
- Acceptance: Every test uses a fresh temporary database, schema initialization occurs through `create_app`, the environment path is explicit, TestClient lifecycle is closed, and runtime `taskboard.db` is not touched. Fixture changes must not weaken existing project coverage.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Extend repository tests from project CRUD to the complete task persistence lifecycle.
- Architecture: Exercise `ProjectRepository`/`TaskRepository` and the architecture-defined repository functions; SQL remains behind repository APIs and project deletion cascades through the foreign key.
- Interfaces: Tests repository task create/list/update/delete and `list_tasks(project_id, status, priority)` behavior; consumes the existing database/model/repository implementation and isolated test setup.
- Depends on: phase-1 `taskboard/db.py`, `taskboard/models.py`, `taskboard/repository.py`; `taskboard/tests/conftest.py`.
- Consumed by: the phase pytest gate and implementation feedback for `taskboard/main.py`.
- Acceptance: Prove task creation defaults status to `todo` and priority to `medium`, preserves description and UTC timestamps, returns ascending IDs, filters by status, priority, and both together, partially updates title/description/priority/status while preserving omitted fields, deletes tasks, and confirms project deletion cascades to tasks. Preserve empty-list, project CRUD, schema-idempotence, and validation coverage required by SPEC.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-c2c: taskboard/tests/test_api.py
- Scope: Extend API tests to the exact phase-2 task routes while retaining the phase-1 project and health contract.
- Architecture: Use FastAPI TestClient against the project-scoped routes: `GET/POST /api/projects/{project_id}/tasks`, `PATCH/DELETE /api/projects/{project_id}/tasks/{task_id}`, plus project routes from SPEC.
- Interfaces: Consumes `client` from `taskboard/tests/conftest.py`; asserts JSON shapes, HTTP status codes, error objects, empty arrays, and empty 204 bodies.
- Depends on: `taskboard/tests/conftest.py`, existing `taskboard.main.create_app`, repository/model behavior.
- Consumed by: the phase pytest gate and `taskboard/static/app.js` API integration.
- Acceptance: Verify exact health JSON and project CRUD remain passing; verify task create/list/patch/delete round trips, project scoping, defaults, status transitions, composed status+priority filters, ascending order, empty lists, 201/200/204 responses, and bodyless deletes. Verify 400 for empty/invalid title, description, priority, status, and empty PATCH; 404 for missing project/task; allow framework 422 for malformed integer paths; assert the SPEC error object and no unspecified behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-w1w: taskboard/tests/test_ui_content.py
- Scope: Add content integration assertions for the real phase-2 HTML and JavaScript contract.
- Architecture: Test canonical `taskboard/templates/index.html` and `taskboard/static` content without replacing browser or API tests.
- Interfaces: Reads the template and app.js/style.css; verifies the page and static assets that the browser consumes.
- Depends on: `taskboard/templates/index.html`, `taskboard/static/app.js`, `taskboard/static/style.css`.
- Consumed by: the phase pytest gate and later browser-test phase.
- Acceptance: Assert `TaskBoard`, both project/task forms, project selector/filter and loading/empty/error regions, and all three exact column headings are present. Assert `/static/app.js` and `/static/style.css` references and nonempty static content. Assert app.js references the exact project-scoped task routes, uses `textContent` and `replaceChildren`, and contains the required Move forward/edit/delete and filter behavior without raw user-content `innerHTML`.
- Verify: `cd taskboard && python -m pytest -q tests`

## Dependency order

Implement and test the template/CSS contract, then wire app.js. Preserve the
phase-1 fixture before extending repository/API tests, and run the complete
phase command after integration. No phase-3 Playwright or npm files belong in
this plan.
