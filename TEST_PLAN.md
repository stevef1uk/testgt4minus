# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: Persist projects and tasks in SQLite with idempotent schema setup, parameterized repository operations, model validation, JSON mapping, and UTC-aware creation timestamps.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: te-7yg
Phase: phase-1-core
Scenarios:
- Create a project and task through the repository and read them back with stable integer IDs and the expected fields.
- Create multiple projects and verify IDs/order are ascending; verify duplicate/idempotent schema initialization does not destroy data.
- Verify an overlong project name is rejected by the model/API boundary and that stored timestamps have an explicit UTC offset.
Assertions:
- Repository rows round-trip to the specified model/JSON values and foreign-key task ownership is preserved.
- Returned project ordering is ascending by ID, validation rejects names beyond the specified maximum, and created_at.utcoffset() equals UTC.

### phase-1-app
Requirement: Expose the specified project/task HTTP API, render the TaskBoard page, and serve JavaScript and CSS with canonical content types.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-1-app
Scenarios:
- GET the page and assert the visible TaskBoard heading and project form; create more than one project and retrieve them through the API.
- Submit a project name longer than the specified limit and assert HTTP 422 with the documented validation response.
- Request the JavaScript and CSS static assets and exercise the documented API responses/statuses and JSON fields.
Assertions:
- The page contains a visible `TaskBoard` heading and a project form, project creation succeeds, and list results are ordered by ascending ID.
- Invalid project input returns 422; API responses have the specified status/content type and decoded JSON values; JavaScript is `application/javascript` and CSS is `text/css`.

### phase-2
Requirement: Add task repository/API behavior and the visible project-selection and Kanban workflows, including task creation, editing, deletion, status movement, empty states, and visible API errors.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-2
Scenarios:
- Create a project and exercise project-scoped task creation, listing, PATCH updates, and deletion.
- Verify task defaults, title trimming, description behavior, priority/status changes, project scoping, ID ordering, and combined filters.
- Submit invalid task titles, descriptions, statuses, priorities, null PATCH values, empty PATCH objects, and missing project/task IDs.
Assertions:
- Task routes return the documented 201, 200, 204, 400, 404, and framework 422 responses with decoded JSON shapes.
- Invalid requests do not mutate stored state; PATCH preserves omitted fields and does not reassign projects.
- Project deletion cascades to its tasks, and empty task lists serialize as [].

Level: integration
Test file: taskboard/tests/test_ui_content.py
Bead ID: te-c2c
Phase: phase-2
Scenarios:
- Fetch the root page and inspect project/task forms, selectors, filters, Kanban columns, task controls, empty-state, and error regions.
- Fetch both canonical static assets and inspect their nonempty content.
Assertions:
- The rendered page contains the required TaskBoard controls, To Do, Doing, and Done headings, and visible content hooks.
- Static assets return successful, nonempty responses at the canonical paths.

### phase-3
Requirement: Complete status and priority filtering and prove independent browser flows for loading, project/task creation, Kanban movement, deletion, and filtered task visibility against the running application.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending (future phase bead)
Phase: phase-3
Scenarios:
- Load a clean application and verify the TaskBoard heading and To Do, Doing, and Done columns.
- Create a uniquely named project and task through the browser, move it from To Do to Doing to Done, delete it, and verify it disappears.
- Create two uniquely named tasks with different priorities, select the high-priority filter, verify only the high-priority task is rendered, then reset the filter and verify both return.
Assertions:
- Browser assertions inspect real task titles, priorities, columns, and rendered state rather than only HTTP status or placeholder visibility.
- Move-forward changes the task through todo, doing, and done; done tasks hide or disable Move forward.
- Filtering excludes filtered-out cards and restores the complete list; scenarios use independent setup and cleanup.
