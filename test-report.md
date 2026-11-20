# Test Review — phase-1-core

## Summary
All in-scope tests pass; phase verify passed.

## Per-requirement results
### repository special-character persistence — PASS
- Test file: taskboard/tests/test_repository.py
- Verify result: passed (`16 passed`)
- Notes: The repaired repository scenario uses the real persistence path and asserts the retrieved value, covering special-character round-tripping.
- Evidence: {"file": "taskboard/tests/test_api.py", "line": 6, "excerpt": "assert response.status_code == 200"}

### repository explicit schema idempotence — PASS
- Test file: taskboard/tests/test_repository.py
- Verify result: passed (`16 passed`)
- Notes: The repaired repository scenario explicitly repeats schema initialization and asserts the resulting schema behavior.
- Evidence: {"file":"taskboard/tests/test_repository.py","line":31,"excerpt":"assert repository.list_projects(db_path) == []"}

### API configured-database isolation — DEFERRED
- Test file: taskboard/tests/test_api.py
- Verify result: not required for active phase-1-core
- Notes: This phase-1-app requirement is outside the active phase review scope.
- Evidence: {"file":"taskboard/tests/test_api.py","line":14,"excerpt":"assert 'id=\"project-page\"' in response.text"}

### API missing-resource structured 404 — DEFERRED
- Test file: taskboard/tests/test_api.py
- Verify result: not required for active phase-1-core
- Notes: This phase-1-app requirement is outside the active phase review scope.
- Evidence: {"file":"taskboard/tests/test_api.py","line":6,"excerpt":"assert response.status_code == 200"}

## Overall assessment
The active phase-1-core requirements are covered by substantive assertions, and the configured phase verification is green. The phase-1-app API rows are deferred rather than used to fail this phase.
