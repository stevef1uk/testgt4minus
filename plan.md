# Implementation plan

Active delivery phase: `phase-1-app` (Foundation and projects: runnable app). The completed core phase supplies the database, models, and repository; this phase must use those exports rather than introduce a second persistence model. Work only on the six active-phase paths.

## Verification contract

Run from the project directory after implementation:
`cd taskboard && python -m pytest -q tests`
The tests must exercise the real FastAPI application with an isolated database, and must prove the SPEC-defined project CRUD behavior, HTML/static responses, JSON shapes, status codes, and invalid-request behavior. Do not add later-phase task/Kanban/filter or browser-test scope.

## Bead map

### te-2qb: taskboard/templates/index.html
- Scope: Provide the semantic application page and the elements named by the SPEC for the project view. Keep this file presentational: no database calls, application logic, or invented API contract.
- Architecture: `architecture.md` template ownership; passive semantic markup consumed by `taskboard/main.py`, with the project-page structure and static asset references required by SPEC.
- Interfaces: HTML document and the SPEC-required page elements; references the application JavaScript and stylesheet at the paths served by the app.
- Depends on: `<none>` (the template is passive and must not depend on `taskboard/main.py`).
- Consumed by: `taskboard/main.py` (HTML rendering/serving); `taskboard/tests/test_api.py` (page response assertions).
- Acceptance: GET `/` returns this template through the application with a successful HTML response; required project controls, headings, containers, and asset references are present; markup does not embed repository/database behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Implement the SPEC-required layout and readable styling for the page, forms, project list, and feedback states without adding behavior.
- Architecture: `architecture.md` static stylesheet ownership; served as a static asset referenced by the template.
- Interfaces: stylesheet at `/static/style.css`, with selectors/classes matching the elements in `taskboard/templates/index.html`.
- Depends on: `<none>` (standalone static asset).
- Consumed by: `taskboard/templates/index.html`, `taskboard/main.py`, and API/page tests that verify static delivery.
- Acceptance: the stylesheet is served from the SPEC-defined static URL with a successful CSS response; it contains rules for the required page/project/form presentation and does not implement persistence or JavaScript behavior.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-ms3: taskboard/static/app.js
- Scope: Implement the browser-side project interactions specified for this phase, using the exact API paths, methods, request fields, and response fields from SPEC; update the template-owned elements.
- Architecture: `architecture.md` static JavaScript ownership; browser client for the phase-1 project API, not a second data store.
- Interfaces: JavaScript asset at `/static/app.js`; calls only the SPEC project endpoints and renders their returned project data into the page.
- Depends on: `<none>` (the script is a passive static dependency of the rendered page).
- Consumed by: `taskboard/templates/index.html`, `taskboard/main.py`, and later UI tests.
- Acceptance: the script loads successfully; it can list projects, submit the SPEC project creation form, and remove a project using the exact documented request/response contract; success and invalid-request feedback are reflected in the page without inventing task features.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-hit: taskboard/main.py
- Scope: Build the runnable FastAPI application, render the template, mount/serve static assets, and expose the SPEC-defined project endpoints using the completed core repository.
- Architecture: `architecture.md` application ownership; depends on core `db.py`, `models.py`, and `repository.py`, and serves the passive template and static assets. Preserve the application factory used by tests.
- Interfaces: exported application factory `create_app(...)` as specified by architecture/tests; HTML root route, static mounting, and the exact SPEC HTTP routes for project listing, creation, and deletion, including their documented JSON keys and status codes.
- Depends on: `taskboard/templates/index.html`, `taskboard/static/app.js`, `taskboard/static/style.css`, and completed-phase `taskboard/db.py`, `taskboard/models.py`, `taskboard/repository.py`.
- Consumed by: `taskboard/tests/conftest.py`, `taskboard/tests/test_api.py`, and the eventual runnable entrypoint/UI.
- Acceptance: the factory initializes against the test-selected database; GET `/` renders the page; static files are reachable; project create/list/delete operations delegate to the core repository and persist across requests; valid responses match SPEC JSON and status codes; malformed or invalid project requests produce the SPEC-defined error response; no duplicate in-memory model or unrelated endpoints is introduced.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Supply the isolated pytest client fixture for the real application and a temporary database per test.
- Architecture: `architecture.md` test-fixture ownership; reload/configure the application so tests do not use a developer database.
- Interfaces: pytest fixture `client` yielding a `TestClient` for the application factory.
- Depends on: `taskboard/main.py`.
- Consumed by: `taskboard/tests/test_api.py`.
- Acceptance: each test receives a functioning client backed by a fresh temporary SQLite path; the fixture exercises `create_app` and does not replace repository behavior with mocks.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Add focused API/page tests that lock the phase contract and catch route, payload, status, persistence, template, and static-asset drift.
- Architecture: `architecture.md` API-test ownership; use the shared `client` fixture and the real application.
- Interfaces: pytest tests for the SPEC HTTP table and rendered/static responses; exact endpoint names and JSON fields must come from SPEC rather than guessed aliases.
- Depends on: `taskboard/tests/conftest.py`, `taskboard/main.py`, and the completed core repository.
- Consumed by: phase verification and QA.
- Acceptance: tests prove the root HTML page and both static assets; prove empty/list project behavior, valid creation, persistence/listing, deletion, and the SPEC-defined invalid request/status behavior; assert exact JSON keys and status codes and fail on route drift. Tests remain limited to phase-1 project functionality.
- Verify: `cd taskboard && python -m pytest -q tests`

## Dependency direction

Static/template files are passive providers. `taskboard/main.py` consumes them; it is incorrect for the template or assets to depend on `main.py`. The fixture depends on the application, and API tests depend on the fixture/application. Core files are completed-phase prerequisites and are not re-beaded here.

## Definition of done

All six active-phase beads are implemented without stubs or unrelated features, the app uses the completed core repository, and `cd taskboard && python -m pytest -q tests` passes.
