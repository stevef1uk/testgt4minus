# Implementation plan

## Active phase: phase-3

Phase 3 owns the Playwright manifests, host configuration, browser scenarios,
and release check. It does not create backend or application files. The exact
phase verification is:
`cd taskboard && python -m pytest -q tests && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`
Dependencies are installed before test review; the verification command itself
must not install packages or start a second server.

## Bead map

### ○: taskboard/package.json
- Scope: Define the Node manifest with `@playwright/test` as the development dependency only.
- Architecture: architecture.md, Planned file layout and Delivery phases phase-3.
- Interfaces: npm metadata and the Playwright dependency consumed by the canonical config and spec.
- Depends on: <none>
- Consumed by: taskboard/package-lock.json; taskboard/playwright.config.ts; taskboard/playwright/taskboard.spec.ts
- Acceptance: The manifest supports the canonical Playwright runner, adds no frontend build, application runtime, duplicate config, wrapper, or container.
- Verify: `cd taskboard && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

### ○: taskboard/package-lock.json
- Scope: Provide the generated lockfile matching package.json and its Playwright dependency graph.
- Architecture: architecture.md, Planned file layout and Delivery phases phase-3; this is npm tool output, not a second manifest.
- Interfaces: npm lockfile metadata and reproducible dependency resolution for the installed runner.
- Depends on: taskboard/package.json (○)
- Consumed by: taskboard/playwright.config.ts; taskboard/playwright/taskboard.spec.ts
- Acceptance: Root metadata matches package.json and resolves the declared Playwright dependency without extra application dependencies.
- Verify: `cd taskboard && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

### : taskboard/playwright.config.ts
- Scope: Configure the canonical browser suite for the already-running host server at 127.0.0.1:8080.
- Architecture: architecture.md, E2E / integration testing and phase-3 delivery contract.
- Interfaces: Export the Playwright configuration consumed by --config; target the canonical playwright directory and host URL.
- Depends on: taskboard/package.json (○); taskboard/package-lock.json (○)
- Consumed by: taskboard/playwright/taskboard.spec.ts ()
- Acceptance: The required command discovers the canonical spec, uses the existing host server, and invokes no Docker, container hostname, or second application.
- Verify: `cd taskboard && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

### : taskboard/playwright/taskboard.spec.ts
- Scope: Implement the three independent SPEC browser scenarios with unique data and cleanup.
- Architecture: architecture.md, E2E / integration testing and phase-3 requirements.
- Interfaces: Playwright test declarations consumed by the canonical config; no production exports or routes.
- Depends on: taskboard/playwright.config.ts (); taskboard/package.json (○); taskboard/package-lock.json (○)
- Consumed by: phase-3 release verification
- Acceptance: Assert the real TaskBoard heading and all three column headings; create and move a unique task todo-to-doing-to-done then delete it; create two differently prioritized tasks, filter high to show only the high task, reset to show both; scenarios must not depend on order or prior data.
- Verify: `cd taskboard && ./node_modules/.bin/playwright test --config playwright.config.ts playwright`

## Release gate

Implement package metadata, lockfile, configuration, then scenarios. Run exactly
the phase verification from taskboard against 127.0.0.1:8080. Both the complete
pytest suite and real browser assertions must pass. No additional routes,
frontend build, deployment mechanism, or out-of-scope feature is planned.

## Future considerations

None for this phase; later application changes remain owned by their earlier
canonical files and are not new phase-3 beads.
