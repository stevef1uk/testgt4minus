# Implementation plan

## Active phase: phase-1-core

This plan covers exactly the eight required first-delivery paths for the
Foundation and projects core subphase. All paths are relative to the
taskboard layout root. The active verification command is:

`cd taskboard && python -m pytest -q tests/test_repository.py`

The implementation must retain the taskboard package layout from SPEC:
database DDL stays in db.py, validation and row mapping stay in models.py,
SQL persistence stays in repository.py, and the repository test contains
behavioral assertions rather than placeholder checks. API, HTML, JavaScript,
CSS, and Playwright work belongs to later phases.

## Bead map

### tm-w78: taskboard/pyproject.toml
- Scope: Provide setuptools metadata for the Python 3.11+ TaskBoard project and its FastAPI, Uvicorn, Jinja2, httpx, and pytest dependencies.
- Architecture: architecture.md planned file layout, packaging guidance, and phase-1-core ownership.
- Interfaces: Installation must support the documented taskboard application and test commands.
- Depends on: <none>
- Consumed by: taskboard/README.md and all Python source/tests.
- Acceptance: Metadata preserves the project name/version, Python requirement, runtime dependencies, pytest test extra, and declared modules/package data required by the validated project contract. It does not add a second project or frontend build.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-bvb: taskboard/README.md
- Scope: Document installation, database selection, server startup, repository tests, browser instructions, and the canonical taskboard layout.
- Architecture: architecture.md documentation and integration/testing sections; SPEC sections 3, 6, 7, and phase-1-core.
- Interfaces: Name `TASKBOARD_DB_PATH`, `python -m uvicorn taskboard.main:app --host 127.0.0.1 --port 8080`, and the canonical pytest command.
- Depends on: tm-w78
- Consumed by: developers and later review phases.
- Acceptance: Documentation accurately describes local-only Python/FastAPI/SQLite/Jinja2/vanilla-JS operation, default taskboard.db behavior, editable installation, and test commands without inventing features.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-1d6: taskboard/.gitignore
- Scope: Exclude Python caches, virtual environments, local SQLite files, packaging output, node_modules, browser reports/results, and coverage artifacts.
- Architecture: architecture.md repository hygiene and planned file layout; SPEC sections 2 and 3.
- Interfaces: Include patterns for `__pycache__/`, `.pytest_cache/`, `.venv/`, `*.db`, `*.sqlite*`, `node_modules/`, Playwright output, and coverage/build output.
- Depends on: <none>
- Consumed by: later taskboard source and test work.
- Acceptance: Generated runtime artifacts are ignored while all eight canonical source/documentation/test paths remain trackable.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-1ns: taskboard/__init__.py
- Scope: Keep taskboard importable as the project package with no application startup side effects.
- Architecture: architecture.md package layout and module ownership.
- Interfaces: `import taskboard` succeeds.
- Depends on: tm-w78
- Consumed by: taskboard/db.py, taskboard/models.py, taskboard/repository.py, and later taskboard/main.py.
- Acceptance: The package marker is present and performs no database I/O or server startup during import.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-tvv: taskboard/db.py
- Scope: Implement database_path, SQLite connection configuration, and idempotent schema initialization for projects and tasks.
- Architecture: architecture.md db.py ownership and data invariants; SPEC sections 4 and 8.
- Interfaces: Export `database_path()`, `connect(path=None)`, and `initialize(path=None)` as defined by the validated core contract.
- Depends on: tm-1ns
- Consumed by: tm-edl and tm-ns3.
- Acceptance: Use TASKBOARD_DB_PATH when nonempty and taskboard.db otherwise; connections return row-accessible results, enable foreign keys, and set busy_timeout 5000. Initialization is repeatable and creates required project/task columns, defaults, UTC timestamps, ON DELETE CASCADE, and the project/status/priority task index.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-51g: taskboard/models.py
- Scope: Implement shared validation constants, project/task validation, and row-to-JSON mapping helpers.
- Architecture: architecture.md models.py ownership and unit-test requirements; SPEC sections 4 and 5.
- Interfaces: Provide the architecture-defined status/priority constants and project/task validation and mapping helpers consumed by repository code.
- Depends on: tm-1ns
- Consumed by: tm-edl and later taskboard/main.py.
- Acceptance: Enforce trimmed project names of 1–80 characters, trimmed titles of 1–120, descriptions of at most 1000, valid `todo/doing/done` statuses and `low/medium/high` priorities, creation defaults, and exact project/task JSON fields.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-edl: taskboard/repository.py
- Scope: Implement parameterized project and task persistence operations, explicit write transactions, deterministic ordering, filters, partial updates, and deletion behavior.
- Architecture: architecture.md repository ownership and file dependencies; SPEC sections 4, 5, and repository tests.
- Interfaces: Provide the project and task repository operations defined by architecture.md, returning the exact SPEC project/task shapes and validation/not-found results.
- Depends on: tm-tvv, tm-51g
- Consumed by: tm-ns3 and later taskboard/main.py.
- Acceptance: Projects list by ascending ID; tasks support creation defaults, status/priority/both filters, partial updates preserving omitted fields, UTC timestamps, cascade-observable project deletion, and parameterized writes. No HTTP, HTML, or browser logic belongs here.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

### tm-ns3: taskboard/tests/test_repository.py
- Scope: Write isolated repository tests using a temporary database path per test and public core interfaces only.
- Architecture: architecture.md unit-test contract and phase-1-core requirements; SPEC repository tests 1–6.
- Interfaces: Exercise db, models, and repository behavior without importing HTTP/UI modules or touching the runtime database.
- Depends on: tm-tvv, tm-51g, tm-edl
- Consumed by: phase verification and later API work.
- Acceptance: Assert idempotent schema and empty lists; ascending project IDs; 80/81 project-name boundaries; 120/121 title boundaries; 1000/1001 description boundaries; unknown status/priority rejection; defaults and UTC timestamps; individual and combined filters; partial-update preservation; and project deletion cascading to tasks.
- Verify: `cd taskboard && python -m pytest -q tests/test_repository.py`

## Phase acceptance

Implement only these eight paths, preserve the taskboard module ownership
and dependency order, and pass the canonical repository test command. Do not
implement later-phase API, template, static, UI, or browser deliverables.
