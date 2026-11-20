# Implementation plan

## Active delivery scope

This plan covers only delivery subphase `phase-1-core` and its eight required
files. Preserve the validated contents supplied for the metadata, README,
ignore rules, database, models, repository, and repository-test files. Do not
create or modify later-phase `main.py`, templates, static assets, API tests,
or Playwright files. The exact phase gate is:

`cd taskboard && python -m pytest -q taskboard/tests/test_repository.py`

The implementation follows SPEC.md and architecture.md: Python 3.11+, built-in
sqlite3, explicit UTC timestamps, isolated temporary test databases,
parameterized write SQL, idempotent DDL, foreign keys, and a 5000 ms busy
timeout.

## Bead map

### te-9lw: taskboard/pyproject.toml
- Scope: Preserve the validated setuptools metadata, Python requirement,
  runtime dependencies (fastapi, uvicorn, jinja2, httpx), pytest extra, and
  module/package configuration.
- Architecture: architecture.md Planned file layout and packaging contract.
- Interfaces: installable `taskboard` project and test extra; later phases
  import `taskboard.main` and the database/model/repository modules.
- Depends on: <none>
- Consumed by: taskboard/README.md, taskboard/tests/test_repository.py, later app phases.
- Acceptance:
  - Editable installation from `taskboard/` succeeds with the documented
    `.[test]` extra and exposes the declared project modules.
  - Metadata does not add a frontend build, ORM, Docker, or undeclared service.
- Verify: `cd taskboard && python -m pytest -q taskboard/tests/test_repository.py`

### te-9f0: taskboard/README.md
- Scope: Preserve the validated installation, server, database-path,
  repository-test, browser-test, and layout documentation.
- Architecture: architecture.md README/documentation contract.
- Interfaces: documents `TASKBOARD_DB_PATH`, `taskboard.db`, the canonical
  uvicorn command, and the phase verification command.
- Depends on: taskboard/pyproject.toml
- Consumed by: developers and later release verification.
- Acceptance:
  - Commands and paths are relative to the `taskboard/` project as specified.
  - Documentation states the default database and explicit environment override,
    and does not promise features outside SPEC.
- Verify: `cd taskboard && python -m pytest -q taskboard/tests/test_repository.py`

### te-flq: taskboard/.gitignore
- Scope: Preserve ignore rules for Python caches, virtual environments,
  SQLite/runtime databases, build output, node_modules, coverage, and
  Playwright reports.
- Architecture: architecture.md repository hygiene contract.
- Interfaces: prevents generated runtime/test artifacts from being tracked.
- Depends on: <none>
- Consumed by: all taskboard implementation and test files.
- Acceptance:
  - `*.db`, SQLite variants, caches, `.venv`, build artifacts, node_modules,
    coverage, and Playwright results are ignored.
  - Source files, tests, and documented project files remain trackable.
- Verify: `test -s taskboard/.gitignore`

### te-fu0: taskboard/__init__.py
- Scope: Provide the importable package marker and only package metadata
  required by architecture; no eager app construction or database I/O.
- Architecture: architecture.md module/bead ownership for `__init__.py`.
- Interfaces: importable `taskboard` package; package metadata only.
- Depends on: taskboard/pyproject.toml
- Consumed by: taskboard/db.py, taskboard/models.py, taskboard/repository.py,
  and later `taskboard.main`.
- Acceptance:
  - `import taskboard` succeeds from the repository context.
  - Import has no filesystem database side effect and does not duplicate app
    construction.
- Verify: `cd taskboard && python -m pytest -q taskboard/tests/test_repository.py`

### te-qnn: taskboard/db.py
- Scope: Implement `connect(db_path: str) -> sqlite3.Connection` and
  `init_schema(db_path: str) -> None`, path handling for explicit callers,
  connection configuration, and idempotent projects/tasks DDL.
- Architecture: architecture.md module ownership and SPEC data model.
- Interfaces: exported `connect(db_path: str) -> sqlite3.Connection` and
  `init_schema(db_path: str) -> None`; repository.py consumes connections.
- Depends on: taskboard/__init__.py
- Consumed by: taskboard/repository.py and later `taskboard.main`.
- Acceptance:
  - New and repeated initialization succeeds and creates `projects` and
    `tasks` with required columns, defaults, primary keys, and timestamps.
  - `tasks.project_id` references projects with `ON DELETE CASCADE`, an index
    exists, and foreign keys are enabled on every connection.
  - Connections configure `busy_timeout=5000`; parent directories are created
    for explicitly selected paths; schema setup is not a migration system.
  - Status/priority constraints match exactly `todo|doing|done` and
    `low|medium|high`, and timestamps use explicit UTC offsets.
