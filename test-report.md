# Test Review — phase-1-core

## Summary
Partial coverage; phase verify passed, but the repaired API test still asserts the wrong SPEC contract and repository negative tests do not prove invalid-write isolation.

## Per-requirement results

### phase-1-core — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: passed — 7 passed, 1 warning.
- Notes: The file now contains real boundary and enum assertions: 80/81 project names, 120/121 titles, 1000/1001 descriptions, and invalid status/priority. However, the negative cases only assert `ValueError`; they do not assert that the rejected attempts leave the repository unchanged, which is an assertion required by the plan and architecture.
- Evidence: {"file":"taskboard/tests/test_repository.py","line":89,"excerpt":"tasks.create_task(boundary_project[\"id\"], \"x\" * 121)"}
- Evidence: {"file":"taskboard/tests/test_repository.py","line":97,"excerpt":"tasks.create_task(boundary_project[\"id\"], \"Task\", priority=\"invalid\")"}

### phase-1-app — FAIL (deferred from the active phase gate)
- Test file: taskboard/tests/test_api.py
- Verify result: not part of the active phase-1-core verify command.
- Notes: The repaired API scenarios remain incorrect against SPEC. The 2001-character description is accepted with status 201 instead of being required to return 400 with a decoded `{\"error\": ...}` object, and the test asserts undocumented `detail` responses for missing resources and validation instead of the required application error object. It also does not verify that the rejected write is absent from a subsequent GET.
- Evidence: {"file":"taskboard/tests/test_api.py","line":137,"excerpt":"assert preserved.status_code == 201"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":138,"excerpt":"assert preserved.json()[\"description\"] == \"x\" * 2001"}

## Overall assessment
FAIL. Reopen tm-ns3 for Test repair: taskboard/tests/test_repository.py — add explicit post-rejection repository-state assertions for the overlong project name, overlong title/description, and invalid status/priority cases. Reopen tm-ssd for Implementation repair: taskboard/tests/test_api.py — replace the 2001-character acceptance and undocumented `detail` assertions with SPEC-required HTTP 400 and `{\"error\": ...}` checks, then assert invalid writes are absent from subsequent GET responses. The phase-1-core repository gate is green, but the repaired findings are not fully covered.
