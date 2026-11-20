# Phase 2 implementation plan — Tasks and Kanban UI

Phase 2 extends the Phase 1 application in place. Implement exactly the seven
active required paths below; preserve the canonical `taskboard/` layout and
the existing project API. The phase gate is `cd taskboard && python -m pytest -q tests`.
The implementation must satisfy the SPEC HTTP table and UI contract, without
adding routes, drag-and-drop, ranking, frameworks, or unrelated features.

## Bead map

### te-7yg: taskboard/tests/test_repository.py
- Scope: Extend repository coverage for task persistence and lifecycle behavior.
- Architecture: `taskboard/repository.py` owns `ProjectRepository`, `TaskRepository`, `list_tasks(project_id, status: str | None = None, priority: str | None = None) -> list[dict]`, `create_task(...) -> dict`, `update_task(task_id: int, changes: dict) -> dict | None`, and `delete_task(task_id: int) -> bool`; validation/mapping remain in `taskboard/models.py`.
- Interfaces / Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py; existing project repository API.
- Consumed by: taskboard/tests/test_api.py and taskboard/static/app.js through the API.
- Acceptance: Assert a created task has the exact SPEC fields, defaults to `status="todo"` and `priority="medium"`, retains an empty default description, and has explicit UTC timestamps. Assert tasks list in ascending ID order and filters by status, priority, and both together. Assert partial updates change title/description/priority/status while preserving omitted fields. Assert deleting a project cascades to its tasks and empty lists are `[]`; use temporary SQLite databases and substantive state assertions.
- Verify: cd taskboard && python -m pytest -q tests

### te-xsd: taskboard/tests/conftest.py
- Scope: Maintain isolated pytest application fixtures while Phase 2 adds task routes.
- Architecture: `taskboard/tests/conftest.py` owns the temporary-path app/client fixture and must not touch runtime `taskboard.db`.
- Interfaces / Depends on: taskboard/main.py `create_app(db_path: str | None = None) -> FastAPI`; FastAPI `TestClient`; pytest `tmp_path`.
- Consumed by: taskboard/tests/test_repository.py and taskboard/tests/test_api.py.
- Acceptance: Set `TASKBOARD_DB_PATH` to a unique `tmp_path` database before importing/reloading `taskboard.main`; create the app with that path; yield a working TestClient; isolate every test's data; close the client after use. The fixture must support health, project, and task API assertions without production behavior.
- Verify: cd taskboard && python -m pytest -q tests

### te-oj5: taskboard/tests/test_api.py
- Scope: Extend API contract tests for task creation, listing, patching, deletion, filters, validation, and project cascade.
- Architecture: `taskboard/main.py` owns exact routes: GET `/api/projects/{project_id}/tasks`, POST the same path, PATCH `/api/tasks/{task_id}`, and DELETE the same path; errors are `{"error": "..."}` with 400/404 and deletes are 204 with no body.
- Interfaces / Depends on: te-xsd taskboard/tests/conftest.py; taskboard/main.py; taskboard/repository.py; existing project endpoints.
- Consumed by: taskboard/static/app.js and the phase verification suite.
- Acceptance: Assert task POST returns 201 with title trimmed, description/priority defaults, status `todo`, and exact JSON fields; GET returns ascending tasks and combines valid status/priority filters with AND. Assert PATCH accepts nonempty subsets of title, description, priority, status and preserves omitted fields; assert DELETE returns 204 with an empty body. Assert missing projects/tasks return 404, nonexistent task project creation returns 404, invalid status/priority/title/description and empty PATCH return 400, and empty lists serialize as `[]`; preserve exact health/project assertions.
- Verify: cd taskboard && python -m pytest -q tests

