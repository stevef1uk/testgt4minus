# Implementation plan

## Active phase

Phase `phase-1-app` implements the runnable app and project API using the
completed core package. The exact verification command is:
`cd taskboard && python -m pytest -q tests`. Only the six active required
paths are included; task/Kanban behavior beyond the basic page shell remains
for later phases.

## Bead map

### tm-lro: taskboard/main.py
- Scope: Implement `create_app(db_path: str | None = None) -> FastAPI`, module `app`, health/project routes, template rendering, and static mounting.
- Architecture: architecture.md module ownership and HTTP + entrypoint integration; SPEC sections 5–6.
- Interfaces: export `create_app` and `app`; provide GET `/api/health`, GET `/api/projects`, POST `/api/projects`, DELETE `/api/projects/{project_id}`, GET `/`, `/static/app.js`, and `/static/style.css`.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: taskboard/tests/conftest.py, taskboard/tests/test_api.py
- Acceptance: Resolve explicit db path then nonempty `TASKBOARD_DB_PATH` then fallback; initialize schema and store path in app state. Return exact health JSON, ordered projects, 201 creation with trimmed valid names, 400 error objects for invalid names, 204 empty deletes, and 404 missing deletes. Render real HTML and mount both canonical static assets.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-c2q: taskboard/templates/index.html
- Scope: Provide the real TaskBoard HTML shell with project controls, task-form shell, Kanban headings, and message regions.
- Architecture: architecture.md template ownership and planned layout; SPEC UI contract.
- Interfaces: provide semantic hooks for project form/list, task form, task list, error/empty regions, and visible `To Do`, `Doing`, `Done` columns; reference `/static/app.js` and `/static/style.css`.
- Depends on: taskboard/main.py
- Consumed by: taskboard/main.py, taskboard/static/app.js, taskboard/tests/test_api.py
- Acceptance: Include heading `TaskBoard`, project input and Add project control, project selector/list, task title/description/priority controls and Add task control, all three headings, accessible labels, stable script hooks, and visible empty/error regions. No inline database logic.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Implement phase-1 project loading, selection, creation/deletion, safe rendering, and visible API errors.
- Architecture: architecture.md browser behavior ownership; SPEC UI contract.
- Interfaces: use template DOM hooks; call `/api/projects` with GET/POST/DELETE; preserve hooks for later task behavior and use `textContent` for user data.
- Depends on: taskboard/templates/index.html, taskboard/main.py
- Consumed by: taskboard/templates/index.html and browser users
- Acceptance: Load and safely render projects, show no-project state, submit without navigation, refresh selection after creation, confirm before deletion, refresh after deletion, and display failures in the visible error area. Use vanilla JavaScript only.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Style the page, project controls, forms, columns, task-list shell, error/empty states, and narrow layouts.
- Architecture: architecture.md stylesheet ownership; SPEC UI requirements.
- Interfaces: define selectors consumed by index.html and app.js for page, forms, projects, columns, errors, and empty states.
- Depends on: taskboard/templates/index.html
- Consumed by: taskboard/templates/index.html and browser rendering
- Acceptance: Make heading, controls, forms, and three columns usable and readable on desktop and narrow windows; provide clear state styling and accessible focusable controls; contain presentation only.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-ff6: taskboard/tests/conftest.py
- Scope: Provide isolated pytest client setup backed by a temporary SQLite database and public app factory.
- Architecture: architecture.md testing ownership; SPEC testing contract.
- Interfaces: export pytest fixture `client`, yielding FastAPI TestClient with `tmp_path / "taskboard-test.db"`.
- Depends on: taskboard/main.py
- Consumed by: taskboard/tests/test_api.py
- Acceptance: Set per-test `TASKBOARD_DB_PATH`, reload/import main, call `create_app`, confirm initialization, assert exact health response, yield and close client. Never use runtime or in-memory databases.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rmz: taskboard/tests/test_api.py
- Scope: Write substantive API integration tests for the active health/project/page/static contract.
- Architecture: architecture.md API-test ownership and phase-1-app requirements; SPEC API and testing contracts.
- Interfaces: use `client` fixture and public HTTP requests, not private repository internals.
- Depends on: taskboard/main.py, taskboard/tests/conftest.py
- Consumed by: phase verification and QA
- Acceptance: Assert exact health JSON, empty list, project create/list ordering and trimming, invalid empty/overlong names with 400 error objects, missing delete 404, successful delete 204 with no body, and malformed integer 422. Assert `/` has real TaskBoard, forms, and all three headings; assert both static assets return 200 and nonempty content.
- Verify: `cd taskboard && python -m pytest -q tests`

## Integration contract

`main.py` imports the completed db/models/repository modules, initializes the
selected database, stores the path in app state, registers the exact routes,
and renders the template while mounting static files. The fixture obtains the
app only through `create_app`; API tests consume the fixture. The template
owns the DOM hooks consumed by app.js, and CSS owns presentation selectors.
No later-phase file is needed for this phase.

## Phase completion

All six active beads must be implemented and verified with the exact phase
pytest command. Acceptance must prove real project state changes and rendered
content, not merely imports or status-only responses.
