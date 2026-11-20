# Test Review — Phase 1 foundation and runnable app

## Summary

The configured Phase 1 verification passed: `cd taskboard && python -m pytest -q tests` reported 16 passed. The active test files exist and contain real assertions, but coverage is incomplete for two active requirements.

## Per-requirement results

### phase-1-core — FAIL

- Test file: `taskboard/tests/test_repository.py`
- Verify result: passed (the full suite passed)
- Notes: The tests cover idempotent initialization, empty lists, ordering, timestamps, defaults, filters, partial updates, cascade deletion, and some validation. They do not assert rejection of invalid status/priority values or demonstrate that writes remain parameterized, despite those behaviors being explicitly included in this planned requirement.

### phase-1-app — FAIL

- Test file: `taskboard/tests/test_api.py`
- Verify result: passed (the full suite passed)
- Notes: The tests cover health JSON, project CRUD, error status/body shape, static delivery, and database isolation. The root-content assertion only checks `id="project-page"` and static references; it does not assert the required visible `TaskBoard` heading and project form content.

### phase-2 — DEFERRED

- Test files: `taskboard/tests/test_api.py`, `taskboard/tests/test_ui_content.py`
- Notes: Future-phase requirement; not evaluated in this Phase 1 review.

### phase-3 — DEFERRED

- Test file: `taskboard/playwright/taskboard.spec.ts`
- Notes: Future-phase requirement; not evaluated in this Phase 1 review.

## Overall assessment

FAIL. Reopen `te-7yg` to add real repository assertions for invalid status/priority values and parameterized-write safety, and reopen `te-c2c` to assert the Phase 1 root response contains the `TaskBoard` heading and project form. Re-run the full Phase 1 verification after those test additions.
