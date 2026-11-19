# Implementation plan

## Active phase

Phase `phase-1-app` delivers the runnable foundation on top of the completed
phase-1-core package. Implement exactly these six required paths. This phase
owns the application factory, health and project HTTP API, real initial HTML
shell/static serving, isolated API fixtures, and API tests. Do not add task
routes or Kanban/filter behavior; those belong to later phases. The phase gate
is `cd taskboard && python -m pytest -q tests`.

## Bead map

### te-hit: taskboard/main.py
- Scope: Implement the FastAPI application factory and module-level app, initialize the selected SQLite database, mount `taskboard/static`, render the real index template, and register the phase-1 health and project routes.
- Architecture: `architecture.md` module ownership and `### phase-1-app`; `create_app(db_path: str | None = None) -> FastAPI`, app state database-path wiring, and the exact HTTP route table in SPEC.md.
- Interfaces: export `create_app(db_path: str | None = None) -> FastAPI` and module-level `app`; provide GET `/api/health` with `{"status":"ok"}`, GET `/api/projects` with ascending project JSON, POST `/api/projects` with 201 and project JSON, DELETE `/api/projects/{project_id}` with 204 empty body, GET `/` as HTML, and static asset delivery.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py, the documented uvicorn command
- Acceptance: explicit `db_path` wins over nonempty `TASKBOARD_DB_PATH`, otherwise the documented default is used; schema initialization occurs without a mutable global connection; health JSON is exact; project create trims valid names and returns 201; list preserves repository ID order; missing project deletion returns `{"error": ...}` with 404; successful deletion has no body; GET `/` is real HTML and static files are served.
- Verify: cd taskboard && python -m pytest -q tests

### te-2qb: taskboard/templates/index.html
- Scope: Provide the real initial TaskBoard HTML shell required by the phase-1 root route, including project form, task-form shell, Kanban headings, and stable hooks for later client behavior.
- Architecture: `architecture.md` template ownership and `### phase-1-app`; semantic forms, selector/state regions, three columns, and static references are the canonical contract.
- Interfaces: reference `/static/app.js` and `/static/style.css`; contain heading `TaskBoard`, project creation input and `Add project` button, task form hooks, project selector/list, visible `To Do`, `Doing`, and `Done` headings, and empty/error regions for the client.
- Depends on: taskboard/static/app.js, taskboard/static/style.css
- Consumed by: taskboard/main.py and browser GET `/`
- Acceptance: rendered HTML is not a placeholder; it contains the exact heading, project form, task form, all three column headings, accessible labels, and both static asset references; it embeds no database calls or fabricated user tasks.
- Verify: cd taskboard && python -m pytest -q tests

### te-ms3: taskboard/static/app.js
- Scope: Supply the non-placeholder vanilla JavaScript entry asset and phase-compatible DOM initialization hooks while preserving the later API/UI ownership boundary.
- Architecture: `architecture.md` static app ownership; browser behavior belongs here and user content must be rendered safely with `textContent`.
- Interfaces: load as `/static/app.js`, locate the template's project/task/filter/error hooks, and define the client-side surface needed for the real page without introducing routes outside SPEC.md.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html and GET `/static/app.js`
- Acceptance: file is nonempty real JavaScript, references the canonical DOM contract, does not use a second frontend build or raw user-content injection, and is returned successfully as a nonempty static response. Full task CRUD, moving, and filters remain later-phase behavior.
- Verify: cd taskboard && python -m pytest -q tests

### te-1vt: taskboard/static/style.css
- Scope: Provide the real initial responsive presentation for the TaskBoard shell, forms, project area, three columns, empty/error states, and controls.
- Architecture: `architecture.md` stylesheet ownership; plain CSS only, with narrow-window usability and no application logic.
- Interfaces: style the selectors/classes supplied by taskboard/templates/index.html, including the three-column layout and visible error/empty regions.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html and GET `/static/style.css`
- Acceptance: nonempty CSS gives the page readable spacing, form/button presentation, visible Kanban columns, usable narrow layout, and distinct error/empty states; it introduces no framework, animation, alternate markup, or API behavior.
- Verify: cd taskboard && python -m pytest -q tests

### te-xsd: taskboard/tests/conftest.py
- Scope: Provide the validated pytest fixture that isolates every API test in a temporary SQLite database.
- Architecture: `architecture.md` fixture ownership and SPEC testing contract; use `tmp_path`, `TASKBOARD_DB_PATH`, module reload, `create_app`, and FastAPI TestClient.
- Interfaces: export a pytest `client` fixture yielding a usable TestClient for an app initialized against `tmp_path / "taskboard.sqlite3"`.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: each test gets a fresh database path; the environment is set before app creation; the reloaded app uses that path; the client is yielded inside a context manager and closed afterward; the fixture never touches runtime `taskboard.db`.
- Verify: cd taskboard && python -m pytest -q tests

### te-oj5: taskboard/tests/test_api.py
- Scope: Write substantive phase-1 HTTP tests against the fixture, covering the exact health/project/root/static contract while retaining repository tests from phase-1-core.
- Architecture: `architecture.md` API-test ownership, HTTP integration contract, and `### phase-1-app`; assertions must match SPEC.md status codes and JSON shapes.
- Interfaces: consume the `client` fixture and assert responses from GET `/api/health`, GET/POST `/api/projects`, DELETE `/api/projects/{project_id}`, GET `/`, `/static/app.js`, and `/static/style.css`.
- Depends on: taskboard/tests/conftest.py, taskboard/main.py
- Consumed by: phase-1-app verification
- Acceptance: assert exact health JSON; prove project create/list/delete round trip, trimmed names, ascending IDs, 201/204 statuses and empty delete body; assert invalid/empty project names return application-level 400 errors; assert missing project deletion returns 404 with an `error` field; assert root HTML contains TaskBoard, both forms, and all three headings; assert both static responses are 200 and nonempty.
- Verify: cd taskboard && python -m pytest -q tests

## Verification and boundaries

The polecat must run exactly `cd taskboard && python -m pytest -q tests` after
implementation. The active phase must preserve all phase-1-core repository
tests and must not create later-phase files such as
`taskboard/tests/test_ui_content.py` or Playwright manifests. Acceptance is
behavioral: status-only or placeholder-only tests are insufficient.

## Future considerations

Task CRUD, repository task operations, Kanban movement/edit/delete behavior,
filters, and Playwright scenarios are explicitly deferred to their later
delivery phases and are not acceptance criteria for this plan.
