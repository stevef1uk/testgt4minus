# Test Review — Phase 1 Foundation and projects

## Summary
Partial tests pass; phase verify `cd taskboard && python -m pytest -q tests` failed.

## Per-requirement results

### phase-1-core — PASS
- Test file: `taskboard/tests/test_repository.py`
- Verify result: failed overall (`3 failed, 20 passed`)
- Notes: The repository tests contain substantive assertions for persistence, ordering, filtering, partial updates, validation, special characters, timestamps, and cascade deletion.

### phase-1-app — FAIL
- Test file: `taskboard/tests/test_api.py`
- Verify result: failed. `test_task_api_create_list_patch_and_delete` expected PATCH 200 but received 404; `test_task_api_rejects_invalid_payloads_and_missing_resources` expected `{"error":"task not found"}` but received `{"detail":"Not Found"}`; `test_task_api_does_not_allow_project_mutation` expected 400 but received 404.
- Notes: The active app tests do cover health, project CRUD, isolated databases, root/static responses, and real assertions. However, the configured full-suite gate is not green. The root assertion in this file checks `id="project-page"` and static references rather than the planned `TaskBoard` heading and project form.

### phase-1-app fixture — PARTIAL
- Test file: `taskboard/tests/conftest.py`
- Verify result: fixture is exercised by the API tests, but the overall suite failed.
- Notes: The fixture creates an isolated temporary database and a real TestClient; teardown is provided by the context manager.

## Overall assessment
FAIL. The required phase verification is red. Implementation repair is required for the missing task PATCH/error handling currently exercised by `taskboard/tests/test_api.py`; reopen bead `te-hky`. The active app test also needs stronger root-content assertions for the planned heading and project-form requirement.
