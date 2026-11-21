# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: Persist projects and tasks in SQLite and expose the repository operations specified by the store contract.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: tm-ns3
Phase: phase-1-core
Scenarios:
- Initialize an isolated database, create a project, and list and retrieve it with its tasks.
- Create, update, list, and delete tasks, including filtering by project and status and deleting a project with its tasks.
- Verify empty results, missing identifiers, invalid status values, and parameterized persistence across a reopened connection.
Assertions:
- Returned records contain the contract fields and preserve task status, priority/position, descriptions, and timestamps.
- Mutations affect only the addressed project/task; missing records produce the repository's specified not-found result and invalid values are rejected.
- Schema initialization is idempotent and foreign-key cascade behavior is enforced.

### phase-1-app
Requirement: Serve the TaskBoard page and implement the documented project/task HTTP API with the specified validation, status codes, and JSON shapes.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: tm-ns3
Phase: phase-1-app
Scenarios:
- Exercise the root page and each documented project and task endpoint through the FastAPI application with a temporary database.
- Create, read, update, and delete projects and tasks; exercise status updates/filtering and malformed, invalid, missing, or unknown resources.
- Request the static browser assets and verify API responses use JSON for successful and error responses.
Assertions:
- Routes return the documented status codes, decoded JSON keys and value types, and the created/updated resource values.
- Invalid request bodies and invalid status values return the documented client error without changing stored data; unknown IDs return the documented not-found response.
- The root response is successful HTML and static assets are reachable; API content types and required response fields are correct.

### phase-2
Requirement: Render the server-provided board and expose the required task/project controls and columns in the browser-facing page.
Level: integration
Test file: taskboard/tests/test_ui_content.py
Bead ID: tm-ns3
Phase: phase-2
Scenarios:
- Load the page with an empty database and with projects/tasks in each supported status.
- Verify project creation and task creation/editing/deletion controls and movement between the todo, doing, and done columns through the API-backed page contract.
- Verify empty-state rendering, visible error regions, safe user-content rendering, and display of task title, description, status, priority, and project context.
Assertions:
- The page loads successfully and contains the required board columns, forms, controls, empty/error regions, and asset references.
- Served client content uses the specified API paths and textContent-safe rendering for user content; static assets are nonempty.
- The content and API integration assertions cover the task state transitions, filtering, validation, and deletion behavior without introducing alternate routes or layouts.

### phase-3
Requirement: Complete the documented browser acceptance flow against the running local application.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: tm-ns3
Phase: phase-3
Scenarios:
- Start the application with an isolated database, open the root page, create a project and task, and verify the task is visible.
- Edit the task, move it through the supported statuses, reload, and delete it and the project.
Assertions:
- Browser-visible labels, controls, and task values match the API-backed state after each action.
- Status movement is reflected in the corresponding column and survives reload.
- Deletion removes the task/project from the UI and subsequent API-backed reload shows no stale record.
