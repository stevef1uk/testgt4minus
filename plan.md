# Implementation plan

## Active phase: phase-1-core

This plan covers exactly the eight required files for the Foundation core
subphase. Later application, API, UI, and browser files are excluded. The
phase gate is `cd taskboard && python -m pytest -q tests/test_repository.py`.
Tests must use explicit temporary SQLite paths and prove domain behavior.

## Bead map

### tm-w78: taskboard/pyproject.toml
- Scope: Define setuptools metadata, Python 3.11+ requirement, runtime dependencies, pytest extra, package mapping, and package data.
- Architecture: Packaging and project-layout contract in architecture.md and SPEC.md.
- Interfaces / Depends on / Consumed by: Provides editable-install metadata consumed by project tests and the later server; depends on <none>.
- Acceptance: Metadata names the project, declares fastapi, uvicorn, jinja2, httpx and pytest appropriately, and supports the canonical taskboard package without a second project.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-bvb: taskboard/README.md
- Scope: Document installation, TASKBOARD_DB_PATH, server startup, repository/full-test commands, layout, and canonical browser commands.
- Architecture: README ownership and SPEC installation/testing contract.
- Interfaces / Depends on / Consumed by: Documents project interfaces; depends on taskboard/pyproject.toml; consumed by maintainers and later review.
- Acceptance: Commands use canonical taskboard paths, describe SQLite and isolated tests, and do not promise out-of-scope behavior.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-1d6: taskboard/.gitignore
- Scope: Ignore caches, virtual environments, local databases, build output, node_modules, coverage, and Playwright reports.
- Architecture: Generated-artifact and repository hygiene rules.
- Interfaces / Depends on / Consumed by: No runtime exports; depends on <none>; consumed by repository tooling.
- Acceptance: Documented generated artifacts are ignored while source, tests, templates, static files, and metadata remain trackable.
- Verify: `test -s taskboard/.gitignore`

### tm-1ns: taskboard/__init__.py
- Scope: Provide the importable taskboard package marker without side effects.
- Architecture: Package layout ownership in architecture.md.
- Interfaces / Depends on / Consumed by: Provides the taskboard namespace; depends on <none>; consumed by taskboard/db.py, taskboard/models.py, taskboard/repository.py, and later main.py.
- Acceptance: Import succeeds from the documented layout and does not open databases or register routes.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-tvv: taskboard/db.py
- Scope: Implement database path handling, SQLite connections, and idempotent schema DDL for projects and tasks.
- Architecture: Owns `connect(db_path: str) -> sqlite3.Connection` and `init_schema(db_path: str) -> None`; enables foreign keys and busy_timeout 5000.
- Interfaces / Depends on / Consumed by: Exports connect and init_schema; depends on taskboard/__init__.py; consumed by taskboard/repository.py and taskboard/tests/test_repository.py.
- Acceptance: Fresh and repeated initialization create the required tables, UTC timestamp defaults, project_id foreign key with ON DELETE CASCADE, and task project index; connections expose rows and enforce required pragmas.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-51g: taskboard/models.py
- Scope: Define VALID_STATUSES, VALID_PRIORITIES, pure validation helpers, and project/task row mappers.
- Architecture: Models own validation and mapping only, without SQLite or FastAPI dependencies.
- Interfaces / Depends on / Consumed by: Exports architecture-defined constants, validators, and mappers; depends on <none>; consumed by taskboard/repository.py and repository tests.
- Acceptance: Project names trim and allow 1–80 characters; titles trim and allow 1–120; descriptions preserve content through 1000 characters; creation null/missing descriptions become empty; invalid enums are rejected; mapped JSON has exact documented fields and UTC timestamps.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-edl: taskboard/repository.py
- Scope: Implement parameterized project/task persistence, explicit write transactions, ascending ID ordering, filters, partial updates, and deletion.
- Architecture: Owns ProjectRepository, TaskRepository, and architecture-defined CRUD/list methods; SQL access remains exclusively here.
- Interfaces / Depends on / Consumed by: Exports ProjectRepository and TaskRepository; depends on taskboard/db.py and taskboard/models.py; consumed by taskboard/tests/test_repository.py and later main.py.
- Acceptance: Project and task CRUD persists exact fields; task defaults are todo/medium; missing projects are rejected; status and priority filters combine with AND; omitted patch fields remain unchanged; all writes are parameterized; project deletion cascades child tasks.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-ns3: taskboard/tests/test_repository.py
- Scope: Write substantive pytest coverage for the database, models, and repository contract using a separate tmp_path database per test.
- Architecture: Repository test ownership in architecture.md; tests use public interfaces rather than duplicate SQL.
- Interfaces / Depends on / Consumed by: Consumes taskboard/db.py, taskboard/models.py, and taskboard/repository.py; depends on tm-tvv, tm-51g, and tm-edl; consumed by the phase gate.
- Acceptance: Tests assert empty lists and idempotent schema; ascending project IDs; name 80/81 boundaries; task defaults and timestamps; title 120/121 and description 1000/1001 boundaries; valid enum round trips and invalid enum rejection; composed AND filters; partial update preservation; and actual project-delete child cascade.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

## Dependency order and phase boundary

Implement package metadata and the package marker first, then db.py and models.py,
then repository.py, and finally the repository tests. Do not add main.py,
templates, static assets, conftest.py, API tests, or Playwright files to this
phase. The later app phase consumes the exports established here.

## Future considerations

HTTP routes, application error objects, static responses, Kanban behavior, and
browser scenarios belong to later delivery phases and are intentionally excluded.
