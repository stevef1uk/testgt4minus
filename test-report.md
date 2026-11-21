# Test Review — phase-1 app/core

## Summary
The phase verification passes (16 tests), but the repaired API test remains inadequate for the original finding. The invalid enum cases still assert undocumented `detail` objects instead of the SPEC-required `{"error": ...}` contract, and the composed-filter assertion expects all three tasks rather than the AND-filtered result. The overlong-description and invalid-write-isolation cases are substantively covered.

## Per-requirement results

### phase-1-core — PASS
- Test file: taskboard/tests/test_repository.py
- Verify result: passed as part of `cd taskboard && python -m pytest -q tests`
- Notes: The repository test asserts the 80/81 project-name boundary, 120/121 task-title boundary, 1000/1001 description boundary, and invalid status/priority rejection with real repository state checks.

### phase-1-app — FAIL
- Test file: taskboard/tests/test_api.py
- Verify result: pytest passed with 16 tests, but adequacy review failed.
- Notes: The test has real assertions for the overlong description, invalid create isolation, and invalid patch isolation. However, invalid status and priority still expect `{"detail": ...}` rather than asserting the SPEC-required 400 `{"error": ...}` response. The filter test also does not assert AND behavior because it expects all three records despite requesting `status=todo` and `priority=high`.

- Evidence: {"file":"taskboard/tests/test_api.py","line":118,"excerpt":"({"title": "bad", "description": "x" * 1001}, {"error": "description: String should have at most 1000 characters"}),"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":124,"excerpt":"assert response.json() == expected"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":125,"excerpt":"assert client.get(f\"/api/projects/{project_id}/tasks\").json() == before"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":138,"excerpt":"assert invalid_patch.status_code == 400"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":142,"excerpt":"assert client.get(f\"/api/projects/{project_id}/tasks\").json() == before_patch"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":114,"excerpt":"({"title": "bad", "status": "invalid"}, {"detail": "invalid status"}),"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":115,"excerpt":"({"title": "bad", "priority": "invalid"}, {"detail": "invalid priority"}),"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":159,"excerpt":"assert [task[\"title\"] for task in filtered.json()] == [\"todo-high\", \"todo-low\", \"done-high\"]"}

## Overall assessment
Failure. Test repair: taskboard/tests/test_api.py — replace the invalid enum `detail` expectations with explicit SPEC-compliant 400 `{"error": ...}` assertions and correct the composed-filter assertion to prove AND behavior. Reopen implementation/test bead tm-ssd and rerun the full phase verification.
