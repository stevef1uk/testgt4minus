# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: The foundation repository persists projects and tasks with the specified validation limits, enum values, defaults, UTC timestamps, deterministic ordering, filters, partial updates, idempotent schema, and project-delete cascade.
Level: integration
Test file: taskboard/tests/test_repository.py
Bead ID: tm-ns3
Phase: phase-1-core
Scenarios:
- Initialize a temporary database twice, verify empty/idempotent schema behavior, and create projects in ascending ID order.
- Accept project names through 80 characters and task titles through 120 characters; reject empty or overlong values, overlong descriptions, and unknown status or priority values without persistence.
- Create tasks with default todo/medium values and explicit UTC-offset timestamps; filter by status, priority, and both together while preserving ascending ID order.
- Patch each supported task field while preserving omitted fields, reject invalid writes, and delete a project to cascade-delete its tasks.
Assertions:
- Returned project/task records have the exact documented fields, values, integer IDs, and timestamp shapes.
- Boundary values are accepted and one-character-over-limit values are rejected; invalid writes leave row counts and prior values unchanged.
- Combined filters are an AND query, updates cannot reassign projects, and cascade deletion removes all child tasks.

### phase-1-app
Requirement: The FastAPI app exposes the specified health, project collection/create/delete, health, root, and static routes with contract statuses, decoded JSON shapes, error objects, content types, and isolated temporary-database state.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: tm-rmz
Phase: phase-1-app
Scenarios:
- Exercise the health endpoint and verify project create, list, and delete behavior using the temporary-database fixture; do not require unsupported project retrieve or update routes.
- Fetch the root page and both static asset routes, including successful responses and their documented HTML, JavaScript, and CSS content types; verify the root is a real basic TaskBoard page with its heading, project creation controls, and empty-state container.
- Check project response shapes, empty project-list behavior, missing-project delete errors, and malformed integer project paths where applicable.
- Verify valid project writes round-trip, invalid project requests do not persist changes, and the runtime database is not touched.
Assertions:
- Health returns status 200 with decoded JSON {"status": "ok"}; project responses and lists have the documented keys, types, and values.
- Project CRUD uses the specified success and error statuses and {"error": ...} objects; malformed integer paths retain 422.
- The root and static routes return successful responses with the specified content types and nonempty bodies; the root HTML contains the “TaskBoard” heading, project creation form controls, and empty-state container, and temporary data is isolated from taskboard.db.

### phase-2
Requirement: The delivered TaskBoard page provides the specified project/task forms, project selection, task editing/deletion, three Kanban columns, move-forward behavior, empty/error states, and safe visible rendering.
Level: integration
Test file: taskboard/tests/test_ui_content.py
Bead ID: pending
Phase: phase-2
Scenarios:
- Fetch the rendered page and assert the TaskBoard heading, project creation/selection controls, task form and priority options, status/priority filters, all three column headings, empty/error regions, and project-delete control.
- Verify the served JavaScript and CSS are nonempty and the browser code contains the documented API interactions, move-forward/edit/delete flows, filter refresh, visible error handling, and textContent use for user content.
- Exercise the page through the test client with seeded project/task data and verify the rendered document exposes the taskboard controls and task values needed for create, edit, move, and delete flows.
Assertions:
- Required controls and labels exist in real HTML, all canonical static assets load with nonempty bodies, and no placeholder page is accepted.
- The UI contract's task states, filters, error area, safe text rendering, and responsive stylesheet hooks are represented in the delivered canonical files.

### phase-3
Requirement: The completed browser experience supports independent end-to-end project/task lifecycle, Kanban transitions, priority filtering, reset, cleanup, and usable narrow-window layout against the running server.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- In an isolated scenario, load the running page and assert the real TaskBoard heading and To Do, Doing, and Done columns.
- Create a unique project and task, move it todo to doing to done, delete it, and assert each real task-card state and disappearance.
- Create two uniquely named tasks with different priorities, filter to high, assert only the high-priority task is rendered, reset the filter, and assert both return; clean up created projects.
Assertions:
- Browser assertions inspect real task text and column placement, not merely HTTP 200 or placeholder visibility.
- Each scenario is independent, uses the documented API/UI, survives the configured viewport sizes, and leaves no unrelated persisted data.
