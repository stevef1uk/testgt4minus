# Phase 2 implementation plan: Tasks and Kanban UI

This phase delivers the browser UI and phase-specific tests. Implement only the seven paths below, using the completed core application and repository/API contracts in SPEC.md and architecture.md. The required verification command for every bead is `cd taskboard && python -m pytest -q tests`.

## Bead map

### : taskboard/tests/test_ui_content.py
- Scope: Maintain focused content-level UI contract tests for the page shell and JavaScript.
- Architecture: Architecture § Phase 2 UI content tests; inspect template and static bundle without a browser.
- Interfaces / Depends on / Consumed by: Depends on taskboard/templates/index.html and taskboard/static/app.js; consumed by the phase-2 verification suite.
- Acceptance: Assert index.html contains project-form-region, project-form, project-list, project-filter, empty-state, loading-state, and error-state. Assert it loads /static/app.js and /static/style.css. Assert app.js uses textContent and replaceChildren and references /api/projects.
- Verify: cd taskboard && python -m pytest -q tests

### : taskboard/templates/index.html
- Scope: Implement the semantic taskboard shell, project creation form, filter controls, project list container, and loading/empty/error regions.
- Architecture: Architecture § Phase 2 Templates and SPEC UI requirements; preserve exact IDs and static asset paths used by content tests.
- Interfaces / Depends on / Consumed by: Depends on the phase-1 template-serving contract; consumed by taskboard/static/app.js, taskboard/static/style.css, and test_ui_content.py.
- Acceptance: Provide a usable project form with name input and submit control; provide all required regions with exact IDs. Load /static/app.js and /static/style.css. Keep controls keyboard-accessible and labels associated with inputs. Never render user-controlled values as executable markup.
- Verify: cd taskboard && python -m pytest -q tests

### : taskboard/static/app.js
- Scope: Wire the page to the projects API and update list, filter, form, and status regions without unsafe HTML interpolation.
- Architecture: Architecture § Phase 2 client behavior; use completed phase-1 HTTP routes and JSON shapes.
- Interfaces / Depends on / Consumed by: Depends on template DOM IDs and the phase-1 /api/projects contract; consumed by the UI and test_ui_content.py.
- Acceptance: Fetch and display projects from /api/projects; submit the form through the projects API and refresh the list; filter displayed projects; show loading, empty, and error states. Use textContent and replaceChildren, not innerHTML, for user-controlled data.
- Verify: cd taskboard && python -m pytest -q tests

### : taskboard/static/style.css
- Scope: Style the taskboard shell, form, filter, project cards/list, and status regions responsively.
- Architecture: Architecture § Phase 2 static styling; selectors apply to semantic regions from index.html.
- Interfaces / Depends on / Consumed by: Depends on template class and ID hooks; consumed by the rendered browser UI.
- Acceptance: Make form and list distinct, make loading/empty/error states readable, provide narrow and wide layouts, and preserve visible focus states and adequate contrast. Add no functionality outside SPEC.
- Verify: cd taskboard && python -m pytest -q tests

### : taskboard/tests/conftest.py
- Scope: Provide the isolated FastAPI TestClient fixture for phase-2 API and repository tests.
- Architecture: Architecture § Phase 2 test fixtures; each test receives a temporary SQLite database through TASKBOARD_DB_PATH.
- Interfaces / Depends on / Consumed by: Depends on taskboard.main.create_app and the phase-1 application; consumed by test_repository.py and test_api.py.
- Acceptance: Create a unique temporary database path, set TASKBOARD_DB_PATH, reload taskboard.main, call create_app with that path, yield a TestClient, and close it after each test. Tests must not share persistent application state.
- Verify: cd taskboard && python -m pytest -q tests

### : taskboard/tests/test_repository.py
- Scope: Exercise repository behavior needed by the UI against isolated temporary storage.
- Architecture: Architecture § Phase 1 repository contract as consumed by Phase 2; cover creation, listing, filtering/query behavior, and persistence.
- Interfaces / Depends on / Consumed by: Depends on the completed repository module and conftest.py; consumed by the phase verification suite and later UI/API phases.
- Acceptance: Prove schema initialization, project creation with required fields, specified listing order, retrieval/filtering per SPEC, and persistence across repository connections while tests remain isolated.
- Verify: cd taskboard && python -m pytest -q tests

### : taskboard/tests/test_api.py
- Scope: Verify the HTTP contract consumed by app.js for project creation and retrieval.
- Architecture: Architecture § Phase 1 API contract and § Phase 2 client integration; use the isolated client fixture.
- Interfaces / Depends on / Consumed by: Depends on conftest.py, taskboard.main, and phase-1 repository/API implementation; consumed by the browser client and full test suite.
- Acceptance: Test GET /api/projects response and JSON shape, successful POST and subsequent GET visibility, required validation failures, documented status codes, and error payloads. Ensure data does not leak between cases.
- Verify: cd taskboard && python -m pytest -q tests

## Phase acceptance

Run `cd taskboard && python -m pytest -q tests`. Completion requires core and phase-2 tests to pass, exact DOM hooks and static paths to exist, and project data to be rendered safely through textContent/replaceChildren.
