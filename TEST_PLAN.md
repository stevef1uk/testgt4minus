# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: The repository initializes the SQLite schema idempotently, creates projects and tasks with defaults and timestamps, lists in stable order, filters by status and priority, updates partially, deletes projects with cascading tasks, rejects invalid status/priority values, and uses parameterized SQL writes.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: te-7yg
Phase: phase-1-core
Scenarios:
- Initialize a new database twice and verify the schema and empty collections remain usable.
- Create records with default status/priority and verify timestamps, ordering, filters, partial updates, and project deletion cascade.
- Attempt invalid status and priority values and verify they are rejected without modifying stored data.
- Use values containing quotes/SQL metacharacters in create and update writes and verify they round-trip as data rather than altering the query or schema.
Assertions:
- Invalid status and priority writes raise the specified validation error and leave the record unchanged.
- Values are bound as parameters: special-character values are stored literally, no SQL is executed from them, and the database remains queryable.
- Returned records have the documented defaults, ordering, filters, update results, and cascade behavior.

### phase-1-app
Requirement: The HTTP application exposes the documented health and project CRUD behavior, returns the specified error status/body shape, isolates each configured database, and serves the TaskBoard root page with its heading, project form, and static assets.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-1-app
Scenarios:
- Request the health endpoint and create, list, update, and delete projects through the API.
- Submit malformed, missing, and unknown project data and verify the documented error status and JSON shape.
- Request the root page and inspect its visible TaskBoard heading, project form, and references to the static application assets.
- Create data against separate configured temporary databases and verify that one client cannot see the other client's data.
Assertions:
- Health and CRUD responses have the documented status codes, content types, decoded JSON keys, and values.
- Invalid requests return the required error status and body fields without creating a project.
- The root response contains the required TaskBoard heading and project form, and static resources are delivered successfully.
- Database isolation is preserved across application instances.

### phase-2
Requirement: The delivered task-board UI content exposes the documented project/task controls, task fields, status and priority choices, and the project/task empty and populated states.
Level: ui
Test file: taskboard/tests/test_ui_content.py
Bead ID: pending
Phase: phase-2
Scenarios:
- Inspect the served UI markup for project creation and task creation controls and the required labels/fields.
- Verify status and priority controls contain the documented choices and that empty and populated project/task containers are present.
Assertions:
- Required controls, labels, field names, and choice values are present in the UI content.
- The UI provides distinct containers/states for no projects, no tasks, and rendered project/task cards.

### phase-3
Requirement: A browser-driven user can create and manage projects and tasks through the running TaskBoard UI, move tasks through the documented workflow, and cannot move a done task forward.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- Run the canonical Playwright configuration against the host server, create a project and task, and verify both appear in the appropriate cards.
- Edit task fields and move the task through the available status controls, including the done state.
- Reload the page and verify persisted data remains visible; verify done tasks hide or disable Move forward.
Assertions:
- Browser-visible project/task names and updated fields match the submitted values.
- Status transitions update the rendered task card and persist after reload.
- A done task has no enabled Move forward action, while the appropriate cards expose the documented controls.
