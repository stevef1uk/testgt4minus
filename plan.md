# Phase 2 implementation plan — Tasks and Kanban UI

Phase 2 extends the Phase 1 application in place. It adds task persistence,
task API behavior, project selection, task creation/edit/delete, Kanban
columns and move-forward behavior, while preserving canonical paths. The
active verification command is exactly:
`cd taskboard && python -m pytest -q tests`.

## Bead map

### te-zch: taskboard/tests/test_ui_content.py
- Scope: Add content integration tests for the real TaskBoard page and static assets.
- Architecture: `taskboard/tests/test_ui_content.py` owns rendered-page and asset assertions and consumes the canonical template, JavaScript, CSS, and app.
- Interfaces / Depends on: `taskboard/main.py`, `taskboard/templates/index.html`, `taskboard/static/app.js`, `taskboard/static/style.css`.
- Consumed by: Phase 2 pytest gate and QA.
- Acceptance: GET `/` must return real HTML containing `TaskBoard`, project creation, task title/description/priority form, `Add task`, and visible `To Do`, `Doing`, and `Done`; both static routes must return 200 and nonempty content. Assertions must reject placeholder content.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-2qb: taskboard/templates/index.html
- Scope: Extend the Phase 1 shell with project selection/deletion, task form, filter controls, Kanban columns, task regions, and visible empty/error regions.
- Architecture: `taskboard/templates/index.html` owns semantic forms, selector, filters, columns, and state regions; browser behavior remains in `taskboard/static/app.js`.
- Interfaces / Depends on: `taskboard/main.py`; consumed API shapes are the SPEC project/task JSON objects.
- Consumed by: `taskboard/static/app.js`, `taskboard/main.py`, and `taskboard/tests/test_ui_content.py`.
- Acceptance: Preserve the TaskBoard heading; provide project name input and Add project, project selector and delete-project control; task title, description, priority options low/medium/high, and Add task; status options all/todo/doing/done and priority options all/low/medium/high; distinct To Do, Doing, Done columns; no-project, no-matching-task, and API-error regions. Use native HTML and external assets without a second page.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-ms3: taskboard/static/app.js
- Scope: Implement project/task API calls, selection, safe rendering, Kanban movement, edit/delete controls, filtering, and refresh behavior.
- Architecture: `taskboard/static/app.js` owns browser API, rendering, filtering, editing, moving, and deletion; it must not perform server validation or inject raw user content.
- Interfaces / Depends on: `taskboard/templates/index.html`, `taskboard/main.py` routes GET/POST `/api/projects`, DELETE `/api/projects/{project_id}`, GET/POST `/api/projects/{project_id}/tasks`, PATCH/DELETE `/api/tasks/{task_id}`.
- Consumed by: template, static serving, and UI tests.
- Acceptance: Load/create/select/delete projects with window.confirm and refresh selection; create tasks and render cards in the matching column; show title and priority; provide Edit/Delete and Move forward todo→doing→done, hiding or disabling it for done; PATCH title/description/priority; send status and priority query parameters while omitting all; display API errors; use textContent for user title/description, not raw innerHTML.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Style responsive forms, project/task controls, Kanban columns/cards, and empty/error states.
- Architecture: `taskboard/static/style.css` owns responsive presentation and visual states, not application data or behavior.
- Interfaces / Depends on: `taskboard/templates/index.html`.
- Consumed by: template and browser rendering.
- Acceptance: Keep all three columns visibly distinct, cards readable, controls usable on desktop and narrow windows, and use plain CSS without frameworks, animations, icons, or drag-and-drop.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Preserve isolated temporary database and FastAPI client fixtures for all Phase 2 tests.
- Architecture: `taskboard/tests/conftest.py` owns temporary-path app/client fixtures and no production behavior.
- Interfaces / Depends on: `taskboard/main.py` create_app(db_path: str | None = None) -> FastAPI.
- Consumed by: repository, API, and UI content tests.
- Acceptance: Every test uses a fresh explicit `tmp_path / "taskboard-test.db"` database, never runtime taskboard.db, while preserving Phase 1 fixture compatibility and schema initialization through create_app.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Extend persistence tests for task defaults, filters, updates, timestamps, ordering, and cascade deletion while preserving project tests.
- Architecture: This file owns repository assertions; SQL remains in repository.py and mapping/validation in models.py.
- Interfaces / Depends on: `taskboard/db.py`, `taskboard/models.py`, `taskboard/repository.py` and its ProjectRepository/TaskRepository operations.
- Consumed by: repository implementation and Phase 2 gate.
- Acceptance: Assert default todo/medium tasks, exact fields, UTC timestamps and ascending IDs; status, priority, and AND filters; partial updates preserving omitted fields; and project deletion cascading tasks. Retain idempotent schema and empty-list coverage.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Extend API tests for task CRUD, validation, filters, statuses, and response bodies while preserving Phase 1 tests.
- Architecture: This file owns HTTP contract assertions for main.py, not repository internals or browser behavior.
- Interfaces / Depends on: `taskboard/tests/conftest.py`, `taskboard/main.py`, and exact task routes GET/POST `/api/projects/{project_id}/tasks`, PATCH/DELETE `/api/tasks/{task_id}`.
- Consumed by: task route implementation and Phase 2 gate.
- Acceptance: Assert task create/list/patch/delete, defaults, exact JSON, ordering, empty arrays, 404 missing project/task, 400 invalid enums and lengths, 400 empty PATCH, 204 empty delete bodies, composed filters, cascade behavior, and preserved exact health/project assertions.
- Verify: `cd taskboard && python -m pytest -q tests`

## Integration boundaries and YAGNI

The active phase has no server-entrypoint bead, so an Integration contract
section is unnecessary. Existing Phase 1 files are extended in place and no
duplicate paths are introduced. Keep SQL in repository.py, validation/mapping
in models.py, HTTP routes in main.py, and browser behavior in app.js. Do not
add authentication, drag-and-drop, custom ranking, external services, build
systems, alternate routes, or Phase 3 Playwright files.
