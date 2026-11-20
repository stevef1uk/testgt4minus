# Test Review — phase-1-core / phase-1-app

## Summary
Partial coverage or verification failure; see per-requirement results.

## Per-requirement results
### overlong project-name rejection — FAIL
- Test file: taskboard/tests/test_api.py
- Verify result: failed
- Notes: No substantive assertion matching this requirement was found.
### ascending project-ID ordering — PASS
- Test file: taskboard/tests/test_api.py
- Verify result: failed
- Notes: Real API-client assertions cover the required returned behavior.
### visible TaskBoard heading — FAIL
- Test file: taskboard/tests/test_api.py
- Verify result: failed
- Notes: No substantive assertion matching this requirement was found.
### project form — FAIL
- Test file: taskboard/tests/test_api.py
- Verify result: failed
- Notes: No substantive assertion matching this requirement was found.
### canonical static content types — PASS
- Test file: taskboard/tests/test_api.py
- Verify result: failed
- Notes: Real API-client assertions cover the required returned behavior.
### explicit UTC timestamp offset — PASS
- Test file: taskboard/tests/test_repository.py
- Verify result: failed
- Notes: The repository test asserts the explicit zero UTC offset.

## Evidence
- Evidence: {"file":"taskboard/tests/test_repository.py","line":44,"excerpt":"assert created_at.utcoffset() == timezone.utc.utcoffset(created_at)"}

## Overall assessment
Coverage remains incomplete or the configured repository verification failed; reopen the corresponding test repair.
