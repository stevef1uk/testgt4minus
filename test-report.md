# Test Review — phase-1-core

## Summary
Partial tests pass; phase verify result could not establish complete phase coverage. The repository test file still contains only the original four tests and does not cover all planned phase-1-core scenarios from the prior finding.

## Per-requirement results

### Schema/index behavior — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: phase verify is not sufficient evidence of coverage.
- Notes: `test_schema_is_idempotent_and_empty` checks idempotent initialization and empty repository results, but it does not assert the required schema/index definitions.

### Foreign keys — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: incomplete coverage.
- Notes: `test_project_delete_cascades_tasks` exercises repository-level cascade behavior, but there is no direct assertion that foreign-key enforcement is enabled or that invalid task project references are rejected.

### busy_timeout=5000 — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: incomplete coverage.
- Notes: No test inspects the connection PRAGMA or verifies the configured timeout.

### Validation and length/Unicode rules — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: incomplete coverage.
- Notes: The tests use ordinary short ASCII values and do not assert accepted/rejected validation boundaries, maximum lengths, or Unicode handling.

### Explicit UTC timestamps — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: incomplete coverage.
- Notes: `test_projects_and_tasks_have_defaults_and_ascending_ids` only checks that a task timestamp contains `T`; it does not assert explicit UTC offset/format for created and updated timestamps.

### Separate-connection persistence — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: incomplete coverage.
- Notes: All operations use the repository fixtures and no test opens a separate connection to verify committed persistence.

### Parameterized writes — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: incomplete coverage.
- Notes: No assertion or recorder verifies that create/update/delete writes use parameterized SQL rather than interpolated values.

### Missing-resource results — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: incomplete coverage.
- Notes: The only missing-resource assertion is `tasks.delete_task(task["id"]) is False` after a cascade; missing create/update/list resource cases are not covered.

## Overall assessment
FAIL. Test repair: taskboard/tests/test_repository.py — bead tm-ns3. Strengthen the test file with substantive assertions for every scenario above, include exact line evidence for each repaired assertion, and rerun `cd taskboard && python -m pytest -q tests/test_repository.py`.
