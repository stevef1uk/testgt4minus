# Implementation plan — phase-2 (Tasks and Kanban UI)

Rig: testgt4m. Active delivery phase: phase-2 per architecture.md delivery_phases.
All bead IDs below are real IDs printed by bd list --limit=0 in this planning session.
Phase gate (verification for every bead in this phase): cd taskboard && python -m pytest -q tests

## Bead map

### tm-2ob: taskboard/static/style.css
- Scope: extend the Phase-1 stylesheet in place with Kanban column, task card, status/priority badge, filter control, and empty/loading/error-state styling; desktop and narrow-window layouts stay usable. No behavior, no new CSS path.
- Architecture: Planned file layout "responsive taskboard presentation"; module ownership row: owns page, form, card, column, status, and responsive styling; must not define application data or behavior.
- Interfaces: stylesheet only, no code symbols; consumed via href="/static/style.css" in taskboard/templates/index.html (tm-c2q) and asserted by tm-r98.
- Depends on: taskboard/main.py (static mounting, delivered in phase-1-app).
- Consumed by: tm-c2q (taskboard/templates/index.html), tm-r98 (taskboard/tests/test_ui_content.py).
- Acceptance:
  - Single canonical file taskboard/static/style.css; phase-2 extends it in place and introduces no duplicate or alternate CSS path (SPEC section 8).
  - GET /static/style.css returns 200 with a nonempty body through the app static mount (SPEC section 6 browser routes, section 7 content tests item 2).
  - Styles cover the TaskBoard heading, project and task forms, three Kanban columns, task cards and their controls, status/priority indicators, both filter dropdowns, and the visible empty/error regions (SPEC section 6 UI requirements).
  - Desktop and narrow-window layouts remain usable (SPEC section 6).
- Verify: cd taskboard && python -m pytest -q tests

### tm-c2q: taskboard/templates/index.html
- Scope: extend the Phase-1 template in place: task form (title required, optional description, priority select low/medium/high, Add task), three Kanban columns, task cards with controls, status/priority filter dropdowns, delete-project control with window.confirm, and empty/loading/error regions. No second page, no new layout.
- Architecture: module ownership row: owns semantic forms, selectors, columns, and message regions; must not define database calls or inline application logic.
- Interfaces: DOM ids consumed by taskboard/static/app.js (tm-rta) and asserted by tm-r98: project-form-region, project-form, project-list, project-filter, empty-state, loading-state, error-state; loads src="/static/app.js" and href="/static/style.css".
- Depends on: taskboard/main.py route and static wiring (delivered in phase-1-app); tm-2ob (linked stylesheet).
- Consumed by: tm-rta (binds to these ids), tm-r98 (asserts ids and asset links).
- Acceptance:
  - Page heading TaskBoard and three visible Kanban columns headed To Do, Doing, Done (SPEC section 6).
  - Project creation input with Add project button; project selector/list populated by /api/projects on page load; selecting a project shows its tasks (SPEC section 6).
  - Task form: title required, optional description, priority select (low, medium, high), Add task button (SPEC section 6).
  - Cards carry Move forward (todo to doing to done; hidden or disabled on done cards), Edit, and Delete controls (SPEC section 6).
  - Status filter dropdown (all, todo, doing, done) and priority filter dropdown (all, low, medium, high); delete-project control uses standard window.confirm (SPEC section 6).
  - All seven pinned element ids present: project-form-region, project-form, project-list, project-filter, empty-state, loading-state, error-state (tm-r98 test_index_contains_required_ui_regions_and_controls).
  - GET / returns 200 text/html with real TaskBoard markup, not a fallback placeholder (SPEC section 6 browser routes).
- Verify: cd taskboard && python -m pytest -q tests

