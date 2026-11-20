# Phase-2 Implementation Plan

Phase 2 extends the existing TaskBoard application in place with task
persistence, task HTTP routes, and the Kanban UI. Do not create duplicate
application files or Phase-3 Playwright files. All paths below are exact
repository-relative paths from the active profile.

## Verification

Run the phase gate after implementation:
`cd taskboard && python -m pytest -q tests`
The tests must use temporary SQLite databases and assert real state changes.
Do not replace behavior checks with status-only or placeholder assertions.

## Bead map

### te-7yg: taskboard/tests/test_repository.py
- Scope: Extend repository tests for task creation, defaults, ordering,
  filtering, partial updates, deletion, timestamps, and project cascade.
- Architecture: `taskboard/repository.py` owns `ProjectRepository`,
  `TaskRepository`, `list_tasks`, `create_task`, `update_task`, and
  `delete_task`; `taskboard/models.py` owns validation and row mapping.
- Acceptance:
  - Assert new tasks default to status `todo` and priority `medium`, preserve
    valid UTC timestamps, and list in ascending ID order.
  - Assert status filtering, priority filtering, combined AND filtering, empty
    results, task deletion, and partial updates preserving omitted fields.
  - Assert deleting a project cascades to its tasks and invalid values/lengths
    are rejected without interpolated request data in SQL.
- Depends on: existing taskboard/repository.py, taskboard/models.py
- Consumed by: te-oj5 task API tests and phase verification.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Extend API tests for task CRUD, validation, filters, errors, and
  project/task lifecycle while retaining Phase-1 project and health coverage.
- Architecture: `taskboard/main.py` owns the exact HTTP routes and response
  shapes: GET/POST `/api/projects/{project_id}/tasks`, PATCH/DELETE
  `/api/tasks/{task_id}`, and the existing project routes.
- Acceptance:
  - Assert task creation returns 201 with defaults, task listing returns
    ordered objects or `[]`, PATCH updates only supplied fields, and DELETE
    returns 204 with an empty body.
  - Assert 404 for missing projects/tasks; 400 for empty title, invalid
    status/priority, overlong title/description, invalid filters, and empty
    PATCH. Malformed integer paths may retain FastAPI 422.
  - Assert status and priority filters combine with AND and preserve ID order;
    retain exact health JSON and project CRUD assertions.
- Depends on: taskboard/tests/conftest.py (te-xsd), taskboard/tests/test_repository.py (te-7yg)
- Consumed by: taskboard/static/app.js (te-ms3) and phase verification.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Preserve the isolated client fixture used by all active-phase tests.
- Architecture: Fixture sets `TASKBOARD_DB_PATH` to a `tmp_path` database and
  creates the app through `taskboard.main.create_app`; it never uses runtime
  `taskboard.db`.
- Acceptance:
  - Every client has a fresh temporary schema and can exercise task and
    project routes through the real FastAPI application.
  - Keep fixture behavior limited to test setup; add no production behavior.
- Depends on: existing taskboard/main.py
- Consumed by: te-oj5 and te-zch.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-2qb: taskboard/templates/index.html
- Scope: Extend the existing page with project selection, task form, filters,
  Kanban columns, task controls, and state regions.
- Architecture: This file owns semantic forms, selector, filters, columns,
  and empty/loading/error regions; it contains no database calls or inline
  application logic.
- Acceptance:
  - Include heading `TaskBoard`, project name input and `Add project`,
    project list/selector, and delete-project control.
  - Include task title, optional description, priority options low/medium/high,
    `Add task`, status and priority filters, and visible `To Do`, `Doing`, and
    `Done` columns.
  - Provide task-card containers and Edit, Delete, and Move forward controls,
    plus visible empty/loading/error regions and both static asset references.
- Depends on: existing taskboard/main.py
- Consumed by: te-ms3 and te-zch.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-ms3: taskboard/static/app.js
- Scope: Implement project/task loading, creation, editing, moving, deletion,
  filtering, rendering, and visible error handling using vanilla JavaScript.
- Architecture: This file owns browser API calls and rendering. User content
  must use `textContent` and DOM replacement, never raw user-content HTML.
- Acceptance:
  - Load/select projects; create and delete projects; refresh selection after
    deletion; create tasks with title, description, and priority.
  - Render cards in the three columns; edit title/description/priority; delete
    tasks; move todo→doing→done through status PATCH, disabling/hiding move on
    done cards.
  - Send status/priority query filters, combine them, omit `all`, render only
    matching cards, and show empty and visible API-error states.
  - Use `/api/projects`, `/api/projects/{id}/tasks`, `/api/tasks/{id}`, and
    `/api/projects/{id}` exactly as specified.
- Depends on: taskboard/templates/index.html (te-2qb), taskboard/tests/test_api.py (te-oj5), taskboard/static/style.css (te-1vt)
- Consumed by: te-zch and later Phase-3 browser coverage.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Style forms, selectors, cards, Kanban columns, filters, and state
  messages with plain responsive CSS.
- Architecture: Owns presentation only; it must not add application data,
  JavaScript behavior, frameworks, animations, or another page.
- Acceptance:
  - Keep all three columns and controls usable on desktop and narrow windows.
  - Provide readable styling for task cards, forms, empty/loading/error states,
    and project/task regions used by the template and script.
- Depends on: taskboard/templates/index.html (te-2qb)
- Consumed by: te-ms3 and te-zch.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-zch: taskboard/tests/test_ui_content.py
- Scope: Add content integration assertions for the real page and served
  static assets.
- Architecture: Owns rendered-page and asset assertions; it consumes
  `taskboard/main.py`, `taskboard/templates/index.html`,
  `taskboard/static/app.js`, and `taskboard/static/style.css`.
- Acceptance:
  - Assert GET `/` returns real HTML containing `TaskBoard`, project and task
    forms, all three column headings, and the required empty/loading/error
    regions.
  - Assert GET `/static/app.js` and `/static/style.css` returns 200 and
    nonempty content; do not use status-only or import-only tests.
- Depends on: taskboard/tests/conftest.py (te-xsd), taskboard/templates/index.html (te-2qb), taskboard/static/app.js (te-ms3), taskboard/static/style.css (te-1vt)
- Consumed by: phase verification and QA.
- Verify: `cd taskboard && python -m pytest -q tests`

## Integration and scope notes

No server-entrypoint bead is active in phase 2. Existing `main.py` remains the
route-registration and app-factory owner and must pass its selected database
path to repository operations. Phase 3 owns Playwright manifests and browser
scenarios, so they are intentionally excluded here. Every bead above maps to
one active required path, and all dependencies refer to existing paths or the
real open bead IDs listed in this plan.
