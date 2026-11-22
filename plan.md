# Phase-2 implementation plan: Tasks and Kanban UI

Phase 2 extends the existing TaskBoard package in place. It adds task
persistence/API behavior and the usable project/task Kanban experience without
new routes, duplicate pages, or alternate asset paths. Every bead closes only
after this phase-wide gate passes:
`cd taskboard && python -m pytest -q tests`

## Bead map

### tm-yo8: taskboard/tests/test_repository.py
- Scope: Extend repository coverage from projects to task CRUD, validation, filtering, partial updates, and cascade deletion.
- Architecture: `taskboard/repository.py` owns `ProjectRepository` and `TaskRepository`; `taskboard/models.py` owns enum/length validation and row mapping; task fields are `id, project_id, title, description, status, priority, created_at, updated_at`.
- Interfaces: Assert task creation defaults `status=todo`, `priority=medium`; task listing accepts `status` and `priority` and combines them with AND; updates accept title, description, priority, status while preserving omitted fields.
- Depends on: <none>
- Consumed by: tm-rmz (taskboard/tests/test_api.py)
- Acceptance:
  - Assert a created project and task round-trip with the exact task fields and explicit UTC timestamps, and an empty project/task list serializes as an empty collection.
  - Assert status transitions `todo` -> `doing` -> `done`, title/description/priority edits, and preservation of omitted PATCH fields.
  - Assert status-only, priority-only, and combined status+priority filters return only matching tasks in ascending ID order.
  - Assert deleting a task removes it and deleting a project cascades to its tasks; assert invalid status/priority, empty PATCH, overlong title/description, and missing IDs are rejected according to the architecture contract.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rmz: taskboard/tests/test_api.py
- Scope: Extend HTTP tests for task routes, exact JSON, validation, filters, lifecycle updates, and deletion semantics.
- Architecture: `taskboard/main.py` exposes `GET /api/projects/{project_id}/tasks`, `POST /api/projects/{project_id}/tasks`, `PATCH /api/tasks/{task_id}`, and `DELETE /api/tasks/{task_id}` with the SPEC status codes and `{ "error": ... }` application errors.
- Interfaces: Task JSON includes `id`, `project_id`, `title`, `description`, `status`, `priority`, `created_at`, and `updated_at`; creates return 201, updates 200, deletes 204 with no body.
- Depends on: taskboard/tests/test_repository.py (tm-yo8)
- Consumed by: <none>
- Acceptance:
  - Assert project creation then task creation/listing returns the exact JSON key sets, defaults, and `[]` for an empty project; assert task IDs remain ascending.
  - Assert PATCH changes title, description, priority, and status, including `todo` -> `doing` -> `done`, while omitted fields remain unchanged.
  - Assert `status` and `priority` query filters each work and together use AND semantics; assert invalid filters and invalid fields return 400 with an error object.
  - Assert empty PATCH, empty title, bad status/priority, and too-long values return 400; missing project/task returns 404; successful task and project deletion returns 204 with an empty body; project deletion makes its task list empty/unavailable through cascade.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-c2q: taskboard/templates/index.html
- Scope: Provide the single real TaskBoard page shell with project controls, task form, filters, feedback regions, and three Kanban columns.
- Architecture: `taskboard/templates/index.html` owns semantic forms/selectors/columns/message regions and links `/static/app.js` and `/static/style.css`.
- Interfaces: Preserve DOM regions `project-form-region`, `project-form`, `project-list`, `project-filter`, `empty-state`, `loading-state`, and `error-state`; provide TaskBoard heading, Add project/task controls, status/priority selectors, and To Do/Doing/Done column containers.
- Depends on: <none>
- Consumed by: taskboard/static/app.js (tm-rta), taskboard/tests/test_ui_content.py (tm-r98)
- Acceptance:
  - Assert rendered HTML contains the `TaskBoard` heading, project creation input and `Add project`, task title/description/priority controls and `Add task`, and exact `To Do`, `Doing`, and `Done` headings.
  - Assert the project selector/list, delete-project control, status options `all/todo/doing/done`, priority options `all/low/medium/high`, and task-card action regions exist.
  - Assert loading, empty, and error containers remain in the page so empty projects/tasks and API failures have visible destinations rather than being silently omitted.
  - Assert exact `/static/app.js` and `/static/style.css` references and all UI-content test hooks; do not use a placeholder page.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Implement vanilla browser state and API interactions for project selection, task creation/edit/delete, forward movement, filtering, safe rendering, and feedback states.
