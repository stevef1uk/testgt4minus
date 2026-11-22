# Phase-2 implementation plan — Tasks and Kanban UI

The active delivery gate is:
`cd taskboard && python -m pytest -q tests`

This plan covers only the phase-2 files and turns the SPEC §6 UI contract and
architecture.md delivery/testing contract into concrete acceptance checks. Existing
phase-1 API/repository behavior must remain compatible with these consumers.

## Bead map

### tm-c2q: taskboard/templates/index.html
- Scope: Implement the canonical TaskBoard document structure, forms, selectors, task controls, Kanban regions, and static-asset links.
- Architecture: architecture.md § UI layer and § Delivery phases (phase-2); SPEC §6 “UI contract”.
- Interfaces: Serve the page consumed by the existing root route; expose IDs/labels for project form and selector, task form with title/description/priority, status and priority filters, project deletion, To Do/Doing/Done columns, loading/empty/error regions, and edit/move/delete task controls.
- Depends on: <none>
- Consumed by: taskboard/static/app.js (tm-rta), taskboard/static/style.css (tm-2ob), taskboard/tests/test_ui_content.py (tm-r98), taskboard/tests/test_api.py (tm-rmz)
- Acceptance: HTML contains the TaskBoard heading; project creation form and project selector/list; task title, description, and priority controls; status/priority filters; all three exact column headings To Do, Doing, and Done; project-delete control; task edit, move-forward, and delete affordances; loading, empty, and visible error regions.
- Acceptance: The document loads `/static/app.js` and `/static/style.css`, uses real controls rather than placeholder text, and provides containers in which seeded project/task values and errors can be rendered.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-2ob: taskboard/static/style.css
- Scope: Provide the responsive Kanban and task-card presentation for the canonical page.
- Architecture: architecture.md § UI layer/static assets and § Delivery phases (phase-2); SPEC §6 responsive layout requirement.
- Interfaces: CSS selectors/classes used by taskboard/templates/index.html (tm-c2q) for the page shell, project/task forms, filters, `.kanban`/column regions, task cards, controls, and loading/empty/error states.
- Depends on: taskboard/templates/index.html (tm-c2q)
- Consumed by: taskboard/tests/test_ui_content.py (tm-r98), taskboard/tests/test_api.py (tm-rmz)
- Acceptance: The stylesheet is nonempty and defines visible project/task form, filter, column, and card layout hooks; To Do/Doing/Done columns render as a usable responsive layout that adapts to narrow widths; cards and action controls remain readable and visibly distinct; empty/loading/error states have dedicated styling hooks.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rta: taskboard/static/app.js
- Scope: Implement the browser-side project/task lifecycle and Kanban interactions against the existing API.
- Architecture: architecture.md § UI layer/client behavior and § Delivery phases (phase-2); SPEC §6 “UI contract”.
- Interfaces: Browser module calls `GET /api/projects`, project/task collection and update/delete routes specified in SPEC §5, renders into the index.html regions, and exports/uses no invented server API; user-provided values are rendered with `textContent` and DOM replacement uses `replaceChildren`.
- Depends on: taskboard/templates/index.html (tm-c2q)
- Consumed by: taskboard/tests/test_ui_content.py (tm-r98), taskboard/tests/test_api.py (tm-rmz)
- Acceptance: On load and project selection, fetch `/api/projects` and render projects/tasks; create projects and tasks through the documented forms; support status/priority filters and refresh results; support task edit and delete; move tasks forward from todo to doing to done using the documented update route; support project deletion and clear the selected project.
- Acceptance: Render To Do/Doing/Done columns, loading/empty/error states, and task values visibly; surface failed requests in the error region; use `textContent` (not unsafe HTML interpolation) for user content and `replaceChildren` when replacing rendered collections.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-yo8: taskboard/tests/test_repository.py
- Scope: Preserve and exercise the repository contract required by the phase-2 UI and its API consumers.
- Architecture: architecture.md § Repository/unit tests and § Delivery phases; SPEC §7 repository testing contract.
- Interfaces: Tests exercise the repository functions/types defined by architecture.md against an isolated temporary database; no production API is invented.
- Depends on: <none>
- Consumed by: taskboard/tests/test_api.py (tm-rmz), taskboard/static/app.js (tm-rta)
- Acceptance: Assert schema initialization is idempotent and records have exact fields, integer IDs, UTC timestamps, deterministic ascending-ID ordering, and documented defaults; accept project names through 80 and task titles through 120, reject empty/over-limit values including 81-character names and 121-character titles, and reject overlong descriptions.
- Acceptance: Assert unknown status and priority values fail without persistence; status, priority, and combined filters are ANDed; partial updates preserve omitted fields and cannot reassign projects; deleting a project cascades to its tasks. Include concrete create, patch, filter, and cascade assertions, not file-existence checks.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-rmz: taskboard/tests/test_api.py
- Scope: Keep the API and static-serving contract executable while phase-2 assets consume it.
- Architecture: architecture.md § API/unit tests and § Delivery phases; SPEC §5 HTTP contract and §7 testing contract.
- Interfaces: Tests use the documented FastAPI routes and temporary-database fixture; exact route paths, statuses, response keys, and error object shape come from SPEC §5.
- Depends on: taskboard/tests/test_repository.py (tm-yo8), taskboard/templates/index.html (tm-c2q), taskboard/static/app.js (tm-rta), taskboard/static/style.css (tm-2ob)
- Consumed by: <none>
- Acceptance: Assert `GET /api/health` is 200 with exact JSON `{"status": "ok"}`; verify project create/list/delete success shapes, empty lists, missing-project errors, malformed integer paths (422), and `{"error": ...}` failures while isolating temporary database state.
- Acceptance: Assert invalid project/task writes do not persist; cover 80/81-character project names, 120/121-character task titles, description maximum, unknown status/priority, status/priority filters, partial updates, project-delete cascade, and bodyless deletes with the documented statuses and response bodies.
- Acceptance: Assert root HTML contains TaskBoard, project controls, and empty/error regions; `/static/app.js` and `/static/style.css` return nonempty bodies with their documented content types and contain the required safe-rendering, API, Kanban, and responsive UI hooks.
- Verify: `cd taskboard && python -m pytest -q tests`

### tm-r98: taskboard/tests/test_ui_content.py
- Scope: Add focused phase-2 contract checks for the canonical HTML and static client assets.
- Architecture: architecture.md § UI layer tests and § Delivery phases (phase-2); SPEC §6 and §7 UI/static testing contract.
- Interfaces: Read the canonical files under taskboard/templates and taskboard/static; assertions target stable IDs, labels, routes, and safe DOM APIs specified by the UI contract.
- Depends on: taskboard/templates/index.html (tm-c2q), taskboard/static/app.js (tm-rta), taskboard/static/style.css (tm-2ob)
- Consumed by: <none>
- Acceptance: Assert HTML exposes project form/selector, task form and priority options, status/priority filters, project-delete control, To Do/Doing/Done columns, and loading/empty/error regions, and loads both canonical assets.
- Acceptance: Assert JavaScript contains `/api/projects`, `textContent`, `replaceChildren`, task move/edit/delete flows, filter refresh, and visible error handling; assert CSS contains responsive column/card layout hooks. Reject placeholder or file-existence-only implementations.
- Verify: `cd taskboard && python -m pytest -q tests`

## Phase-2 completion criteria

All six beads are implemented without changing the documented API contract, and the
single phase gate passes. The acceptance is behavioral: rendered regions, exact
health JSON, validation boundaries, filters, cascade and bodyless deletes, safe
rendering, and task move/edit/delete behavior must be asserted by tests.
