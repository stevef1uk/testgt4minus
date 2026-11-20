# Test Plan — TaskBoard

## Requirements → tests

### phase-1-core
Requirement: Deliver the SQLite schema, validation/mapping, project and task repository foundations with idempotent initialization, foreign keys, busy timeout, UTC timestamps, deterministic ordering, filtering, partial updates, cascade deletion, and parameterized writes.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: te-7yg
Phase: phase-1-core
Scenarios:
- Initialize a new database repeatedly and verify empty project/task collections without schema errors.
- Create projects and tasks, verify ascending IDs, UTC-offset timestamps, task defaults, status/priority filters including AND composition, and preservation of omitted patch fields.
- Delete a project and verify its tasks are removed by the foreign-key cascade.
Assertions:
- Repository results match the specified project/task JSON fields and deterministic ordering.
- Invalid values are rejected by the model/repository boundary, writes do not interpolate request data, and cascade/filter/update behavior changes persisted state as specified.

### phase-1-app
Requirement: Provide a runnable FastAPI app factory with exact health and project API routes, isolated database selection, real HTML root rendering, and mounted static assets.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-1-app
Scenarios:
- Create an isolated app client, verify `GET /api/health` returns the exact health object, and verify project create/list/delete round trips with ascending IDs.
- Submit empty or whitespace-only project names and delete a missing project; inspect application error JSON and status codes.
- Request `/` and both static assets, checking the real TaskBoard page and nonempty served files.
Assertions:
- Valid project creation returns 201, deletion returns 204 with an empty body, missing deletion returns 404, and invalid names return 400 with an `error` field.
- Root content is HTML containing `TaskBoard`, the project form, task form, and `To Do`, `Doing`, and `Done`; static responses are 200 and nonempty.
- Tests use a fresh temporary SQLite path and never touch the runtime database.

### phase-2
Requirement: Add task persistence and API behavior, project selection, task creation/edit/delete, three Kanban columns, move-forward behavior, visible empty/error states, and safe rendering while preserving Phase 1 behavior.
Level: integration
Test file: taskboard/tests/test_api.py
Bead ID: te-c2c
Phase: phase-2
Scenarios:
- Create a project and task, list tasks, patch each supported field while preserving omitted fields, and delete the task.
- Verify missing project/task responses, invalid title/description/status/priority values, empty PATCH rejection, empty lists, and composed query filters with ID ordering.
- Verify project selection and task UI content through the required content-test surface, including forms, columns, empty/error regions, and static assets.
Assertions:
- Task creation returns 201 with `todo` status and default `medium` priority; patch returns 200 and does not permit project reassignment.
- Invalid task inputs return 400, missing resources return 404, deletes return bodyless 204, and project deletion removes its tasks.
- The UI exposes task title/description/priority controls, Move forward/Edit/Delete controls, and hides or disables Move forward for done tasks; user text is inserted safely.



### phase-3
Requirement: Complete status and priority filters and provide independent Playwright browser coverage for initial rendering, task lifecycle, and priority filtering against the running server.
Level: ui
Test file: taskboard/playwright/taskboard.spec.ts
Bead ID: pending
Phase: phase-3
Scenarios:
- Load the running UI and verify the TaskBoard heading and all three Kanban column headings.
- Create a uniquely named project and task, move it from To Do to Doing to Done, delete it, and verify each visible state change.
- Create two differently prioritized tasks, filter to high priority, verify only the high-priority card is shown, then reset the filter and verify both cards return.
Assertions:
- Browser assertions inspect real task titles and column placement, not only status codes or placeholder visibility.
- Each scenario uses unique data and cleanup, remains independent of test order, and verifies that filter query parameters exclude and restore the appropriate cards.
- Done tasks hide or disable Move forward; browser tests run through the canonical Playwright configuration and host server without creating a second application.
---END WRITE
