# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: Provide the SQLite foundation, validation/mapping, project and task persistence, ordering, defaults, UTC timestamps, filtering, partial updates, cascade deletion, and isolated repository coverage.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: tm-ns3
Phase: phase-1-core
Scenarios:
- Initialize a new database repeatedly and verify empty collections, required schema/index behavior, foreign keys, and the configured busy timeout.
- Create projects and tasks, verify trimmed names/titles, ascending IDs, task defaults, explicit UTC timestamps, and Unicode/length validation.
- List tasks with status, priority, and combined filters; update any supported task subset while preserving omitted fields.
- Delete a project and verify its tasks cascade; verify missing project/task operations return the repository's not-found result.
Assertions:
- Repository results match the specified project/task JSON fields and deterministic ID order.
- Invalid values are rejected, writes are parameterized, and persistence survives separate repository connections.
- Combined filters use AND semantics and cascade deletion leaves no child tasks.

### phase-1-app
Requirement: The application exposes the specified project API routes and wires them to the repository.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-1-app
Scenarios:
- Create an app with the fixture's temporary database and call `/api/health`, project create/list/delete, and missing-project deletion.
- Request `/` and both static asset paths; submit invalid and valid project names and inspect the project round trip.
Assertions:
- Health decodes exactly as `{"status": "ok"}`; project creation is 201, listing is ID-ordered, deletion is bodyless 204, and missing resources are 404 with the specified error JSON.
- Root is 200 `text/html` containing a real TaskBoard page, and both static responses are 200 and nonempty.
- Tests use a fresh explicit temporary database and do not touch the runtime database.

### phase-2
Requirement: Add task repository/API behavior and the user-visible project/task Kanban workflow: selection, creation, editing, deletion, todo→doing→done movement, validation, empty/error states, and safe rendering.
Level: integration
Test file: taskboard/tests/test_repository.py
Bead ID:
Phase: phase-2
Scenarios:
- Create tasks through repository operations with defaults, filter them, update title/description/priority/status partially, and delete through project cascade.
Assertions:
- Task state changes, defaults, validation, filter conjunction, ordering, and cascade behavior match the contract without weakening earlier persistence assertions.

Requirement: Expose project-scoped task list/create routes and task patch/delete routes with exact success/error statuses, JSON shapes, validation, missing-resource behavior, empty arrays, bodyless deletes, and composed filters.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-2
Scenarios:
- Create a project and tasks, list them in ID order, apply status and priority filters together, patch each supported field while preserving omitted fields, and delete a task.
- Exercise default task fields, trimmed/empty and overlong inputs, invalid enums, null PATCH fields, empty PATCH, unknown project/task IDs, malformed integer paths, and empty lists.
Assertions:
- Task create/update/list/delete responses use the specified decoded JSON values, status codes, and timestamps with explicit UTC offsets.
- Invalid application inputs return 400 error objects, missing resources return 404 error objects, malformed paths retain 422, and deletes have no body.
- Filtered results contain only matching tasks and preserve ascending IDs.

Requirement: Render the real TaskBoard page with project/task forms, project selection, three Kanban columns, controls, empty/error regions, and safe static client behavior.
Level: integration
Test file: taskboard/tests/test_ui_content.py
Bead ID:
Phase: phase-2
Scenarios:
- Fetch the rendered page and inspect the project form, task form, selectors, priority controls, `To Do`/`Doing`/`Done` columns, and empty/loading/error regions.
- Inspect served JavaScript and CSS for nonempty content, `/api/projects` usage, safe `textContent` rendering, and replacement of rendered children.
Assertions:
- Required UI regions and controls exist in the real template and both static assets are served.
- Client code uses safe text insertion rather than raw user-content HTML and calls the specified project/task API paths.
- The page supports the specified visible Kanban and empty/error structure without introducing alternate routes or layouts.

### phase-3
Requirement: Complete status/priority filtering and release coverage with three independent browser acceptance scenarios against the running host application.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- Load the real page and verify the TaskBoard heading and all three column headings.
- Create a unique project and task, move it from To Do to Doing to Done, verify real task text/state, delete it, and verify it disappears; clean up independently.
- Create two uniquely named tasks with different priorities, select the high filter, verify only the high-priority task is rendered, reset the filter, and verify both return.
Assertions:
- Browser interactions use the real forms and controls, inspect task content and columns, and observe each persisted state transition.
- Filters send the specified query parameters, combine correctly, and do not render filtered-out cards.
- Each scenario is order-independent, uses unique data and cleanup, and runs through the canonical host configuration without a second app or container.
