# Implementation plan

## Active phase: phase-3

Phase 3 delivers only the Playwright toolchain and browser release checks.
Existing Phase 2 application files provide the filters and UI under test. The
required verification command is:
`cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`
Run it from `taskboard/` against the already-running server at
`127.0.0.1:8080`; it must not start another application or container.

## Bead map

### te-8ip: taskboard/package.json
- Scope: Define the Node manifest with `@playwright/test` as the development dependency only.
- Architecture: `architecture.md` Planned file layout and Delivery phases `phase-3`.
- Interfaces: npm package metadata and the Playwright dependency consumed by the config and browser spec.
- Depends on: `<none>`
- Consumed by: `taskboard/package-lock.json`; `taskboard/playwright.config.ts`; `taskboard/playwright/taskboard.spec.ts`
- Acceptance: The manifest supports the canonical Playwright runner and introduces no frontend build, application runtime, duplicate config, wrapper, or container.
- Verify: `cd taskboard && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

### te-0j6: taskboard/package-lock.json
- Scope: Provide the generated lockfile matching package.json and its Playwright dependency graph.
- Architecture: `architecture.md` Planned file layout and Delivery phases `phase-3`; this is npm tool output, not a second manifest.
- Interfaces: Lockfile root metadata and reproducible dependency resolution for the configured runner.
- Depends on: `taskboard/package.json` (te-8ip)
- Consumed by: `taskboard/playwright.config.ts`; `taskboard/playwright/taskboard.spec.ts`
- Acceptance: Root metadata matches package.json, the declared Playwright dependency resolves, and no unrelated application dependency is added.
- Verify: `cd taskboard && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

### te-3ut: taskboard/playwright.config.ts
- Scope: Configure the canonical browser suite for the existing TaskBoard host server at `127.0.0.1:8080`.
- Architecture: `architecture.md` E2E / integration testing and Delivery phases `phase-3`.
- Interfaces: Export the Playwright configuration consumed by `--config playwright.config.ts`; target the canonical `playwright` directory and host URL.
- Depends on: `taskboard/package.json` (te-8ip); `taskboard/package-lock.json` (te-0j6)
- Consumed by: `taskboard/playwright/taskboard.spec.ts` (te-u8o)
- Acceptance: The required runner discovers the canonical spec, targets the existing host server, and does not invoke Docker, a container hostname, or a second application.
- Verify: `cd taskboard && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

### te-u8o: taskboard/playwright/taskboard.spec.ts
- Scope: Implement the three independent SPEC browser scenarios using real UI interactions, unique data, and cleanup.
- Architecture: `architecture.md` E2E / integration testing, phase-3 requirements, and SPEC §7 Browser E2E.
- Interfaces: Playwright test declarations consumed by the canonical config; no production exports or additional routes.
- Depends on: `taskboard/playwright.config.ts` (te-3ut); `taskboard/package.json` (te-8ip); `taskboard/package-lock.json` (te-0j6)
- Consumed by: phase-3 release verification
- Acceptance: Scenario one asserts the real TaskBoard heading and To Do, Doing, and Done headings. Scenario two creates a unique project and task, verifies To Do, moves it to Doing and Done, deletes it, and asserts disappearance. Scenario three creates two uniquely named tasks with different priorities, selects high, asserts only the high-priority task is visible, resets the filter, and asserts both return. Tests are independent of order and prior data and inspect real task content.
- Verify: `cd taskboard && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

## Dependency order and release gate

Implement package metadata first, then its lockfile, then Playwright
configuration, then browser scenarios. The browser files consume the existing
Phase 2 template, static JavaScript, API routes, and filter behavior; they do
not duplicate or replace those files. The phase succeeds only when the exact
pytest plus Playwright command above passes, with all browser assertions
demonstrating the SPEC behavior.

## Future considerations

No additional frontend build, deployment mechanism, route, framework, or
out-of-scope feature is included in this phase.
