# Test Review — Phase 1

## Summary
Tests execute successfully (16 passed), but phase verification is insufficient for the active requirements. The planned tests exist and contain real assertions, yet key SPEC boundary and error-contract assertions are missing or inverted.

## Per-requirement results

### phase-1-core — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: passed — 16 passed, 1 warning
- Notes: The repository suite exercises persistence, filtering, updates, cascade deletion, timestamps, and schema settings, but it does not cover the planned/SPEC-required boundaries. It tests 201-character project names and titles rather than the specified 81/121-character limits, and it has no assertions for the 80/120-character accepted boundaries, 1000/1001-character descriptions, or unknown status/priority rejection.

### phase-1-app — FAIL
- Test file: taskboard/tests/test_api.py
- Verify result: passed — 16 passed, 1 warning
- Notes: The API suite has substantive route assertions, but its validation/error coverage conflicts with the SPEC. It expects a 200/201 response for a 2001-character description instead of asserting rejection at 1001 characters, and it asserts `{"detail": ...}` for a documented application error that must be `{"error": ...}`. The suite therefore cannot establish the required API contract or invalid-write non-persistence.

## Overall assessment
FAIL. Reopen tm-ns3 for Test repair: taskboard/tests/test_repository.py — add exact 80/81 project-name, 120/121 task-title, 1000/1001 description, and invalid status/priority assertions, including valid boundary persistence. Reopen tm-ssd for Implementation repair: taskboard/tests/test_api.py — correct the API validation/error assertions and implementation behavior so overlong descriptions return the documented 400 `{"error": ...}` object and invalid writes are absent from subsequent reads. Re-run the exact phase gate afterward.
