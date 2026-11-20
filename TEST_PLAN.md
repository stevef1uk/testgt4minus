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
Requirement: The runnable application exposes the health and project HTTP routes, initializes the configured database, renders real root HTML, and serves both canonical static assets.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-1-app
Scenarios:
- Create an isolated app with a temporary database and verify GET /api/health returns exactly {"status":"ok"}.
- Create trimmed projects, verify ascending ID ordering and empty-list serialization, then delete an existing and a missing project.
- Submit empty and whitespace-only names and verify the documented 400 error shape.
- Request the root page and both canonical static assets.
Assertions:
- Health and project endpoints return the documented decoded JSON values and status codes; successful deletion is 204 with an empty body and missing deletion is 404 with an error object.
- Project names are trimmed and persisted, IDs remain ordered, and isolated clients do not share database state.
- Invalid project names return the documented application-level validation response.
- The root response is real HTML containing the TaskBoard heading and project form, while app.js and style.css return 200 with nonempty content.

### phase-2
Requirement: The phase-2 delivery adds the specified task HTTP behavior and user-visible task interactions.
Level: integration
Test file: taskboard/tests/test_api.py
Test file: taskboard/tests/test_ui_content.py
Bead ID: pending
Phase: phase-2
Scenarios:
- Exercise each task route documented for phase 2, including project scoping, creation, listing, update, and deletion.
- Exercise invalid task payloads and missing task/project resources.
- Verify the phase-2 HTML contains the required task-management controls and project/task content hooks.
Assertions:
- Task responses use the documented status codes and decoded JSON fields.
- Invalid and missing resources return the documented error shape without mutating stored data.
- The UI-content test finds the required controls and content structure in the rendered page.

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
