# Phase 3 implementation plan

Phase 3 owns exactly the four active required files for filters, browser
scenarios, and the release check. Existing Python application, templates,
static assets, and pytest files are consumed dependencies from earlier phases;
do not create duplicate paths or reopen them in this phase.

## Verification contract

Run this command verbatim from the rig working directory:
`cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`
The Playwright verb is the literal `test`; it must remain unprefixed. The
command must load `taskboard/playwright.config.ts`, use the existing local
application at `http://127.0.0.1:8080`, pass the complete pytest suite, and
pass all three Chromium scenarios. Dependency setup occurs before review; the
verification command itself must not alter dependencies or start a second
application container.

## Bead map

### tm-5d8: taskboard/package.json
- Scope: Supply the canonical Playwright package manifest with the validated `@playwright/test` development dependency and Chromium test script.
- Architecture: `architecture.md` Planned file layout, Module / bead ownership, and phase-3 delivery mapping.
- Interfaces: npm metadata, the `test` script, and the `@playwright/test` package consumed by the Playwright CLI and spec.
- Depends on: <none>
- Consumed by: taskboard/package-lock.json; taskboard/playwright.config.ts; taskboard/playwright/taskboard.spec.ts
- Acceptance: Valid JSON declares `@playwright/test` version 1.62.1 under development dependencies; the script invokes `npx playwright test --project=chromium`; no application build or runtime dependency is added.

### tm-ddc: taskboard/package-lock.json
- Scope: Supply the committed lockfile matching the phase-3 package manifest.
- Architecture: `architecture.md` Planned file layout and phase-3 delivery mapping.
- Interfaces: Lockfile metadata used to resolve the Playwright package and `taskboard/node_modules/.bin/playwright`.
- Depends on: taskboard/package.json (tm-5d8)
- Consumed by: taskboard/playwright/taskboard.spec.ts and the canonical verification command
- Acceptance: Present, nonempty, valid lockfile JSON whose root package metadata and Playwright version match `taskboard/package.json`; it adds no second application or container.

### tm-p96: taskboard/playwright.config.ts
- Scope: Configure the canonical host-server Playwright run.
- Architecture: `architecture.md` Module / bead ownership and E2E / integration testing; preserve the validated config's default export, browser project, base URL, timeout, reporters, retries, and tracing.
- Interfaces: Default-exported Playwright configuration consumed by the CLI and `taskboard/playwright/taskboard.spec.ts`; base URL defaults to `http://127.0.0.1:8080` and may be overridden by `BASE_URL`.
- Depends on: taskboard/package.json (tm-5d8); taskboard/package-lock.json (tm-ddc)
- Consumed by: taskboard/playwright/taskboard.spec.ts and the canonical verification command
- Acceptance: The exact command discovers the canonical `playwright` spec directory, runs only the configured Chromium project, honors the host base URL, and retains the specified 10-second timeout, CI worker behavior, reporters, first-retry tracing, and certificate/HTTPS launch arguments. It must not start another server, rewrite the CLI verb, or add aliases.

### tm-ebm: taskboard/playwright/taskboard.spec.ts
- Scope: Implement independent browser acceptance scenarios against the real TaskBoard UI and clean up data created by each scenario.
- Architecture: `architecture.md` E2E / integration testing and phase-3 requirements; browser interactions belong in this file while application behavior remains in `taskboard/static/app.js`.
- Interfaces: Playwright tests loaded from the configured `playwright` directory; uses the configured base URL, project/task API cleanup, visible forms, Kanban columns, cards, and filter controls.
- Depends on: taskboard/package.json (tm-5d8); taskboard/package-lock.json (tm-ddc); taskboard/playwright.config.ts (tm-p96); taskboard/main.py; taskboard/templates/index.html; taskboard/static/app.js; taskboard/static/style.css
- Consumed by: the canonical phase-3 verification command
- Acceptance: (1) first load asserts the real `TaskBoard` heading and `To Do`, `Doing`, and `Done` columns; (2) an isolated unique project flow creates a task, asserts it in To Do, moves it to Doing and Done, deletes it, and asserts disappearance; (3) an isolated unique project flow creates low- and high-priority tasks, filters to high and asserts only the high task, resets to all and asserts both. Use real task text and controls, clean up created projects before/after scenarios without masking failures, and do not depend on test order or pre-existing projects.

## Phase boundary

Earlier-phase test files remain part of the pytest verification but are not
beads in this phase. No extra routes, wrapper scripts, duplicate configs/specs,
frontend build, container, or out-of-scope dependency is allowed.
