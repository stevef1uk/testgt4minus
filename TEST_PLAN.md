# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: Provide the SQLite foundation, validated project/task models, repository persistence, deterministic ordering/filtering, partial updates, UTC timestamps, parameterized writes, and cascade deletion.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: te-7yg
Phase: phase-1-core
Scenarios:
- Initialize a new database repeatedly and verify empty project/task collections, required tables, foreign keys, busy timeout, and the project-task index.
- Create projects and tasks containing Unicode and special characters, then verify ascending project/task IDs, defaults, and explicit UTC timestamps.
- Filter tasks by status, priority, and both filters together, while preserving ascending ID order.
- Partially update title, description, priority, and status while omitted fields remain unchanged.
- Delete a project and verify its dependent tasks are removed by cascade.
- Exercise invalid names, titles, descriptions, statuses, and priorities.
Assertions:
- Repository results match the documented project/task JSON fields and types.
- Schema initialization is idempotent and each test uses its supplied temporary database.
- Validation rejects empty or overlong values and unknown enum values.
- Combined filters use AND semantics; updates preserve omitted values; cascade deletion leaves no orphan tasks.
- Timestamps include an explicit UTC offset without asserting an exact wall-clock value.

### phase-1-app
Requirement: Expose the health and project HTTP API, initialize the configured database through create_app, render real root HTML, and serve the canonical static assets with documented status and response shapes.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-1-app
Scenarios:
- Create isolated clients through the conftest fixture with explicit temporary database paths and verify the database is initialized.
- Request GET /api/health and verify the exact decoded response.
- Create projects with trimmed names, list them in ascending ID order, verify an empty collection is [], and delete existing and missing projects.
- Submit empty, whitespace-only, and overlong project names.
- Request /, /static/app.js, and /static/style.css.
Assertions:
- create_app uses the configured database and separate fixtures do not share state or touch the runtime database.
- Health returns 200 and {"status":"ok"}; project creation returns 201; list returns 200; successful deletion returns 204 with no body; missing deletion returns the documented 404 error object.
- Project names are trimmed, IDs are ascending, and invalid names return the documented application-level 400 JSON error.
- Root content is real HTML containing the TaskBoard heading and project form; both canonical assets return 200 with nonempty content and appropriate content types.
- Assertions compare decoded JSON values, keys, and types rather than insignificant whitespace or key order.

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
- Verify the rendered page contains project selection, task form, three Kanban headings, task controls, empty-state, and error regions.
Assertions:
- Task routes return the documented 201, 200, 204, 400, 404, and framework 422 responses with decoded JSON shapes.
- Invalid requests do not mutate stored state; PATCH preserves fields omitted from the request and does not reassign projects.
- Project deletion cascades to its tasks, and an empty task list serializes as [].
- The page exposes To Do, Doing, and Done columns plus required project/task controls and content hooks.

Level: integration
Test file: taskboard/tests/test_ui_content.py
Bead ID: te-w1w
Phase: phase-2
Scenarios:
- Fetch the root page after the task/Kanban markup is delivered.
- Inspect the HTML for project controls, task fields, priority controls, move/edit/delete controls, filter controls, empty/error regions, and all three columns.
- Fetch both canonical static assets and inspect their nonempty content.
Assertions:
- Rendered content is a real TaskBoard page and includes the specified user-visible controls without a placeholder-only response.
- Static asset responses are successful and nonempty.
- Required task and project content hooks are present at the canonical paths.

### phase-3
Requirement: Complete status and priority filtering and prove the independent browser flows for loading, project/task creation, Kanban movement, deletion, and filtered task visibility against the running application.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- Load a clean application and verify the TaskBoard heading and To Do, Doing, and Done columns.
- Create a uniquely named project and task through the browser, verify the task in To Do, move it to Doing and Done, then delete it and verify it disappears.
- Create two uniquely named tasks with different priorities, select the high-priority filter, verify only the high-priority task is rendered, then reset the filter and verify both tasks return.
- Use independent setup/cleanup so scenarios do not depend on prior projects, task order, or previous runs.
Assertions:
- Browser assertions inspect real task titles, priorities, columns, and rendered state rather than only HTTP status or placeholder visibility.
- Move forward changes the task through todo, doing, and done; done tasks hide or disable Move forward.
- Filtering uses the documented status/priority controls and excludes filtered-out cards, then restores the complete list.
- Created/deleted state is API-backed and remains consistent after refresh; generated project data is cleaned up before or after each scenario.
