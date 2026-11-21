# Test Plan — Taskboard

## Requirements → tests

### phase-1-core
Requirement: The repository/domain layer persists projects and tasks, validates required fields and enum values, enforces title/description length limits, and supports task filtering and project-delete cascade.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: tm-ns3
Phase: phase-1-core
Scenarios:
- Create and retrieve projects and tasks with stable IDs and the documented fields.
- Reject empty or overlong titles/descriptions and invalid status or priority values.
- Apply status and priority filters independently and together as an AND query.
- Delete a project and cascade-delete its tasks; missing records return the repository's documented result.
Assertions:
- Valid records round-trip with the expected values and types.
- Invalid values raise/return the specified validation error without persistence.
- A composed filter returns only records matching both predicates.
- After project deletion neither the project nor its tasks can be retrieved.

### phase-1-app
Requirement: The FastAPI application exposes the documented health, project, task, and static/root routes with SPEC-correct statuses, JSON error objects, validation limits, content types, and runtime-database isolation.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: tm-ssd
Phase: phase-1-app
Scenarios:
- Health, root, and JavaScript/static endpoints return success, nonempty bodies, and their documented media types.
- Project/task create, list, get, update, and delete routes return decoded JSON values with the documented statuses and content types.
- Missing resources return the SPEC error object; malformed integer paths return 422 with the framework validation shape.
- Invalid status/priority, empty fields, and overlong title/description requests return 400 with the documented error object and do not persist data.
- Status plus priority query parameters compose as an AND filter.
- Deleting a project returns 204 with an empty body and removes its tasks.
- The TestClient configured with a temporary database does not read from or write to the runtime taskboard.db.
Assertions:
- Root/static bodies are nonempty; HTML, JavaScript, and JSON responses have the specified content types.
- Response status and decoded JSON keys/types/values match SPEC; 204 has exactly an empty body.
- Every documented 400 response has the required error object, while malformed integer paths are 422.
- Length-boundary and over-limit inputs are handled at the specified limits, and invalid writes are absent from subsequent GETs.
- Combined filters return only rows satisfying both predicates.
- Temporary-database data is isolated and the runtime database remains unchanged.

### phase-2
Requirement: The delivered taskboard UI presents the available projects and tasks and lets a user perform the specified taskboard flows through the running application.
Level: integration
Test file: taskboard/tests/test_ui_content.py
Bead ID: pending
Phase: phase-2
Scenarios:
- Load the running root page and verify the taskboard shell, project/task controls, and seeded data render.
- Create, edit, filter, and delete the user-visible project/task records through the UI.
- Exercise empty, loading, validation-error, and server-error states exposed by the UI.
Assertions:
- Required controls and rendered records are present and remain synchronized with the API.
- Submitted valid data appears with the documented values; invalid data displays an error and does not create a record.
- Filters show only matching records and deletion removes the record from the visible board.

### phase-3
Requirement: The completed browser experience provides the specified responsive styling and client-side interactions without breaking the documented API behavior.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- Exercise the primary taskboard flow at desktop and narrow viewport sizes.
- Verify client-side filtering, refresh/error handling, and static asset loading in the running UI.
Assertions:
- The main layout and controls remain usable at both viewport sizes.
- Interactions update the DOM with the expected records and show recoverable errors.
- Static assets load successfully and API responses retain their documented statuses and media types.
