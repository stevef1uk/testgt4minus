# Phase 1 app implementation plan

This plan covers only the active `phase-1-app` delivery. The completed core phase
provides `taskboard.db`, `taskboard.models`, and `taskboard.repository`; those
modules are consumed as implemented and are not re-planned here. The application
must use FastAPI as specified by SPEC section 6, not Flask. The dependency graph
is acyclic: the app consumes the template and static assets, while those assets
do not depend on the app.

## Verification contract

From the rig root, the polecat must run exactly:
`cd taskboard && python -m pytest -q tests`
The suite must exercise the real FastAPI application, its repository-backed
project behavior, HTML response, and mounted static resources. Do not substitute
a Flask test client or a mock-only application.

## Bead map

### te-hit: taskboard/main.py
- Scope: Implement the runnable FastAPI application and `create_app(...) -> FastAPI`
  described in SPEC section 6. Wire the existing db/models/repository modules,
  mount the static directory, render `templates/index.html` for the browser
  entry point, and expose the SPEC project API routes with the required JSON
  status codes and response shapes. Keep the module-level `app` usable by
  uvicorn as `taskboard.main:app`.
- Architecture: `taskboard/main.py` owns app construction, HTTP routing,
  template/static integration, and the phase-1 project endpoints. It depends on
  `taskboard/db.py`, `taskboard/models.py`, and `taskboard/repository.py`, and
  consumes (but does not own) `taskboard/templates/index.html`,
  `taskboard/static/app.js`, and `taskboard/static/style.css`.
- Interfaces: export `create_app(...) -> FastAPI` and the module-level
  `app`; implement the exact HTTP paths, methods, request fields, response
  fields, and status behavior in SPEC section 6.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
  (completed phase); the template and static asset beads below are consumed
  resources, not providers of app symbols.
- Consumed by: te-xsd (`taskboard/tests/conftest.py`), te-oj5
  (`taskboard/tests/test_api.py`), and the phase-2 UI test.
- Acceptance: `create_app` returns a FastAPI instance; the root page returns
  the rendered index document; `/static/...` serves both named assets; project
  list/create behavior uses the repository and persists data; invalid project
  input produces the SPEC-required validation response; API responses match the
  SPEC JSON contract and status codes; module import exposes `app` for uvicorn.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-2qb: taskboard/templates/index.html
- Scope: Provide the browser entry document required by the SPEC, with the
  project-focused phase-1 shell and references to the mounted `/static` assets.
- Architecture: Static Jinja/HTML template consumed by `taskboard/main.py`;
  it has no dependency on `main.py` and must not import or execute server code.
- Interfaces: HTML document served by the root route; include the exact
  structural hooks and asset references required by SPEC section 6 and the
  architecture UI ownership notes.
- Depends on: <none>
- Consumed by: te-hit (`taskboard/main.py`) and later UI tests.
- Acceptance: the file is a complete HTML document; its script and stylesheet
  references resolve to the app's `/static` mount; it contains the project
  page container and the IDs/classes required by the SPEC without adding
  unrequested task/kanban functionality.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-ms3: taskboard/static/app.js
- Scope: Implement the phase-1 browser script needed by the SPEC project UI,
  using the specified API and updating the project view through the template's
  documented hooks.
- Architecture: Browser asset served by FastAPI's static mount; it is not a
  Python module and has no dependency on `taskboard/main.py`.
- Interfaces: issue the exact project API requests and use the exact DOM
  hooks/data behavior required by SPEC section 6; preserve the later-phase
  extension points without implementing future task/filter features.
- Depends on: te-2qb (`taskboard/templates/index.html`) for DOM hooks.
- Consumed by: te-hit (static serving) and later browser/UI tests.
- Acceptance: the script is referenced by the template, calls the SPEC project
  endpoint with the required method and payload, renders returned projects,
  and handles the specified create/list interaction; it contains no Flask
  URLs or invented API paths.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-1vt: taskboard/static/style.css
- Scope: Supply the phase-1 page styling and layout hooks required by the SPEC
  for the project shell.
- Architecture: Browser stylesheet served as a static resource; independent
  of Python application code.
- Interfaces: selectors correspond to the template's documented project
  container, form, and list hooks.
- Depends on: te-2qb (`taskboard/templates/index.html`) for markup hooks.
- Consumed by: te-hit (static serving) and later UI tests.
- Acceptance: the stylesheet is referenced from the rendered HTML, provides
  visible layout for the project form/list and required state classes, and
  does not claim or implement later Kanban/filter requirements.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-xsd: taskboard/tests/conftest.py
- Scope: Configure pytest fixtures for the real phase-1 FastAPI app and an
  isolated database/repository state.
- Architecture: Test support imports `taskboard.main` and supplies the client
  dependency used by `test_api.py`; it must respect the existing db contract.
- Interfaces: provide the fixtures expected by the API tests, including a
  test client against `create_app`/`app`, with no Flask client.
- Depends on: te-hit (`taskboard/main.py`) and completed core db/repository
  modules.
- Consumed by: te-oj5 (`taskboard/tests/test_api.py`).
- Acceptance: every API test can run against an isolated, repeatable
  FastAPI application; fixture setup does not use the production database or
  require a running server; the client can request the root and SPEC API
  routes and observe real status/JSON responses.
- Verify: `cd taskboard && python -m pytest -q tests`

### te-oj5: taskboard/tests/test_api.py
- Scope: Add the phase-1 API and app integration tests prescribed by SPEC.
- Architecture: Tests use fixtures from `taskboard/tests/conftest.py` and the
  real FastAPI app; they cover the entry page, static integration, and project
  HTTP contract, not a Flask app.
- Interfaces: test the exact methods and paths from SPEC section 6, including
  request/response schemas, persistence-visible list/create behavior, and
  validation/status outcomes.
- Depends on: te-xsd (`taskboard/tests/conftest.py`) and te-hit
  (`taskboard/main.py`).
- Consumed by: phase-1 QA verification.
- Acceptance: assertions prove the root returns HTML with the expected asset
  links; static assets are reachable; an initially empty project list is
  returned; creating a valid project returns the SPEC-required success status
  and fields; a subsequent list observes it; invalid/missing required input
  returns the SPEC-required error status and shape; tests use the exact
  `cd taskboard && python -m pytest -q tests` command.
- Verify: `cd taskboard && python -m pytest -q tests`

## Future considerations

Tasks, Kanban interactions, filtering, browser Playwright coverage, and release
checks belong to later phases and are intentionally excluded from this bead map.
