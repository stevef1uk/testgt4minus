# Phase 3 implementation plan

Phase 3 completes the filters/browser-test release check. Implement only the four
active paths below. Existing Python application, templates, static assets, and
pytest files are phase-2 outputs: consume them and do not create duplicate
application files.

## Verification

From the rig working directory, the polecat/test-reviewer must run exactly:
`cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`
The server is expected to already be running at `127.0.0.1:8080`; this phase
must not add a second server, container, wrapper, or frontend build.

## Bead map

### tm-5d8: taskboard/package.json
- Scope: Provide the canonical Playwright package manifest for the phase-3 browser harness.
- Architecture: `architecture.md` Planned file layout and Module / bead ownership; the manifest contains the validated `@playwright/test` 1.62.1 development dependency and Chromium test script.
- Interfaces: Supplies npm metadata and the `test` script consumed by the phase verification and by `taskboard/playwright.config.ts` and `taskboard/playwright/taskboard.spec.ts`.
- Depends on: <none>
- Consumed by: taskboard/package-lock.json; taskboard/playwright.config.ts; taskboard/playwright/taskboard.spec.ts
- Acceptance: The file is valid JSON; its package name/version and `npx playwright test --project=chromium` script match the validated phase-3 content; `@playwright/test` is a development dependency pinned to 1.62.1; no application runtime or build dependency is added.
- Verify: `test -s taskboard/package.json`

### tm-ddc: taskboard/package-lock.json
- Scope: Provide the canonical reproducible npm lockfile matching the Playwright manifest.
- Architecture: `architecture.md` Planned file layout and phase-3 delivery mapping; lockfile is generated/matching package metadata and is not an application dependency manifest.
- Interfaces: Provides deterministic dependency metadata for the package.json installation used by the Playwright CLI and browser spec.
- Depends on: taskboard/package.json
- Consumed by: taskboard/playwright.config.ts; taskboard/playwright/taskboard.spec.ts
- Acceptance: The file is present, nonempty, valid lockfile JSON, and matches `taskboard/package.json`; it records `@playwright/test` 1.62.1 and does not introduce a second application or container.
- Verify: `test -s taskboard/package-lock.json`

### tm-p96: taskboard/playwright.config.ts
- Scope: Configure the canonical Playwright runner for the existing host application.
- Architecture: `architecture.md` Module / bead ownership and E2E / integration testing; export the default config with `testDir: './playwright'`, the BASE_URL default `http://127.0.0.1:8080`, Chromium-only project, 10-second timeout, CI worker behavior, HTML/list reporters, and first-retry tracing.
- Interfaces: Exports the default Playwright configuration consumed by the Playwright CLI and `taskboard/playwright/taskboard.spec.ts`.
- Depends on: taskboard/package.json; taskboard/package-lock.json
- Consumed by: taskboard/playwright/taskboard.spec.ts
- Acceptance: The config discovers the canonical spec under `playwright/`; BASE_URL overrides the host URL; only the Chromium project is configured; the specified HTTPS-upgrade/certificate launch arguments, timeout, reporters, retry, and trace settings are retained; it does not start another server or add aliases.
- Verify: `test -s taskboard/playwright.config.ts`

### tm-ebm: taskboard/playwright/taskboard.spec.ts
- Scope: Implement independent browser acceptance scenarios against the real TaskBoard UI.
- Architecture: `architecture.md` E2E / integration testing and phase-3 requirement; browser interactions belong in this file only, while application behavior remains in `taskboard/static/app.js`.
- Interfaces: Provides Playwright test cases loaded by the config and verification command; uses the visible page, forms, Kanban columns, task cards, filters, and configured BASE_URL.
- Depends on: taskboard/package.json; taskboard/package-lock.json; taskboard/playwright.config.ts; taskboard/main.py; taskboard/templates/index.html; taskboard/static/app.js; taskboard/static/style.css
- Consumed by: <none>
- Acceptance: Include three independent scenarios required by SPEC: initial load asserts the real `TaskBoard` heading and `To Do`, `Doing`, and `Done` columns; a unique-project flow creates a task, verifies it in To Do, moves it to Doing then Done, deletes it, and asserts disappearance; a unique-project filter flow creates low- and high-priority tasks, selects `high`, asserts only the high task is rendered, resets to `all`, and asserts both return. Use real accessible controls and task content, clean up created projects/tasks, avoid test-order or pre-existing-data dependence, and do not reduce checks to status codes or placeholders.
- Verify: `test -s taskboard/playwright/taskboard.spec.ts`

## Phase acceptance

The complete phase passes the exact verification command above. Python tests
must continue to prove the existing API/filter behavior, and Playwright must
prove visible filter results and real state transitions against the already
running local server. No out-of-SPEC routes, dependencies, application
containers, duplicate configs/specs, or generated reports are added.