- Verify: `cd taskboard && python -m pytest -q taskboard/tests/test_repository.py`

### te-sxq: taskboard/models.py
- Scope: Implement validated status/priority constants, pure field validation,
  and row-to-JSON mapping helpers.
- Architecture: architecture.md module ownership:
  `VALID_STATUSES`, `VALID_PRIORITIES`, `validate_project_name`,
  `validate_task_fields`, `project_from_row`, and `task_from_row`.
- Interfaces: `VALID_STATUSES`; `VALID_PRIORITIES`;
  `validate_project_name(name: str) -> str`;
  `validate_task_fields(...)`; `project_from_row(row) -> dict`;
  `task_from_row(row) -> dict`.
- Depends on: taskboard/__init__.py
- Consumed by: taskboard/repository.py and later API serialization.
- Acceptance:
  - Project names and task titles trim surrounding whitespace and reject empty
    or over-limit Unicode values (80 and 120 respectively).
  - Descriptions remain verbatim strings up to 1000 code points; creation-only
    missing/null description behavior is `""`; enum validation adds no states.
  - Mapping returns exactly the SPEC project/task JSON fields and preserves
    database values and UTC timestamps without SQL or FastAPI dependencies.
- Verify: `cd taskboard && python -m pytest -q taskboard/tests/test_repository.py`

### te-apc: taskboard/repository.py
- Scope: Implement `ProjectRepository`, `TaskRepository`, and the module
  persistence functions using per-operation connections, explicit
  transactions, model validation/mapping, deterministic ID ordering, and
  parameterized SQL.
- Architecture: architecture.md repository ownership and file dependencies.
- Interfaces: `ProjectRepository`; `TaskRepository`;
  `list_projects() -> list[dict]`; `create_project(name: str) -> dict`;
  `delete_project(project_id: int) -> bool`;
  `list_tasks(project_id: int, status: str | None = None, priority: str | None = None) -> list[dict]`;
  `create_task(...) -> dict`; `update_task(task_id: int, changes: dict) -> dict | None`;
  `delete_task(task_id: int) -> bool`.
- Depends on: taskboard/db.py, taskboard/models.py
- Consumed by: taskboard/tests/test_repository.py and later `taskboard.main`.
- Acceptance:
  - Project creation/listing is ascending ID; task creation supplies todo and
    medium defaults, preserves UTC timestamps, and lists ascending ID.
  - Status, priority, and combined filters use AND semantics; partial updates
    preserve omitted fields and update `updated_at`.
  - Missing resources return the architecture-defined empty/false/None
    results; project deletion cascades tasks; task ownership is enforced.
  - Every caller value uses SQL parameters, writes commit explicitly, and
    connections close after each operation.
- Verify: `cd taskboard && python -m pytest -q taskboard/tests/test_repository.py`

### te-7yg: taskboard/tests/test_repository.py
- Scope: Preserve the validated pytest suite as executable proof of the
  repository contract, using one temporary SQLite path per test.
- Architecture: architecture.md Unit tests and SPEC §7 repository tests.
- Interfaces: pytest fixtures/helpers and assertions for db, models, and
  repository behavior; no HTTP or browser assertions.
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py
- Consumed by: phase-1-core test review and QA gate.
- Acceptance:
  - Tests prove empty fresh databases and idempotent schema initialization,
    ascending project IDs, task defaults, valid UTC timestamps, status filter,
    priority filter, combined filters, and empty results.
  - Tests prove partial title/description/priority/status updates preserve
    omitted fields, and deleting a project cascades its tasks.
  - Tests use temporary databases, make substantive functional assertions,
    and do not touch runtime `taskboard.db` or require a running server.
- Verify: `cd taskboard && python -m pytest -q taskboard/tests/test_repository.py`

## Sequencing and YAGNI

Implement packaging and the package marker first, then db.py and models.py,
then repository.py, and finally execute the repository tests. Do not add API
routes, UI behavior, browser tooling, migrations, authentication, or other
out-of-scope features in this phase. Later phases may consume these exports
but must not be pulled into this delivery.

## Verification

Before phase completion, the polecat/test reviewer runs exactly
`cd taskboard && python -m pytest -q taskboard/tests/test_repository.py`.
Dependency installation belongs to setup, not the verification command.
