# Test Plan — Taskboard

## Requirements → tests

### phase-1-core
Requirement: The repository initializes the SQLite schema and supports project/task persistence, ordering, filtering, partial updates, validation, and cascade deletion.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: te-7yg
Phase: phase-1-core
Scenarios:
- Create the schema and persist projects and tasks, including special-character values.
- Return projects and tasks in the specified ordering and filter tasks by project.
- Apply task partial updates without losing unchanged fields.
- Reject invalid project/task values and delete a project together with its dependent tasks.
Assertions:
- Repository operations return the documented records and ordering.
- Invalid values raise the documented validation errors.
- Updating one field preserves the other fields, and deleting a project removes its tasks.

### phase-1-app
Requirement: The application exposes the documented health and project HTTP routes, returns structured errors for invalid or missing resources, isolates each app instance to its configured database, and serves the required project form page and static assets.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-1-app
Scenarios:
- GET the health route and list projects from an isolated temporary database.
- POST a valid project, then GET the collection and DELETE the project; repeat deletion to exercise the 404 response.
- POST missing and blank project names and verify the documented error response.
- Request the root page and static asset, including the required visible heading and project form.
Assertions:
- Health and project routes return the documented status codes and decoded JSON values.
- Successful deletion has status 204 and an empty body; invalid input and missing resources return status 400/404 with an error field.
- A fresh configured database does not expose data from another app instance.
- The root response contains the required heading/form and the static asset is delivered successfully.

### phase-2
Requirement: The phase-2 delivery adds the specified task HTTP behavior and user-visible task interactions.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-2
Scenarios:
- Exercise each task route documented for phase 2, including project scoping, creation, listing, update, and deletion.
- Exercise invalid task payloads and missing task/project resources.
Assertions:
- Task responses use the documented status codes and decoded JSON fields.
- Invalid and missing resources return the documented error shape without mutating stored data.

### phase-3
Requirement: The phase-3 delivery provides the specified browser task-management flow and preserves the API-backed state.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- Load the application in a browser, create/select a project, and create and display its tasks.
- Edit and delete a task and verify the rendered list reflects the API-backed state.
Assertions:
- Required controls and project/task content are visible.
- Browser actions produce the documented state changes and do not show stale deleted data.