- Architecture: `taskboard/static/app.js` owns loading, creating, editing, moving, filtering, deleting, and safe DOM rendering against the specified API routes.
- Interfaces: Uses `/api/projects`, `/api/projects/{project_id}/tasks`, `/api/tasks/{task_id}`; uses `textContent` for user text and `replaceChildren` for rendered collections; status values are `todo`, `doing`, `done`.
- Depends on: taskboard/templates/index.html (tm-c2q)
- Consumed by: taskboard/tests/test_ui_content.py (tm-r98)
- Acceptance:
  - Implement project load/select/create/delete and task create so a user can create a project and task and see the task in To Do; project deletion refreshes selection and its cascaded tasks.
  - Implement Move forward exactly todo -> doing -> done, with the control hidden/disabled for done; implement Edit for title, description, and priority and Delete for tasks.
  - Implement status and priority dropdowns with `all` values, refresh via API query parameters, and render filtered cards only in the To Do, Doing, and Done columns.
  - Show visible empty state for no projects and no matching tasks, loading state during fetches, and API error messages in the error area; use `textContent`/`replaceChildren` rather than raw user-content `innerHTML`.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Style the page, forms, task cards, filter controls, feedback states, and responsive three-column Kanban layout.
- Architecture: `taskboard/static/style.css` provides presentation for the template DOM contract, with usable desktop and narrow-window layouts.
- Interfaces: Styles project form/list/filter, task form/card actions, loading/empty/error states, and the To Do/Doing/Done column containers.
- Depends on: taskboard/templates/index.html (tm-c2q)
- Consumed by: taskboard/tests/test_ui_content.py (tm-r98)
- Acceptance:
  - Provide visibly distinct, separately labeled To Do, Doing, and Done column presentation and task cards showing title and priority.
  - Keep project/task creation, edit/delete, Move forward, and status/priority filter controls usable; preserve visible empty, loading, and error states without CSS-only disappearance.
  - Keep the Kanban layout usable at narrow widths and validate the real nonempty asset through the phase-wide pytest content checks, not file existence alone.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-r98: taskboard/tests/test_ui_content.py
- Scope: Assert the real page and static assets expose the phase-2 UI contract.
- Architecture: Content tests cover `taskboard/templates/index.html`, `taskboard/static/app.js`, and `taskboard/static/style.css`, including safe rendering and required API hooks.
- Interfaces: Assert exact regions, `/static/app.js`, `/static/style.css`, `/api/projects`, `textContent`, and `replaceChildren`; assert TaskBoard/task form/filter/column content.
- Depends on: taskboard/templates/index.html (tm-c2q), taskboard/static/app.js (tm-rta), taskboard/static/style.css (tm-2ob)
- Consumed by: <none>
- Acceptance:
  - Assert GET `/` content includes TaskBoard, project and task forms, all three `To Do`/`Doing`/`Done` headings, project/filter controls, and visible empty/loading/error regions.
  - Assert both static assets are nonempty and linked at exact paths; assert app.js contains `/api/projects`, `textContent`, and `replaceChildren`.
  - Assert content hooks cover project creation/task creation, status and priority filter choices, edit/delete/move controls, and the three-column Kanban rendering contract.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase acceptance
The completed phase must demonstrate project and task creation, todo-to-doing-to-done movement, editing, deletion, status and priority filtering, three visible Kanban columns, and preserved empty/error states. The sole closure command is `cd taskboard && python -m pytest -q tests`.