### tm-rta: taskboard/static/app.js
- Scope: extend the Phase-1 script in place with task and Kanban behavior: project selection, task creation/edit/delete, move-forward transitions, status/priority filter refresh via API query parameters, safe rendering, and visible empty/error states.
- Architecture: module ownership row: owns loading, creating, editing, moving, filtering, deleting, and safe DOM rendering; must not implement server validation.
- Interfaces: consumes SPEC section 5 routes exactly — GET /api/projects, POST /api/projects/{project_id}/tasks, PATCH /api/tasks/{task_id}, DELETE /api/tasks/{task_id}; binds to tm-c2q element ids; uses textContent and replaceChildren.
- Depends on: tm-c2q (element ids), taskboard/main.py API routes (delivered in phase-1-app).
- Consumed by: tm-r98 (pinned content assertions), phase-3 Playwright scenarios (later phase, do not implement here).
- Acceptance:
  - Populates the project selector from GET /api/projects on page load; selecting a project lists its tasks (SPEC section 6).
  - Creates tasks via POST /api/projects/{project_id}/tasks with title required, optional description, priority select; new tasks land in the To Do column as status todo (SPEC section 6).
  - Move forward advances a card one step (todo to doing to done) and is hidden or disabled on done cards; Edit updates title/description/priority via PATCH; Delete removes the card via DELETE (SPEC section 6).
  - Both filter dropdowns refresh the task list with status and priority query parameters; filtered-out cards are not rendered (SPEC section 6).
  - Renders user-provided text with textContent and clears containers with replaceChildren; never injects user content as raw innerHTML (SPEC section 6, pinned tm-r98 assertion).
  - Shows API error messages in the visible error-state region and empty-state message when there are no projects or no matching tasks; never silently swallows errors (SPEC section 6).
- Verify: cd taskboard && python -m pytest -q tests

### tm-yo8: taskboard/tests/test_repository.py
- Scope: extend the Phase-1 repository suite in place with task repository coverage (SPEC section 7 items 1-6) while preserving every earlier phase-1-core assertion; isolated tmp_path database per test, never the runtime taskboard.db.
- Architecture: module ownership row: owns repository assertions; must not assert HTTP or browser behavior. Uses taskboard/db.py, taskboard/models.py, taskboard/repository.py (delivered in phase-1-core).
- Interfaces: imports ProjectRepository/TaskRepository from taskboard.repository and schema helpers from taskboard.db; database path is tmp_path / "taskboard-test.db" per test (SPEC section 7).
- Depends on: taskboard/db.py, taskboard/models.py, taskboard/repository.py (all delivered in phase-1-core).
- Consumed by: tm-rmz and tm-r98 only in the sense that the combined phase gate must stay green; no file imports this file.
- Acceptance (each maps to SPEC section 7):
  - New database has empty projects and schema init is idempotent (item 1).
  - Projects create and list in deterministic ascending ID order (item 2).
  - Tasks persist with default status todo and priority medium and UTC timestamps with explicit offset (item 3).
  - Lists filter by status, by priority, and by both combined with AND (item 4).
  - Patching title/description/priority/status preserves omitted fields (item 5).
  - Deleting a project cascades to its tasks (item 6).
  - Earlier phase-1-core negative boundaries remain present: 80-character project name accepted / 81 rejected, 120-character task title accepted / 121 rejected, description at maximum accepted / overlong rejected, unknown status and unknown priority rejected with the validation error (architecture phase-1-core requirements).
  - Assertions prove real state changes; no trivial always-pass tests (no assert True, no empty test bodies, no import-only tests).
- Verify: cd taskboard && python -m pytest -q tests

### tm-rmz: taskboard/tests/test_api.py
- Scope: extend the Phase-1 API suite in place with task API coverage (SPEC section 7 items 1-8) while preserving every earlier assertion; uses the isolated conftest fixtures from phase-1-app.
- Architecture: module ownership row: owns API assertions; must not depend on repository implementation details. Uses taskboard/tests/conftest.py fixtures and taskboard.main.create_app (delivered in phase-1-app).
- Interfaces: imports create_app from taskboard.main; FastAPI TestClient or HTTPX ASGI transport with a temporary database per test (SPEC section 7).
- Depends on: taskboard/tests/conftest.py, taskboard/main.py (both delivered in phase-1-app).
- Consumed by: the phase gate runs this suite together with tm-yo8 and tm-r98; no file imports this file.
- Acceptance (each maps to SPEC section 7):
  - GET /api/health returns exactly {"status":"ok"} (item 1).
  - Project create/list/delete round trip: 201 create, 200 list ordered by id ASC, 204 delete with empty body (item 2).
  - Task create/list/patch/delete round trip within a project (item 3).
  - Empty project name and empty task title rejected with 400 (item 4).
  - Bad status, bad priority, too-long title, and too-long description rejected with 400 (item 5).
  - 404 for missing project/task and 400 for an empty task PATCH payload (item 6).
  - Empty task lists serialize as [] and 204 deletes have no body (item 7).
  - Status and priority query filters compose with AND and preserve ascending ID order (item 8).
  - Application-level 400/404 bodies use {"error": "human-readable message"}; malformed integer paths keep the framework 422 (SPEC section 5).
  - Assertions prove real state changes; no trivial always-pass tests.
