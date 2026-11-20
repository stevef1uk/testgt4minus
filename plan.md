# Phase 2 implementation plan: Tasks and Kanban UI

The phase delivers the browser-facing project/task board while preserving the API and
repository contracts established by the backend phases. All implementation and test
paths below are repo-relative and use the existing taskboard package layout.

## Verification and concrete acceptance

Run from the rig root:
`cd taskboard && python -m pytest -q tests`

The completed phase must render the project form, project list/filter, loading,
empty, and error regions; load `/static/app.js` and `/static/style.css`; use the
`/api/projects` routes to load and create projects; and render server/API data with
DOM-safe text operations (not HTML injection). The client must provide the
task/Kanban interaction specified by the architecture: project selection, task
columns, task creation/editing and moving between columns, with visible loading and
error feedback. Tests must prove both successful and failure responses rather than
only checking that files exist.

## Bead map

### te-uz4: taskboard/tests/test_ui_content.py
- Scope: Add structural UI contract tests for the template and browser bundle.
- Architecture: Architecture UI test section; checks the required regions, static
  asset links, safe rendering, and project API route references.
- Interfaces: Test assertions consume the exact IDs `project-form-region`,
  `project-form`, `project-list`, `project-filter`, `empty-state`,
  `loading-state`, and `error-state`, plus `/static/app.js`, `/static/style.css`,
  `/api/projects`, `textContent`, and `replaceChildren`.
- Depends on: taskboard/templates/index.html; taskboard/static/app.js; taskboard/static/style.css
- Consumed by: phase-2 UI acceptance
- Acceptance: Tests fail when any required region or asset link is absent; tests
  require `/api/projects` and safe DOM APIs (`textContent` and `replaceChildren`).
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xa1: taskboard/templates/index.html
- Scope: Implement the complete HTML shell for project management and the
  task/Kanban board, including the required state regions and form controls.
- Architecture: Architecture template/UI ownership section.
- Interfaces: Provides the template consumed by the application route and loads
  `/static/app.js` and `/static/style.css`; owns the required element IDs listed
  in the UI tests.
- Depends on: <none>
- Consumed by: taskboard/tests/test_ui_content.py; taskboard/static/app.js
- Acceptance: Include project form/list/filter plus empty, loading, and error
  states; include the board/task controls and stable semantic hooks needed by
  `app.js`; load both static assets at the exact paths.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Style the project view and responsive Kanban layout, including visible
  state messages, cards, columns, forms, and controls.
- Architecture: Architecture stylesheet ownership section.
- Interfaces: Provides the selectors/classes used by `index.html` and `app.js`;
  no backend symbols or new configuration are introduced.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/tests/test_ui_content.py; browser template
- Acceptance: The project form/list and board are readable and distinct; loading,
  empty, and error states remain visible; columns and task cards are usable at
  the supported narrow and wide layouts described by the architecture.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-h52: taskboard/static/app.js
- Scope: Implement browser state, project loading/creation/filtering, board
  rendering, task operations, and user-visible loading/error handling.
- Architecture: Architecture JavaScript ownership and API interaction section.
- Interfaces: Calls `/api/projects` and the task endpoints defined by the
  architecture; binds the template's form, filter, project, board, and state
  hooks; exports no server-side symbols.
- Depends on: taskboard/templates/index.html; taskboard/static/style.css
- Consumed by: taskboard/tests/test_ui_content.py; browser runtime
- Acceptance: Load and create projects through the specified API routes; filter
  the project list; select a project and render its tasks in the specified
  Kanban columns; create/edit/move tasks using the documented routes; update
  loading, empty, and error regions; render API-provided text through safe DOM
  APIs and replace rendered children without unsafe HTML.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Provide the isolated FastAPI test client fixture and per-test SQLite
  database setup.
- Architecture: Architecture test fixture section.
- Interfaces: Provides pytest fixture `client`, reloads `taskboard.main`,
  calls `create_app`, and sets `TASKBOARD_DB_PATH` to a temporary database.
- Depends on: taskboard/main.py (backend phase)
- Consumed by: taskboard/tests/test_repository.py; taskboard/tests/test_api.py
- Acceptance: Each test receives an application backed by its own temporary
  database and can exercise the FastAPI client without sharing persistent state.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Test the repository behavior required by the project/task board,
  including persistence and task status/order operations.
- Architecture: Architecture repository test section.
- Interfaces: Exercises the repository functions and entities named in the
  architecture, including project/task CRUD and status movement contracts.
- Depends on: taskboard/internal/repository.py (backend phase)
- Consumed by: phase-2 backend/UI regression gate
- Acceptance: Prove project and task creation, retrieval, update, deletion,
  filtering/list behavior, and persistence across repository calls; prove the
  documented Kanban status/order transition behavior and relevant validation.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Test the HTTP API used by the browser for projects and Kanban tasks.
- Architecture: Architecture API test section and endpoint table.
- Interfaces: Exercises the documented FastAPI routes, request payloads, JSON
  response shapes, status codes, and validation/error responses.
- Depends on: taskboard/tests/conftest.py; taskboard/main.py; taskboard/internal/repository.py
- Consumed by: taskboard/static/app.js; phase-2 verification
- Acceptance: Prove project list/create and task list/create/update/move/delete
  requests return the specified JSON and status codes; prove project scoping,
  persistence, and documented invalid-input/not-found responses used by the UI.
- Verify: `cd taskboard && python -m pytest -q tests`

## Delivery order

Implement the template and stylesheet hooks first, then the JavaScript behavior.
Keep fixture, repository, and API tests aligned with the existing backend
interfaces; do not add routes, fields, or configuration outside SPEC.md and
architecture.md.
