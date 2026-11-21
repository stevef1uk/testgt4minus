# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: Deliver the SQLite foundation, validation/mapping, project and task repository behavior, schema invariants, and persistence tests.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: tm-ns3
Phase: phase-1-core
Scenarios:
- Initialize a new temporary database twice and verify empty project/task collections, idempotent schema setup, foreign keys, and busy timeout.
- Create projects and tasks, verify trimmed values, ascending IDs, default todo/medium values, explicit UTC timestamps, and status/priority filters including AND composition.
- Patch selected task fields while preserving omitted fields, then delete a project and verify its tasks cascade away.
Assertions:
- Repository results match the specified decoded project/task shapes and deterministic ID ordering.
- Validation rejects empty/overlong titles, overlong descriptions, and unknown status/priority values; writes use persisted state and timestamps carry UTC offsets.
- A deleted project leaves no child tasks, while an empty/new database returns `[]`.

### phase-1-app
Requirement: Deliver the runnable FastAPI app, health and project CRUD HTTP routes, isolated fixture, real HTML root, and static asset serving while preserving the core repository contract.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: tm-j2d
Phase: phase-1-app
Scenarios:
- Use the fresh temporary-database client fixture to verify `GET /api/health` and confirm the isolated test database is used rather than runtime `taskboard.db`.
- Exercise project create/list/patch/delete round trips, including required validation, deterministic ordering, missing-resource behavior, and bodyless 204 deletion.
- Request `/` and the canonical JavaScript and CSS asset paths, checking the real HTML shell and successful static responses.
Assertions:
- `/api/health` returns status 200 and decoded JSON `{"status":"ok"}`; project responses have the specified decoded fields/types and status codes.
- Invalid project names and missing projects produce the documented API error responses; delete returns 204 with no response body.
- Root and static responses have the specified HTML/asset content types and nonempty content, and API tests do not modify the runtime database.

### phase-2
Requirement: Extend the application with project selection, task creation/edit/delete, three Kanban columns, move-forward behavior, and visible empty/error states.
Level: integration
Test file: taskboard/tests/test_ui_content.py
Bead ID: pending
Phase: phase-2
Scenarios:
- Request the rendered page and assert project selector/list, task form controls, priority options, three column headings, task-card controls, and empty/error regions are present.
- Use API-backed test setup to create a project and tasks, then verify the page/API contract supports selection and task state transitions through todo, doing, and done.
- Verify edit and delete operations update or remove only the selected task and that empty project/task states are represented.
Assertions:
- `GET /` is real HTML containing `TaskBoard`, both forms, `To Do`, `Doing`, and `Done`; static assets are nonempty and served at canonical paths.
- Task create/edit/delete and move-forward requests produce documented decoded JSON/status results, with done tasks lacking an enabled move-forward control.
- User-provided content is rendered safely via text content rather than raw HTML, and API failures are visible in the error region.

### phase-3
Requirement: Complete status/priority filters and ship independent Playwright browser acceptance scenarios with full pytest and release verification.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- Load a clean server and verify the real heading and all three Kanban headings.
- Create a unique project and task, move it todo→doing→done, delete it, and verify each visible state and disappearance.
- Create two uniquely named tasks with different priorities, filter to high, verify only the high-priority task, then reset and verify both tasks; clean up created projects.
Assertions:
- Browser assertions inspect real task text and column/state placement, not merely HTTP status or placeholders.
- Filter controls issue the documented status/priority query combinations and filtered-out cards are not rendered; reset restores both tasks.
- Each scenario is independent and uses cleanup against the persistent local server without introducing a second app or noncanonical test path.