- Verify: cd taskboard && python -m pytest -q tests

### tm-r98: taskboard/tests/test_ui_content.py
- Scope: first-delivery owner in phase-2. Content integration tests pinned to the validated content reproduced below; reads the real worktree files with ROOT = Path(__file__).parents[1]; no HTTP and no database.
- Architecture: module ownership row: owns HTML and static asset assertions; must not touch persistence implementation. Architecture unit-test section: proves the rendered page contains the TaskBoard heading, project and task forms, all three column headings, and nonempty app.js and style.css content.
- Interfaces: reads taskboard/templates/index.html and taskboard/static/app.js relative to ROOT; depends on tm-c2q, tm-rta, tm-2ob content.
- Depends on: tm-c2q (taskboard/templates/index.html), tm-rta (taskboard/static/app.js), tm-2ob (taskboard/static/style.css).
- Consumed by: the phase gate runs this file together with tm-yo8 and tm-rmz.
- Acceptance (pinned test names and assertions from the validated content):
  - test_index_contains_required_ui_regions_and_controls: index.html contains id="project-form-region", id="project-form", id="project-list", id="project-filter", id="empty-state", id="loading-state", id="error-state".
  - test_index_loads_static_assets: index.html contains src="/static/app.js" and href="/static/style.css".
  - test_app_uses_safe_text_rendering_and_required_api_routes: app.js contains textContent, /api/projects, and replaceChildren.
  - Module uses ROOT = Path(__file__).parents[1] and Path.read_text; assertions target real file content, not placeholders.
- Verify: cd taskboard && python -m pytest -q tests

## Phase context

- Active phase: phase-2, Tasks and Kanban UI (architecture delivery_phases). Depends on phase-1-core and phase-1-app, both complete: taskboard/db.py, taskboard/models.py, taskboard/repository.py, taskboard/main.py, taskboard/tests/conftest.py are delivered and are extended in place, not duplicated.
- Phase gate for every bead: cd taskboard && python -m pytest -q tests — the full suite including all earlier phase assertions (architecture: preserve all earlier assertions).
- Phase-2 exit criteria (SPEC section 8): the pytest gate passes and a user can create a project and task, move it from todo to doing to done, edit it, and delete it via the real browser UI.
- No Integration contract section: phase-2 required_files contain no cmd/.../main entrypoint; taskboard/main.py was delivered in phase-1-app and is extended only through the phase-2 required files.

## Dependency ordering (polecat queue)

Earlier first; only real bead IDs from this session's bd list --limit=0:
1. tm-2ob (taskboard/static/style.css) and tm-c2q (taskboard/templates/index.html) — independent of each other.
2. tm-rta (taskboard/static/app.js) — binds to tm-c2q element ids.
3. tm-yo8 (taskboard/tests/test_repository.py) and tm-rmz (taskboard/tests/test_api.py) — depend only on delivered phase-1 files.
4. tm-r98 (taskboard/tests/test_ui_content.py) — depends on tm-c2q, tm-rta, tm-2ob content being present.

## Review amendments (phase-2 planning rework, addressing QA)

- All six phase-2 required paths now have exactly one open implement bead each, verified via bd list --limit=0 --status=open,in_progress this session: tm-r98, tm-yo8, tm-rmz, tm-2ob, tm-c2q, tm-rta. The stale IDs QA named (tm-rta, tm-2ob, tm-c2q, tm-rmz, tm-yo8, tm-r98 are current; earlier unlisted tm-dv3, tm-ff6, tm-tvv, tm-51g, tm-edl references) have been removed — this Bead map references only IDs printed by bd list --limit=0 in this session.
- Every Verify field is the phase gate from architecture delivery_phases phase-2: cd taskboard && python -m pytest -q tests (full suite, earlier assertions preserved). Per-file pytest invocation was replaced by the phase gate.
- Cached validated content is the pinned target for tm-r98 and the in-place extension baseline for the other five files; polecat reuses the validated phase-1 file contents (index.html 4285 bytes, app.js 3616 bytes, style.css 3531 bytes, test_repository.py 7164 bytes, test_api.py 8338 bytes) and extends them without regressing pinned assertions.
- Scope stays inside SPEC section 6/7 and architecture phase-2: task repository operations, task API routes, validation, project selection, task creation/edit/delete, three Kanban columns, move-forward behavior, visible empty/error states, and expanded pytest repository/API/UI-content coverage. No filters beyond the specified dropdowns refresh behavior, no Playwright work (phase-3), no extra routes or dependencies (YAGNI).
