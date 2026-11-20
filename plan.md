# Phase 1 implementation plan: runnable Taskboard app

The phase-1 deliverable is the six active files below. Work only on these paths and preserve the later-phase ownership described in architecture.md. The required verification command for every bead and for the phase is `cd taskboard && python -m pytest -q tests`.

## Bead map

### te-hky: taskboard/main.py
- Scope: Implement the FastAPI application factory, SQLite-backed task persistence, request/response handling, and static/template mounting assigned to this phase.
- Architecture: Follow architecture.md § Application entrypoint and § persistence/API contract; use the SPEC data model and HTTP table exactly.
- Interfaces: Export `create_app(database_path: str | None = None)` and provide the SPEC routes for the HTML page and task JSON API. Keep the documented task fields, status values, and JSON response shapes.
- Depends on: taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py
- Acceptance: A fresh database is usable without manual setup; the app serves the board page and exposes the SPEC task-list create/update/delete behavior; requests persist across app instances; invalid or missing task input receives the SPEC-described HTTP response; responses contain the documented task fields.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-fzd: taskboard/templates/index.html
- Scope: Provide the complete board document and the semantic controls/containers required by the SPEC.
- Architecture: Follow architecture.md § frontend template and the SPEC UI requirements; reference the phase static stylesheet and JavaScript asset.
- Interfaces: Supply the board root, task creation form, task list container, filter/status controls, and script/style links expected by app.js.
- Depends on: <none>
- Consumed by: taskboard/static/app.js, taskboard/tests/test_api.py
- Acceptance: The served page contains the documented title, form fields, task-board container, status/filter controls, and local static asset references; no backend-only behavior is duplicated in the template.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-rpb: taskboard/static/style.css
- Scope: Implement the SPEC visual layout for the board, form, task cards, status presentation, filters, and responsive behavior.
- Architecture: Follow architecture.md § static presentation; target the classes and IDs owned by index.html/app.js.
- Interfaces: Define selectors for the board shell, task form, task list/cards, status controls, and the documented status-specific visual states.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html, taskboard/tests/test_api.py
- Acceptance: The board is readable and usable with the documented controls; task cards and their status states are visually distinct; the stylesheet is loaded from the app's static route and does not require external assets.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-sxk: taskboard/static/app.js
- Scope: Implement browser-side loading, rendering, creation, status editing, deletion, filtering, and form interaction required by the SPEC.
- Architecture: Follow architecture.md § client behavior and the API paths/shapes in the SPEC HTTP table; use the DOM hooks from index.html.
- Interfaces: Call the documented task API routes, render the returned task fields, submit the documented create/update/delete actions, and maintain the selected filter/status view.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Initial load displays API tasks; submitting the form creates and displays a task; the documented status control updates a task; delete removes it; filtering shows only the selected status; empty/error states follow the SPEC behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-j3i: taskboard/tests/conftest.py
- Scope: Provide the isolated pytest client fixture and per-test database configuration described by architecture.md.
- Architecture: Follow architecture.md § test harness; isolate SQLite under pytest's temporary directory and construct the application through its public factory.
- Interfaces: Export the pytest `client` fixture, set `TASKBOARD_DB_PATH` for each test, reload `taskboard.main`, and yield a FastAPI TestClient.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Each test receives an isolated client/database, the fixture works with the public `create_app` contract, and tests do not depend on repository or developer machine state.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-c2c: taskboard/tests/test_api.py
- Scope: Implement the phase API acceptance suite from SPEC and architecture.md using the shared client fixture.
- Architecture: Follow architecture.md § test coverage and the SPEC HTTP table; test externally observable behavior rather than private implementation details.
- Interfaces: Exercise the page route and every phase task API operation, including documented request payloads, response fields, persistence, status changes, deletion, and specified validation responses.
- Depends on: taskboard/main.py, taskboard/tests/conftest.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css
- Consumed by: <none>
- Acceptance: Tests prove the page is served, task creation returns the documented result, list returns created tasks, update changes the documented status/data, delete removes the task, data persists for the configured database, and SPEC-defined invalid requests return their required status/body.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase verification

Run exactly `cd taskboard && python -m pytest -q tests`. The phase is complete only when the full suite passes and the six required paths exist with the interfaces and behavior above. Do not implement later-phase files or features not specified by SPEC.md.
