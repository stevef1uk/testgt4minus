# Phase-2 implementation plan: Tasks and Kanban UI

Phase 2 extends the existing Phase-1 application in place. The seven active
paths are covered by the beads below. The required verification command is:

    cd taskboard && python -m pytest -q tests

No alternate page, duplicate asset, new framework, or new route is allowed.
Repository SQL remains in `taskboard/repository.py`, HTTP wiring remains in
`taskboard/main.py`, and browser behavior remains in `taskboard/static/app.js`.

## Bead map

### te-h52: taskboard/static/app.js
- Scope: Implement the vanilla-JavaScript project and Kanban workflow.
- Architecture: `taskboard/static/app.js` owns browser API calls, state, safe rendering, filtering, editing, moving, and deletion.
- Interfaces: Consume `GET/POST /api/projects`, `DELETE /api/projects/{project_id}`, `GET/POST /api/projects/{project_id}/tasks`, `PATCH /api/tasks/{task_id}`, and `DELETE /api/tasks/{task_id}`; consume the DOM contract from `taskboard/templates/index.html`.
- Depends on: `taskboard/templates/index.html`; existing `taskboard/main.py` routes and JSON contracts.
- Consumed by: Browser users and `taskboard/tests/test_ui_content.py`.
- Acceptance: Load and display projects; create, select, and confirmed-delete projects; create tasks with title, description, and priority; render cards in To Do, Doing, and Done; edit title/description/priority; delete tasks; and move `todo` to `doing` to `done` through PATCH. Hide or disable Move forward for done cards. Apply status and priority filters through API query parameters, refresh after mutations, and show visible empty and API-error states. Use `textContent` for user data, `replaceChildren` for rendered collections, and no raw user-content `innerHTML`.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Extend the existing stylesheet in place for the complete phase-2 dashboard.
- Architecture: `taskboard/static/style.css` owns responsive presentation for forms, cards, columns, filters, and visual state regions.
- Interfaces: Style the semantic IDs/classes supplied by `taskboard/templates/index.html`; do not implement application behavior.
- Depends on: `taskboard/templates/index.html`.
- Consumed by: The rendered root page and `taskboard/tests/test_ui_content.py`.
- Acceptance: Keep the three Kanban columns, task cards, project/task forms, filters, loading, empty, and error messages usable on desktop and narrow windows. Preserve the template's `/static/style.css` asset contract and add no framework or animation requirement.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xa1: taskboard/templates/index.html
- Scope: Extend the real Phase-1 page into the complete TaskBoard shell.
- Architecture: `taskboard/templates/index.html` owns semantic forms, project selector/list, filters, Kanban columns, and state regions.
- Interfaces: Provide project creation and selection controls, task form and edit controls, status/priority filters, delete-project control, `To Do`, `Doing`, `Done`, and `project-form-region`, `project-form`, `project-list`, `project-filter`, `empty-state`, `loading-state`, and `error-state` regions.
- Depends on: Existing `taskboard/main.py` template rendering and static mounts.
- Consumed by: `taskboard/static/app.js` and `taskboard/tests/test_ui_content.py`.
- Acceptance: `GET /` remains real HTML containing the `TaskBoard` heading, project form, task form, all three column headings, selector/list, filters, and state regions. Reference `/static/app.js` and `/static/style.css`; use native accessible controls; contain no database calls or inline application logic.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Preserve an isolated FastAPI test client fixture for all phase tests.
- Architecture: `taskboard/tests/conftest.py` owns the temporary database path, `TASKBOARD_DB_PATH` setup, app reload, `create_app`, and `TestClient` lifecycle.
- Interfaces: Provide the `client` pytest fixture consumed by `taskboard/tests/test_api.py` and UI integration tests.
- Depends on: Existing `taskboard.main.create_app`.
- Consumed by: `taskboard/tests/test_api.py`, `taskboard/tests/test_ui_content.py`, and the full pytest gate.
- Acceptance: Each test receives a temporary SQLite database, application initialization honors that path, the runtime database is never touched, and the client context closes correctly.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Preserve and expand repository assertions for the task domain.
- Architecture: Repository tests cover idempotent schema setup, ascending IDs, defaults, UTC timestamps, status/priority filters including AND, partial updates, and project cascade deletion.
- Interfaces: Assert public repository behavior rather than SQL internals or HTTP behavior.
- Depends on: Existing `taskboard/db.py`, `taskboard/models.py`, and `taskboard/repository.py`.
- Consumed by: The phase pytest gate and QA review.
- Acceptance: Tests prove empty initial collections, deterministic project/task ordering, task creation defaults, valid explicit-UTC timestamps, status and priority filtering alone and together, preservation of omitted PATCH fields, and deletion of a project cascading to its tasks. Assertions must inspect returned state, not only execution or status.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Preserve and expand HTTP contract tests for projects and tasks.
- Architecture: API tests cover exact routes, JSON shapes, status codes, validation, empty arrays, bodyless deletes, ordering, and composed filters.
- Interfaces: Use the isolated `client` fixture and the exact SPEC routes: `/api/health`, `/api/projects`, `/api/projects/{project_id}/tasks`, and `/api/tasks/{task_id}`.
- Depends on: `taskboard/tests/conftest.py`, existing `taskboard/main.py`, and repository behavior.
- Consumed by: The phase pytest gate and QA review.
- Acceptance: Assert exact health JSON; project and task create/list/patch/delete round trips; trimmed valid values and defaults; 400 for empty/invalid fields, invalid enums, oversized title/description, and empty PATCH; 404 for missing projects/tasks; `[]` for empty lists; empty bodies for 204 responses; and ascending IDs with status and priority filters combined using AND.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-uz4: taskboard/tests/test_ui_content.py
- Scope: Add substantive rendered-page and static-asset integration assertions.
- Architecture: `taskboard/tests/test_ui_content.py` owns root-page and static-content checks, not persistence implementation.
- Interfaces: Exercise the application client and inspect `GET /`, `/static/app.js`, and `/static/style.css`.
- Depends on: `taskboard/tests/conftest.py`, `taskboard/templates/index.html`, `taskboard/static/app.js`, and `taskboard/static/style.css`.
- Consumed by: The phase pytest gate and QA review.
- Acceptance: Assert root HTML contains `TaskBoard`, project and task forms, `To Do`, `Doing`, and `Done`, selector/filter controls, and empty/loading/error regions. Assert both static responses are 200 and nonempty. Assert JavaScript includes `/api/projects`, `textContent`, and `replaceChildren`, proving required wiring and safe rendering rather than merely checking status.
- Verify: `cd taskboard && python -m pytest -q tests`

## Delivery order and completion

Implement the template and stylesheet contract before relying on their DOM from
JavaScript; keep the isolated fixture and existing repository/API assertions
green while extending them; then complete the UI content assertions. The full
phase gate must pass. The resulting UI must support project selection,
task creation, move-forward transitions, edit, delete, filtering, and visible
empty/error states. Do not add authentication, persistence features outside
SPEC, alternate paths, or Phase-3 Playwright files.
