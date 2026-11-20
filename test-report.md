# Test Review — phase-1-app

## Summary
No: the repaired API test file still lacks the requested coverage, and the configured phase verify fails because its path does not exist from `taskboard/`.

## Per-requirement results

### phase-1-core — PASS
- Test file: taskboard/tests/test_repository.py
- Verify result: failed to collect the configured path; the repository suite itself passes when invoked as `python -m pytest -q tests/test_repository.py` from `taskboard/`.
- Notes: The existing repository assertions cover overlong model rejection, ascending IDs, idempotent persistence, and UTC offsets. The UTC offset assertion is adequate.
- Evidence: {"file":"taskboard/tests/test_repository.py","line":44,"excerpt":"assert created_at.utcoffset() == timezone.utc.utcoffset(created_at)"}

### phase-1-app — FAIL
- Test file: taskboard/tests/test_api.py
- Verify result: failed — `cd taskboard && python -m pytest -q taskboard/tests/test_repository.py` reports `file or directory not found`.
- Notes: `test_api.py` has no assertion for overlong project-name API rejection, no multi-project ascending-ID list assertion, no visible `TaskBoard` heading assertion, no project-form assertion, and no canonical `application/javascript` / `text/css` content-type assertions. Its existing static test only checks status and nonempty bytes.
- Test repair: taskboard/tests/test_api.py — add real API assertions for all five requested scenarios and correct the planned invalid-name status to the SPEC's 400 application error (the plan currently says 422, which is not the documented project-name API contract).
- Evidence: {"file":"taskboard/tests/test_api.py","line":13,"excerpt":"assert \"text/html\" in response.headers[\"content-type\"]"}

## Overall assessment
FAIL. Reopen te-c2c for test repair. The configured repository verification command must also be corrected or aligned with the actual repository test path before approval; no source implementation change is indicated by this test-coverage finding.
