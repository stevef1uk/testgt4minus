# Phase 3 implementation plan

Phase 3 owns exactly four required files: the Playwright manifest and
lockfile, the canonical host configuration, and the canonical browser
scenarios. Earlier-phase Python, template, static, and pytest files are
consumed dependencies, not new work in this phase. Preserve the validated
content for the four active files and do not create duplicate harness paths.

## Verification contract

The polecat must run this exact command from the town root:
`cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`
The application is already available at `http://127.0.0.1:8080`. The command
must exercise the complete pytest suite and the Chromium browser scenarios
against that existing server. Dependency preparation happens before review;
the verification command itself only runs the specified test tools.

## Bead map

### tm-5d8: taskboard/package.json
- Scope: Provide the canonical browser-test manifest named `playwright-tests`, version `1.0.0`, with the `test` script `npx playwright test --project=chromium` and `@playwright/test` version `1.62.1` under `devDependencies`.
- Architecture: `architecture.md` Planned file layout, Module / bead ownership, and `phase-3` delivery mapping.
- Interfaces: npm `test` script and the pinned Playwright development dependency consumed by the CLI and browser specification.
- Depends on: `<none>`
- Consumed by: taskboard/package-lock.json (tm-ddc), taskboard/playwright.config.ts (tm-p96), taskboard/playwright/taskboard.spec.ts (tm-ebm)
- Acceptance: The file is valid JSON; its script and exact dependency version match SPEC; it adds no runtime dependency, frontend build, alternate config, or container.
- Verify: `cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

### tm-ddc: taskboard/package-lock.json
- Scope: Preserve the validated lockfile corresponding to taskboard/package.json and its reproducible Playwright dependency graph.
- Architecture: `architecture.md` Planned file layout and `phase-3` delivery mapping.
- Interfaces: Lockfile package metadata consumed by the project dependency resolver and the canonical Playwright executable.
- Depends on: taskboard/package.json (tm-5d8)
- Consumed by: taskboard/playwright.config.ts (tm-p96), taskboard/playwright/taskboard.spec.ts (tm-ebm), release verification
- Acceptance: The lockfile is valid, nonempty, and consistent with package.json; its root metadata and Playwright version match exactly; no unrelated application dependency or second harness is introduced.
- Verify: `cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

### tm-p96: taskboard/playwright.config.ts
- Scope: Provide the validated Playwright configuration with `./e2e` test directory, 10000ms timeout, CI forbid-only/retry/worker behavior, HTML and list reporters, first-retry tracing, BASE_URL override with default `http://127.0.0.1:8080`, and the Chromium Desktop Chrome project.
- Architecture: `architecture.md` Module / bead ownership and E2E / integration testing; retain the validated `defineConfig` default export and launch arguments.
- Interfaces: Default export consumed by the Playwright CLI and spec; `baseURL` reads `BASE_URL`; project name is `chromium`; the required command loads this config.
- Depends on: taskboard/package.json (tm-5d8), taskboard/package-lock.json (tm-ddc)
- Consumed by: taskboard/playwright/taskboard.spec.ts (tm-ebm), release verification
- Acceptance: Chromium is the only configured project; CI uses one worker and forbids focused tests; reporters do not auto-open; tracing is on first retry; the required HTTPS-upgrade disabling and certificate-ignore arguments remain present; no server startup or path alias is added.
- Verify: `cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

### tm-ebm: taskboard/playwright/taskboard.spec.ts
- Scope: Provide three independent browser acceptance scenarios against the real TaskBoard UI, using unique project data and cleanup through the application API or UI.
- Architecture: `architecture.md` E2E / integration testing and phase-3 requirements; browser interactions belong here while behavior remains in taskboard/static/app.js.
- Interfaces: Playwright tests loaded from the configured `playwright` directory; use the configured base URL, visible forms, Kanban columns, task cards, filters, and project/task cleanup endpoints.
- Depends on: taskboard/package.json (tm-5d8), taskboard/package-lock.json (tm-ddc), taskboard/playwright.config.ts (tm-p96), taskboard/main.py, taskboard/templates/index.html, taskboard/static/app.js, taskboard/static/style.css
- Consumed by: the canonical phase-3 verification command
- Acceptance: First load asserts `TaskBoard` plus `To Do`, `Doing`, and `Done`. A unique project flow creates a task, proves To Do, moves it to Doing and Done, deletes it, and proves disappearance. A separate unique project flow creates low/high tasks, filters to high and proves only high is visible, then resets and proves both return. Assertions inspect real text and controls; scenarios do not depend on order or pre-existing data; cleanup cannot hide assertion failures.
- Verify: `cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

## Phase boundary

Only the four mapped paths are active. Do not add routes, persistence code,
frontend build tooling, alternate configs/specs, containers, or completed-phase
test files. The release gate must prove both the existing pytest behavior and
the SPEC browser requirements.
