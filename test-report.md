# Test Review — Phase 1

## Summary
Phase verification passed (14 tests passed), but the active phase-1-app requirement is not adequately covered by its planned API test.

## Per-requirement results
### phase-1-core — PASS
- Test file: taskboard/tests/test_repository.py
- Verify result: passed (`cd taskboard && python -m pytest -q tests`)
- Notes: The repository suite contains substantive database inputs and assertions for initialization, persistence, defaults, ordering, updates, filters, validation, timestamps, and cascade behavior.

### phase-1-app — FAIL
- Test file: taskboard/tests/test_api.py
- Verify result: passed (`cd taskboard && python -m pytest -q tests`)
- Notes: The active plan requires root HTML/static responses, composed status/priority filters, detailed invalid status/priority/length and error-object behavior, malformed integer 422 behavior, empty-list behavior, and API cascade coverage. The current test file does not assert all of these. It also asserts `status: "in_progress"` at line 79, which contradicts the SPEC enum contract (`todo`, `doing`, `done`).
- Evidence: `{"file":"taskboard/tests/test_api.py","line":79,"excerpt":"        json={\"title\": \"Renamed\", \"status\": \"in_progress\"},"}`

## Overall assessment
FAIL — the configured pytest command is green, but the phase-1-app TEST_PLAN row is only partially covered. Repair `taskboard/tests/test_api.py` with real assertions for the missing API, HTML, static, validation, filter, 422, empty-list, and cascade requirements, then rerun the phase gate.
