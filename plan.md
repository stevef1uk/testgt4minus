# Phase 2 implementation plan: Tasks and Kanban UI

Phase 2 extends the Phase 1 application in place. The active verification
command is exactly `cd taskboard && python -m pytest -q tests`. Preserve the
architecture boundaries: DDL stays in `taskboard/db.py`, SQL stays in
`taskboard/repository.py`, HTTP routes stay in `taskboard/main.py`, and browser
behavior stays in the canonical template and static files.

## Bead map

### te-tlq: taskboard/tests/test_api.py
- Scope: Extend API tests for the complete project/task HTTP contract.
- Architecture: architecture.md HTTP + entrypoint integration and Unit tests;
  use exact routes and response shapes from SPEC.md.
- Interfaces: TestClient fixture; `/api/health`, `/api/projects`,
  `/api/projects/{project_id}/tasks`, and `/api/tasks/{task_id}`.
- Depends on: taskboard/tests/conftest.py, taskboard/main.py, taskboard/repository.py
- Consumed by: taskboard/static/app.js and the phase gate.
- Acceptance: Assert exact health JSON; project/task create, list, patch, and
  delete round trips with 201/200/204 and empty delete bodies; defaults,
  complete JSON fields, ascending IDs, empty arrays, composed status/priority
  filters; 400 invalid fields/filters/lengths and empty PATCH; 404 missing
  resources; and isolated temporary database state.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-21l: taskboard/templates/index.html
- Scope: Extend the real page with project/task forms, filters, state regions,
  and completed Kanban columns.
- Architecture: architecture.md planned layout and template ownership; SPEC.md
  UI contract.
- Interfaces: TaskBoard heading, project form/list/selector, task form,
  project delete control, status and priority filters, loading/empty/error
  regions, To Do/Doing/Done columns, and exact static asset URLs.
- Depends on: taskboard/static/app.js, taskboard/static/style.css
- Consumed by: taskboard/static/app.js and taskboard/tests/test_ui_content.py.
- Acceptance: Render real accessible HTML with stable JavaScript hooks,
  controls for project/task CRUD and title/description/priority, both filter
  selects, all three headings and state regions; contain no database calls or
  inline application logic.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-5bn: taskboard/static/app.js
- Scope: Implement vanilla-JS project selection, task CRUD, Kanban rendering,
  movement, filtering, and visible errors.
- Architecture: architecture.md static ownership and HTTP integration.
- Interfaces: Call `/api/projects`, `/api/projects/{project_id}/tasks`,
  `/api/projects/{project_id}`, and `/api/tasks/{task_id}` using SPEC methods
  and fields; consume the template DOM.
- Depends on: taskboard/templates/index.html, taskboard/main.py
- Consumed by: the rendered page and phase acceptance.
- Acceptance: Load/select/create/delete projects; create, edit, delete, and
  render tasks in three columns; move todo to doing to done and hide/disable
  movement for done; apply status/priority query filters; show empty and API
  error states; use textContent and replaceChildren for API/user text and
  never raw user-content HTML.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-uz4: taskboard/tests/test_ui_content.py
- Scope: Test real rendered HTML and served static assets.
- Architecture: architecture.md phase-2 delivery and UI test ownership.
- Interfaces: client fixture with GET `/`, `/static/app.js`, and
  `/static/style.css`.
- Depends on: taskboard/tests/conftest.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css
- Consumed by: the phase verification gate.
- Acceptance: Assert HTML content type, TaskBoard heading, project and task
  forms, project controls, all three column headings, filters, and state
  regions; assert both static responses are 200 and nonempty with substantive
  content.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Style forms, controls, Kanban columns/cards, and state messages.
- Architecture: architecture.md static stylesheet ownership.
- Interfaces: Selectors for template regions, controls, board columns/cards,
  and loading/empty/error states.
- Depends on: taskboard/templates/index.html
- Consumed by: the rendered browser page.
- Acceptance: Make columns and cards distinct, keep forms and filters usable
  on narrow windows, style all state regions, preserve the canonical URL, and
  add no dependencies or JavaScript behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Provide isolated FastAPI TestClient setup per test.
- Architecture: architecture.md Unit tests and temporary database fixture.
- Interfaces: pytest fixture `client(tmp_path, monkeypatch)`.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py and taskboard/tests/test_ui_content.py.
- Acceptance: Use `tmp_path / "taskboard.sqlite3"`, set TASKBOARD_DB_PATH,
  reload taskboard.main, call create_app with the temporary path, and yield a
  context-managed TestClient; never use runtime or in-memory databases.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Test task persistence, defaults, filtering, updates, ordering, and
  project cascade deletion.
- Architecture: architecture.md repository ownership and Unit tests.
- Interfaces: Documented ProjectRepository/TaskRepository operations and SPEC
  project/task records.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/tests/test_api.py and the regression gate.
- Acceptance: Prove idempotent schema, empty lists, defaults, UTC timestamps,
  ascending IDs, status/priority AND filters, partial updates preserving
  omitted fields, all task field changes, and cascade deletion using real
  isolated SQLite assertions.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase 2 acceptance

The full pytest gate must preserve Phase 1 behavior while proving task
persistence, exact API transitions, real Kanban markup, safe rendering,
project/task CRUD, movement, filtering, and visible empty/error states from
SPEC.md. Do not add alternate paths, frameworks, routes, or Phase 3 files.
