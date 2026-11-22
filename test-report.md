# Test Review — phase-1-core

## Summary
Phase verification is green, but the repaired coverage is incomplete. The repository partial-update repair is substantive; the requested API scenarios remain untested, and the implementation findings remain reproducible from the reviewed source.

## Per-requirement results

### phase-1-core — PASS
- Test file: `taskboard/tests/test_repository.py`
- Verify result: `cd taskboard && python -m pytest -q tests/test_repository.py` passed.
- The repository test independently patches description, priority, status, and title, asserting each changed value and asserting omitted fields remain unchanged after every patch.
- Evidence: {"file":"taskboard/tests/test_repository.py","line":139,"excerpt":"assert patched[\"description\"] == \"Rewritten\""}
- Evidence: {"file":"taskboard/tests/test_repository.py","line":146,"excerpt":"assert patched[\"priority\"] == \"low\""}
- Evidence: {"file":"taskboard/tests/test_repository.py","line":152,"excerpt":"assert patched[\"status\"] == \"done\""}

### phase-1-app — FAIL
- Test file: `taskboard/tests/test_api.py`
- The file has real API assertions and the full pytest suite is green, but it does not cover the requested repaired scenarios: root form controls and empty-state container, DELETE of a missing project with its `{"error": ...}` body, whitespace-only project names, or explicit UTC-offset timestamps.
- The existing assertion at the missing-project task-list route is not coverage for DELETE `/api/projects/{project_id}`.
- No valid evidence line can be supplied for the missing API scenarios because the required assertions are absent.

### implementation repair — FAIL
- Source file: `taskboard/main.py`
- Project creation strips the name only at insertion, after Pydantic's `min_length=1` check, so whitespace-only names can pass validation and be persisted.
- The database schema in this file uses `CURRENT_TIMESTAMP`, which produces a naive timestamp, rather than the explicit UTC-offset timestamp required by SPEC §4. The API tests do not currently detect either issue.

## Overall assessment
FAIL. Reopen `tm-rmz` for `taskboard/tests/test_api.py` and add independent assertions for all four missing scenarios. Reopen `tm-lro` for `taskboard/main.py` and repair whitespace-only project-name rejection and explicit UTC-offset timestamps. Reopen `tm-edl` only if the repository partial-update repair is not retained; the current repository assertions above cover that finding. Re-run the phase verify and the full pytest suite after repair.