### te-2qb: taskboard/templates/index.html
- Scope: Extend the canonical real page with project selection, task form, filters, Kanban columns, and stable DOM hooks.
- Architecture: Template owns semantic forms, selector, filters, columns, empty/error regions; it contains no database calls or inline application logic and loads `/static/app.js` and `/static/style.css`.
- Interfaces / Depends on: taskboard/static/app.js; taskboard/static/style.css; existing `taskboard/main.py` root rendering/static mount.
- Consumed by: taskboard/static/app.js, taskboard/tests/test_ui_content.py, and browser users.
- Acceptance: Render heading `TaskBoard`, project-name input and `Add project` button, project selector/list, selected-project task form with required title, optional description, low/medium/high priority select and `Add task`, status and priority filter selects including `all`, delete-project control, and visible `To Do`, `Doing`, `Done` columns. Provide task/empty/error regions and controls hooks; include no placeholder-only page and no unsupported drag/drop UI.
- Verify: cd taskboard && python -m pytest -q tests

### te-ms3: taskboard/static/app.js
- Scope: Implement vanilla browser API calls, state, safe task rendering, project/task CRUD, move-forward behavior, and filter refreshes.
- Architecture: Browser behavior belongs only here; consume the exact API paths and JSON shapes from SPEC. Use `textContent` for user content and do not use raw user-content `innerHTML`.
- Interfaces / Depends on: taskboard/templates/index.html DOM hooks; taskboard/static/style.css classes; API routes GET/POST `/api/projects`, DELETE `/api/projects/{project_id}`, GET/POST `/api/projects/{project_id}/tasks`, PATCH/DELETE `/api/tasks/{task_id}`.
- Consumed by: taskboard/templates/index.html and taskboard/tests/test_ui_content.py; calls taskboard/main.py at runtime.
- Acceptance: Load projects on page load, select a project, fetch its tasks, and show an empty-project state. Create and delete projects, refresh selection, create tasks with title/description/priority, and render cards in `todo`/`doing`/`done` columns showing title and priority. Move forward exactly todo→doing→done and hide/disable that control for done. Edit title/description/priority, delete tasks, submit filter query parameters, omit `all` filters, refresh results, and display API errors visibly. Use safe DOM text insertion and no invented endpoint or client-side ranking.
- Verify: cd taskboard && python -m pytest -q tests

### te-1vt: taskboard/static/style.css
- Scope: Style the canonical TaskBoard page, forms, task cards, Kanban columns, states, and narrow-window layout.
- Architecture: Stylesheet owns responsive presentation and visual states only; selectors must match the template/script hooks.
- Interfaces / Depends on: taskboard/templates/index.html structure and classes; taskboard/static/app.js status/card classes.
- Consumed by: taskboard/templates/index.html and browser users; checked by taskboard/tests/test_ui_content.py.
- Acceptance: Provide readable project/task forms and controls, visibly distinct `todo`, `doing`, and `done` columns/cards, empty/error presentation, and a usable responsive layout for desktop and narrow windows. Do not introduce external assets, animations, frameworks, or unrelated UI behavior.
- Verify: cd taskboard && python -m pytest -q tests

### te-zch: taskboard/tests/test_ui_content.py
- Scope: Add content integration assertions for the real phase-2 page and static assets.
- Architecture: This file owns rendered-page and asset assertions, not persistence implementation; architecture requires real HTML and nonempty static responses.
- Interfaces / Depends on: te-2qb taskboard/templates/index.html, te-ms3 taskboard/static/app.js, te-1vt taskboard/static/style.css, and taskboard/main.py root/static routes.
- Consumed by: phase-2 verification and QA.
- Acceptance: Through the TestClient assert GET `/` returns 200 HTML containing `TaskBoard`, project form and Add project control, task title/description/priority form and Add task control, project selector, both filters, delete-project control, all three exact headings `To Do`, `Doing`, `Done`, and visible error/empty-state hooks. Assert GET `/static/app.js` and `/static/style.css` return 200 with nonempty content; assert content includes required API paths/status concepts and safe rendering (`textContent`) rather than a placeholder.
- Verify: cd taskboard && python -m pytest -q tests

## Dependency and delivery order

Implement and test repository behavior first (`te-7yg`), then the isolated
fixture (`te-xsd`) and API contract (`te-oj5`). In parallel only after the
existing Phase 1 shell is understood, extend the template/style/script in the
dependency order template → stylesheet → script, with UI content assertions
last (`te-2qb`, `te-1vt`, `te-ms3`, `te-zch`). The final gate is the exact
phase command above; no Playwright files or Phase 3 beads belong here.
