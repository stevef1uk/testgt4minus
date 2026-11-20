# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: Deliver the SQLite foundation, validation/mapping, project and task schema invariants, repository operations, and isolated repository coverage.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: te-7yg
Phase: phase-1-core
Scenarios:
- Initialize the database idempotently; verify empty results, foreign-key cascade support, and ascending project IDs.
- Create projects and tasks with trimmed values, defaults, UTC timestamps, and parameterized writes.
- Filter tasks by status and priority, update partially, and verify omitted fields persist.
- Delete projects with cascading tasks and reject invalid or overlong values.
Assertions:
- Rows have exact fields, positive IDs, UTC timestamps, and stable ordering.
- Defaults, filters, partial updates, schema setup, validation, and cascade deletion produce specified state.

### phase-1-app
Requirement: Provide app creation, database selection, health and project routes, HTML/static delivery, isolated fixtures, and project API coverage.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-7yg
Phase: phase-1-app
Scenarios:
- Use a temporary database; verify health, project create/list/delete, invalid names, and missing-project 404.
- Verify root HTML, both static assets, content types, forms, heading, and nonempty bodies.
- Verify 204 deletion is bodyless and tests do not modify runtime taskboard.db.
Assertions:
- Responses use specified status codes and decoded JSON error objects.
- The selected database is initialized and real HTML/assets are served.

### phase-2
Requirement: Add task repository operations, task routes, validation, filtering, and exact task API behavior.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-7yg
Phase: phase-2
Scenarios:
- Create, list, patch, and delete tasks with defaults, valid updates, omitted PATCH fields, and empty PATCH rejection.
- Reject invalid fields, filters, nulls, and overlong values; return 404 for missing resources.
- Verify empty arrays, bodyless 204 responses, conjunctive filters, ascending IDs, and project-delete cascades.
Assertions:
- Responses contain exact decoded fields and specified statuses; errors are {"error": "..."}.
- Persisted task state and filtering match the requested operations.

Requirement: Provide the real project-selection and Kanban page structure with task form, three columns, empty/error states, and controls for create/edit/move/delete.
Level: integration
Test file: taskboard/tests/test_ui_content.py
Bead ID: te-7yg
Phase: phase-2
Scenarios:
- Verify root content contains TaskBoard, project controls, forms, priority controls, three column headings, and empty/error regions.
- Verify app.js and style.css are nonempty and expose task controls and responsive presentation.
Assertions:
- The response is real text/html with every required visible region.
- Controls expose selection, editing, deletion, and move-forward behavior.

### phase-3
Requirement: Complete status and priority filter behavior and release browser coverage with independent host-server scenarios.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- On isolated load verify the heading and all three columns.
- Create unique tasks, move todo to doing to done, verify cards, and delete them.
- Filter two unique-priority tasks by high, then reset to all; clean up and use 127.0.0.1:8080.
Assertions:
- Browser assertions inspect cards and column placement, not only statuses.
- Filtering hides and restores cards independently of pre-existing data.
- The canonical Playwright command and host-server configuration are supported.
