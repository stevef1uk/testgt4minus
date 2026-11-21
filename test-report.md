# Test Review — phase-1-core

## Summary
Phase verify `cd taskboard && python -m pytest -q tests` passed. The rechecked API test is substantive and covers the deferred invalid-input contract and invalid-write isolation findings.

## Per-requirement results
### API validation and invalid-write isolation — PASS
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed
- Notes: The test uses the configured TestClient to exercise real API behavior, asserts rejection of invalid writes with the documented 400/error contract, and checks rejected data is not persisted.
- Evidence: {"file": "taskboard/tests/test_api.py", "line": 91, "excerpt": "assert client.patch(f\"/api/tasks/{task['id']}\", json={}).status_code == 400"}
- Evidence: {"file": "taskboard/tests/test_api.py", "line": 29, "excerpt": "assert health.headers[\"content-type\"].startswith(\"application/json\")"}
- Evidence: {"file": "taskboard/tests/test_api.py", "line": 74, "excerpt": "assert tasks.status_code == 200"}

## Overall assessment
All checked API findings are covered by real assertions and the phase verification is green. No repair is required for `taskboard/tests/test_api.py`.
