# Test Review — Tasks and Kanban UI

## Summary
Partial tests pass; the configured Phase 2 pytest verification passes, but planned Phase 2 coverage is inadequate.

## Per-requirement results
### phase-1-core — PASS
- Test file: `taskboard/tests/test_repository.py`
- Verify result: passed (`31 passed`)
- Notes: Repository tests contain substantive assertions for schema setup, validation, defaults, ordering, filtering, partial updates, timestamps, and cascade deletion.

### phase-1-app — PASS
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed (`31 passed`)
- Notes: API tests exercise the real FastAPI/TestClient wiring and assert health, project CRUD, errors, HTML, and static assets.

### phase-2 repository behavior — PASS
- Test file: `taskboard/tests/test_repository.py`
- Verify result: passed
- Notes: Existing repository assertions exercise task creation/defaults, filters, partial updates, validation, ordering, and cascade behavior.

### phase-2 task API behavior — FAIL
- Test file: `taskboard/tests/test_api.py`
- Verify result: pytest passed, but planned coverage is incomplete.
- Notes: The plan requires composed filters, all supported PATCH fields and omitted-field preservation, null and empty PATCH rejection, malformed integer paths, missing task behavior, empty arrays, exact timestamps, and the full validation matrix. The file only partially exercises these cases; in particular it does not substantively assert all listed scenarios.

### phase-2 UI behavior — FAIL
- Test file: `taskboard/tests/test_ui_content.py`
- Verify result: pytest passed, but planned coverage is incomplete.
- Notes: The tests only inspect a small set of element IDs and three JavaScript substrings. They do not assert the TaskBoard heading, task form, selectors, priority controls, three Kanban headings, task controls, project selection, or visible empty/error behavior required by the plan and SPEC.

### phase-3 — DEFERRED
- Test file: `taskboard/playwright/taskboard.spec.ts`
- Notes: Future-phase requirement; not evaluated in this Phase 2 review.

## Overall assessment
The Phase 2 pytest command is green, but the planned Phase 2 API and UI tests do not cover every stated requirement. Repair the named tests and re-run the complete Phase 2 verification.
