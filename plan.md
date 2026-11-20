# Phase 2 implementation plan: Tasks and Kanban UI

Phase 2 extends the Phase 1 application in place; it must not create alternate
pages, routes, modules, or copies. The required verification is exactly
`cd taskboard && python -m pytest -q tests`. Implementation follows TDD:
each test bead writes substantive failing assertions first, then the smallest
compatible implementation is added while all Phase 1 health/project behavior
remains green. Task repository/API behavior may extend the already-owned
Phase 1 modules, but this phase creates beads only for the seven required paths.

## Bead map

### te-2qb: taskboard/templates/index.html
- Scope: Extend the canonical server-rendered page with the complete Phase 2 TaskBoard shell.
- Architecture: `taskboard/templates/index.html` owns semantic forms, project selector, filters, three columns, and loading/empty/error regions.
- Interfaces: Provide stable elements for `taskboard/static/app.js`: project form and project-list selector, delete-project control, task form with title/description/priority, status and priority filter selects, `To Do`, `Doing`, and `Done` headings/containers, task empty state, loading state, and visible error area.
- Depends on: taskboard/main.py (Phase 1), taskboard/static/app.js (same phase extension is consumed after markup exists)
- Consumed by: te-ms3, te-zch
- Acceptance: `GET /` remains real HTML with heading `TaskBoard`; it contains project creation with `Add project`, task creation with required title and low/medium/high priority, project selection, delete-project control, both all/todo/doing/done and all/low/medium/high filters, and three visibly labeled columns. Use native forms and no second page.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Extend the canonical stylesheet for the task form, task cards, columns, controls, and state regions.
- Architecture: `taskboard/static/style.css` owns responsive presentation and visual states only.
- Interfaces: Style the semantic regions from `taskboard/templates/index.html`, including cards, priority/status controls, loading/empty/error messages, and the three Kanban columns; define no data or JavaScript behavior.
- Depends on: taskboard/templates/index.html
- Consumed by: te-zch
- Acceptance: To Do, Doing, and Done remain distinct and usable; forms, cards, controls, and visible API errors are readable on desktop and narrow windows. Do not add frameworks, animations, drag-and-drop, or unrelated features.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-ms3: taskboard/static/app.js
- Scope: Implement browser state and all Phase 2 project/task interactions against the existing API.
- Architecture: `taskboard/static/app.js` owns browser API calls, rendering, editing, moving, deletion, and filters.
- Interfaces: Call exact `GET/POST /api/projects`, `DELETE /api/projects/{project_id}`, `GET/POST /api/projects/{project_id}/tasks`, and `PATCH/DELETE /api/tasks/{task_id}`. Consume the canonical template elements and render task cards into the three status containers.
- Depends on: taskboard/templates/index.html, taskboard/main.py (Phase 1 API), te-2qb
- Consumed by: te-zch
- Acceptance: Load/select/create/delete projects and refresh selection; create tasks as todo; render title and priority in the correct column; move todo→doing→done and hide/disable move for done; edit title/description/priority; delete tasks; send selected status/priority filters as query parameters; show API failures in the visible error area. Insert user title/description with `textContent` and clear containers with `replaceChildren`, never raw user-content `innerHTML`; use `window.confirm` for project deletion.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Preserve isolated per-test SQLite and FastAPI client setup for expanded repository/API/content tests.
- Architecture: `taskboard/tests/conftest.py` owns the temporary-path application/client fixture.
- Interfaces: Export pytest fixture `client(tmp_path, monkeypatch)` that sets `TASKBOARD_DB_PATH`, reloads `taskboard.main`, calls `create_app(str(database_path))`, and yields `TestClient`.
- Depends on: taskboard/main.py (Phase 1)
- Consumed by: te-7yg, te-oj5, te-zch
- Acceptance: Every test uses a fresh temporary `taskboard.sqlite3`, never runtime `taskboard.db`; the fixture initializes schema and supports API, root HTML, and static requests without changing production behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Extend repository tests for task persistence and preserve all project/schema assertions.
- Architecture: Tests cover `ProjectRepository`, `TaskRepository`, and repository functions `list_tasks`, `create_task`, `update_task`, and `delete_task` described in architecture.md.
- Interfaces: Assert exact task fields (`id`, `project_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`) and repository return shapes.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py (Phase 1)
- Consumed by: te-oj5
- Acceptance: Keep idempotent schema, empty lists, project ID ordering, UTC timestamp, and cascade assertions green. Add default todo/medium creation, trimmed title, status/priority and combined AND filters in ascending ID order, partial updates for every permitted field while preserving omitted values, invalid-value/length coverage as appropriate, and project deletion cascading all tasks.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Extend API contract tests for task CRUD, validation, filters, and deletion semantics while retaining health/project coverage.
- Architecture: Tests exercise `taskboard/main.py` routes: `GET/POST /api/projects/{project_id}/tasks`, `PATCH/DELETE /api/tasks/{task_id}`, plus existing project and health routes.
- Interfaces: Assert exact 201 task creation, 200 lists/patches, 204 empty-body deletes, and `{ "error": "..." }` for application-level 400/404 responses.
- Depends on: taskboard/main.py, te-xsd, te-7yg
- Consumed by: <none>
- Acceptance: Prove exact `{"status":"ok"}` health JSON; project and task create/list/patch/delete round trips; trimmed title and default description/priority/status; invalid empty or overlong title/description and bad status/priority return 400; missing project/task returns 404; empty PATCH returns 400; empty lists are `[]`; both filters compose with AND and preserve ID order; 204 responses have no body; malformed integer paths retain 422.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-zch: taskboard/tests/test_ui_content.py
- Scope: Add content integration assertions for real Phase 2 markup and served static assets.
- Architecture: `taskboard/tests/test_ui_content.py` owns rendered-page and asset assertions, using the isolated client fixture.
- Interfaces: Test `GET /`, `GET /static/app.js`, and `GET /static/style.css`; inspect response content rather than only status.
- Depends on: taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css, te-2qb, te-1vt, te-ms3, te-xsd
- Consumed by: <none>
- Acceptance: Assert HTML contains `TaskBoard`, project form/list, task form, project selector, both filter controls, empty/loading/error regions, and all `To Do`, `Doing`, `Done` headings; assert both static responses are 200 and nonempty; assert app content includes `/api/projects`, `textContent`, and `replaceChildren` so safe rendering and canonical routes are evidenced. Do not accept placeholder or status-only checks.
- Verify: `cd taskboard && python -m pytest -q tests`

## Integration and acceptance summary

Dependency order is template, stylesheet/fixture, repository tests, API tests,
JavaScript integration, then content assertions; previously delivered
`taskboard/main.py`, `taskboard/repository.py`, `taskboard/db.py`, and
`taskboard/models.py` are extended in place by the corresponding implementation
beads and are not duplicated. The repository contract supplies task JSON and
validation before API routes consume it. The template supplies stable semantic
regions before JavaScript wires browser behavior. The full pytest command is
the sole Phase 2 gate and must prove real persistence, HTTP state changes,
safe rendered content, and the required Kanban UI contract.
