# TaskBoard

TaskBoard is a local-only Python 3.11+ Kanban application built with FastAPI,
SQLite, Jinja2, and vanilla JavaScript.

## Installation

Run these commands from the `taskboard/` project directory:

python -m pip install -e '.[test]'

For an isolated development environment:

python -m venv .venv
.venv/bin/python -m pip install -e '.[test]'

The application uses the built-in `sqlite3` module. By default, it stores data
in `taskboard.db`. Set `TASKBOARD_DB_PATH` to select another database file.

## Running the server

From the repository root, start the documented development server with:

python -m uvicorn taskboard.main:app --host 127.0.0.1 --port 8080

Open <http://127.0.0.1:8080/> in a browser. The application serves the
TaskBoard page at `/`, its API under `/api/`, and browser assets under
`/static/`.

## Running tests

The repository tests use a temporary SQLite database and do not modify the
runtime database:

cd taskboard
python -m pytest -q tests/test_repository.py

Run all available Python tests with:

python -m pytest -q tests

## Browser tests

Install the Playwright development dependency and run the canonical browser
suite from `taskboard/`:

npm install --ignore-scripts
npx playwright test --config playwright.config.ts playwright

The browser configuration targets the server at `127.0.0.1:8080`. Playwright
reports and test results are excluded from version control.

## Project layout

- `pyproject.toml` — setuptools metadata and runtime/test dependencies.
- `db.py` — SQLite connection configuration and idempotent schema creation.
- `models.py` — validation constants and row-to-JSON mapping helpers.
- `repository.py` — parameterized project and task persistence operations.
- `main.py` — application factory, routes, and static/template serving.
- `templates/` and `static/` — the server-rendered page and browser assets.
- `tests/` — repository, API, and UI-content tests.
- `playwright/` — browser acceptance scenarios.