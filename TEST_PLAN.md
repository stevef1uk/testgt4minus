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
Requirement: The runnable application exposes the health and project HTTP routes, initializes the configured database, renders the real project page, and serves both static assets.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-1-app
Scenarios:
- Create an isolated app with a temporary database and verify the health endpoint returns the exact documented JSON.
- Create trimmed projects, list them in ascending ID order, delete one successfully, and request a missing project deletion.
- Submit empty or whitespace-only project names and verify structured validation errors; verify an empty project list is an empty JSON array.
- Request the root page and both canonical static assets and verify the rendered project form and nonempty responses.
Assertions:
- Health and project endpoints return the documented decoded JSON values and status codes; successful deletion is 204 with an empty body, while invalid and missing operations return the documented error shape.
- Project names are trimmed and persisted, IDs remain ordered, and isolated app instances do not share database state.
- The root response is real HTML containing the TaskBoard heading and project form, and `/static/app.js` and `/static/style.css` return 200 with nonempty content.

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
