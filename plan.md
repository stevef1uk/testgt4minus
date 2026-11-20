# Phase 2 implementation plan — Tasks and Kanban UI

## Scope and verification

Implement only the active phase-2 extensions to the existing TaskBoard application. The canonical paths are the seven phase-2 required files below; extend phase-1 files in place and do not create alternate UI, API, repository, or test paths. Acceptance is grounded in SPEC.md sections 4–7 and architecture.md sections “Module / bead ownership,” “Unit tests,” and “Requirements / phase-2”. The required verification command is:

`cd taskboard && python -m pytest -q tests`

The tests must exercise real persisted state and rendered content, not placeholder status checks. Follow TDD for each testable change: add or extend the relevant test first, observe the expected failure, then implement the smallest matching behavior.

## Bead map

### te-xsd: taskboard/tests/conftest.py
- Scope: Preserve an isolated temporary SQLite database and FastAPI TestClient fixture while phase-2 repository and task routes are added.
- Architecture: architecture.md module ownership for `taskboard/tests/conftest.py`; consume `taskboard.main.create_app(db_path: str | None = None) -> FastAPI`.
- Interfaces: pytest fixture `client`; selected database is supplied through `TASKBOARD_DB_PATH` and/or `create_app`.
- Depends on: taskboard/main.py (phase-1)
- Consumed by: taskboard/tests/test_repository.py, taskboard/tests/test_api.py
- Acceptance: each test receives a fresh temporary database; tests never touch runtime `taskboard.db`; schema initialization and client teardown remain reliable while task operations are exercised.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Extend repository coverage for task creation, defaults, filtering, partial updates, ordering, and cascade deletion.
- Architecture: architecture.md repository ownership and Unit tests; use `TaskRepository`/task repository functions and exact SPEC task JSON fields.
- Interfaces: assert `list_tasks(project_id, status=None, priority=None)`, `create_task(...)`, `update_task(task_id, changes)`, and `delete_task(task_id)` behavior.
- Depends on: taskboard/repository.py (phase-1), taskboard/models.py (phase-1), taskboard/tests/conftest.py
- Consumed by: taskboard/tests/test_api.py, phase-2 verification
- Acceptance: prove empty/idempotent setup; project and task IDs are ascending; new tasks default to `todo` and `medium`; status, priority, and combined filters use AND; partial updates preserve omitted fields; invalid task fields are rejected according to SPEC; deleting a project cascades to its tasks; timestamps carry explicit UTC offsets.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Extend HTTP contract tests for task routes while preserving project and health coverage.
- Architecture: architecture.md exact HTTP route integration and API test ownership.
- Interfaces: exercise GET/POST `/api/projects/{project_id}/tasks`, PATCH/DELETE `/api/tasks/{task_id}`, and existing project routes; assert documented 200/201/204/400/404 responses.
- Depends on: taskboard/repository.py (phase-1), taskboard/main.py (phase-1), taskboard/tests/conftest.py, taskboard/tests/test_repository.py
- Consumed by: taskboard/static/app.js, phase-2 verification
- Acceptance: prove task create/list/patch/delete round trips, default values, composed query filters and ID ordering; reject empty titles, invalid status/priority, overlong title/description, and empty PATCH payload with the specified error format; return 404 for missing projects/tasks; verify empty arrays and bodyless 204 responses.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xa1: taskboard/templates/index.html
- Scope: Extend the existing real page with project selection/deletion, task creation/edit controls, filter controls, three Kanban columns, and visible loading/empty/error regions.
- Architecture: architecture.md template ownership; semantic forms and DOM contract, with no database calls or inline application logic.
- Interfaces: retain `project-form`, `project-list`, `project-filter`, `empty-state`, `loading-state`, and `error-state`; provide task form, status/priority filters, columns headed exactly `To Do`, `Doing`, and `Done`, and controls consumed by app.js.
- Depends on: <none> (extends the phase-1 template contract)
- Consumed by: taskboard/static/app.js, taskboard/tests/test_ui_content.py
- Acceptance: GET `/` remains real HTML with heading `TaskBoard`; page contains project form and selector/list, task title/description/priority form, Add project/Add task controls, delete-project control, both filter dropdowns, all three column headings, and state regions; links `/static/app.js` and `/static/style.css` remain present.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-h52: taskboard/static/app.js
- Scope: Implement vanilla-JS project selection and deletion, task loading/creation/edit/delete, todo→doing→done move-forward behavior, filters, and visible UI states against the documented API.
- Architecture: architecture.md browser behavior ownership and exact route integration; no server validation or raw user-content HTML.
- Interfaces: use `/api/projects`, `/api/projects/{project_id}/tasks`, `/api/tasks/{task_id}`; use DOM IDs and controls from index.html; render user-provided title/description/priority with `textContent` and replace collections with `replaceChildren`.
- Depends on: taskboard/templates/index.html, taskboard/tests/test_api.py
- Consumed by: taskboard/templates/index.html, taskboard/static/style.css, taskboard/tests/test_ui_content.py
- Acceptance: load projects on page load and refresh selected tasks; create and delete projects using `window.confirm`; create tasks with title/description/priority; edit title/description/priority; move only todo→doing→done and hide/disable Move forward for done; delete tasks; send status and priority filters as API query parameters; render cards into the three named columns; show loading, empty, and API error messages; never inject user content through raw `innerHTML`.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Extend static presentation for project/task forms, selector, filters, Kanban columns/cards, action controls, and responsive state regions.
- Architecture: architecture.md stylesheet ownership; static CSS only, with no application data or JavaScript behavior.
- Interfaces: serve at `/static/style.css`; selectors target the template’s project/task forms, columns, cards, filter controls, and loading/empty/error regions.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html, taskboard/static/app.js
- Acceptance: provide readable desktop and narrow-window layouts; visibly distinguish To Do, Doing, Done, task priority, forms, filters, and loading/empty/error feedback; do not add frameworks, animations, drag-and-drop styling, or unrelated configuration.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-uz4: taskboard/tests/test_ui_content.py
- Scope: Add substantive content integration assertions for the completed phase-2 page and static assets.
- Architecture: architecture.md content-test ownership and SPEC testing contract.
- Interfaces: use FastAPI `client` for GET `/` and static routes; inspect real response content and required DOM text/controls.
- Depends on: taskboard/tests/conftest.py, taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css
- Consumed by: phase-2 verification
- Acceptance: assert GET `/` returns HTML containing `TaskBoard`, project and task forms, project selector/list, both filters, `To Do`, `Doing`, and `Done`, plus loading/empty/error regions; assert `/static/app.js` and `/static/style.css` return 200 with nonempty content; assert app.js contains safe `textContent` rendering and required project/task API route usage.
- Verify: `cd taskboard && python -m pytest -q tests`

## YAGNI and phase boundary

Do not add Playwright files, npm manifests, authentication, drag-and-drop, realtime behavior, new routes, or deployment infrastructure. Phase 3 owns browser E2E and release artifacts; this plan only requires the phase-2 pytest gate.
