# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: Deliver the SQLite foundation, validation/mapping, project and task schema invariants, repository operations, and isolated repository coverage.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: te-7yg
Phase: phase-1-core
Scenarios:
- Initialize a new database twice and verify empty project/task results, foreign-key cascade support, and deterministic ascending project IDs.
- Create projects and tasks with trimmed names/titles, default todo/medium values, UTC timestamps, and parameterized repository writes.
- Filter tasks by status, priority, and both filters together; update a partial task while preserving omitted fields.
- Delete a project and verify its tasks are cascaded; cover invalid enum and length/empty-value validation through the repository/model contract.
Assertions:
- Returned rows have the exact project/task JSON fields, positive IDs, explicit UTC timestamps, and stable ID ordering.
- Defaults, conjunction filters, partial-update preservation, idempotent schema setup, and cascade deletion produce the specified state.

### phase-1-app
Requirement: Provide create_app, database-path selection, health and project HTTP routes, real HTML/static delivery, isolated fixtures, and project API tests.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-oj5
Phase: phase-1-app
Scenarios:
- Create an app with a temporary database and verify GET /api/health returns exact JSON; create, list, and delete projects.
- Reject an empty/invalid project name with 400 and return the specified error object; return 404 when deleting a missing project.
- Request / and both static assets and verify real TaskBoard HTML, forms/heading, content type, and nonempty assets.
- Verify 204 project deletion has an empty body and the fixture does not touch runtime taskboard.db.
Assertions:
- Project creation is 201, listing is a JSON array ordered by ID, deletion is 204, and missing resources use 404 with {"error": "..."}.
- The app uses the selected temporary path, initializes schema, serves actual HTML rather than a placeholder, and exposes both static files.

### phase-2
Requirement: Add task repository operations, task routes, validation, filtering, and exact task API behavior.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: pending
Phase: phase-2
Scenarios:
- Create/list/patch/delete tasks, including defaults, valid title/description/priority/status changes, omitted PATCH fields, and empty PATCH rejection.
- Reject invalid fields, invalid filters, null PATCH fields, and overlong title/description; return 404 for missing projects/tasks.
- Verify empty task lists serialize as [], deletes are 204 with no body, and status/priority filters compose with AND while preserving ID order.
Assertions:
- API responses contain exact decoded project/task fields and specified status codes; application errors are {"error": "..."}.
- Task state changes persist, project deletion cascades, and filters return only matching tasks in ascending ID order.

Requirement: Provide the real project-selection and Kanban page structure with task form, three columns, empty/error states, and controls needed for create/edit/move/delete flows.
Level: integration
Test file: taskboard/tests/test_ui_content.py
Bead ID: pending
Phase: phase-2
Scenarios:
- GET / contains TaskBoard, project selector/list, project and task forms, priority controls, To Do/Doing/Done headings, and empty/error regions.
- Static app.js and style.css are served with nonempty content containing the required task controls and responsive presentation.
Assertions:
- The response is real text/html and includes all required visible UI regions, not a placeholder.
- The page exposes controls for selection, task editing/deletion, and move-forward behavior, with user-content rendering delegated to the static client.

### phase-3
Requirement: Complete status and priority filter behavior and release browser coverage with independent host-server scenarios.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- On an isolated first load, assert the real TaskBoard heading and To Do, Doing, and Done headings.
- Create a unique project and task, move it todo→doing→done, verify each real task-content transition, and delete it.
- Create two unique-priority tasks, select high, verify only the high-priority task is visible, then reset to all and verify both return.
- Clean up created projects before/after each scenario and run against 127.0.0.1:8080 without a second application.
Assertions:
- Browser assertions inspect actual task titles/cards and column placement, not only HTTP status or placeholders.
- Filtering hides nonmatching cards, restores both cards when reset, and scenarios do not depend on order or pre-existing data.
- The canonical package, lockfile, config, and spec support the specified pytest/npm/Playwright release command.
