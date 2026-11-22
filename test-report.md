# Test Review — phase-1-core

## Summary
All active phase-1-core tests pass; phase verify passed. The prior evidence mismatch has been corrected: line 146 is the status-preservation assertion shown below.

## Per-requirement results

### phase-1-core — PASS
- Test file: `taskboard/tests/test_repository.py`
- Verify result: `cd taskboard && python -m pytest -q tests/test_repository.py` passed: 8 passed.
- Notes: The repository tests substantively cover idempotent schema initialization, project ordering, validation boundaries, defaults, UTC-offset timestamps, deterministic filtering, partial updates, invalid writes, parameterized persistence, and project-delete cascade.
- Evidence: {"file":"taskboard/tests/test_repository.py","line":146,"excerpt":" assert patched[\"status\"] == \"doing\""}

## Prior finding classification

Test repair: taskboard/tests/test_repository.py — no test repair is required; the test is substantive and line 146 is correctly quoted above. The prior review's evidence excerpt was incorrect, not the test.

## Overall assessment
PASS. Every in-scope phase-1-core requirement has a real assertion in the planned test file, and the configured phase verification is green.
