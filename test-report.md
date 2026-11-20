# Test Review — Tasks and Kanban UI

## Summary

Phase verify passed for the configured pytest suite, but the planned phase-2 requirement is not covered by substantive tests.

## Per-requirement results

### phase-1-core — PASS
- Test file: `taskboard/tests/test_repository.py`
- Verify result: passed (`cd taskboard && python -m pytest -q tests`)
- Notes: Repository persistence, ordering, filters, partial updates, validation, special characters, and cascade deletion have real assertions.

### phase-1-app — PASS
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed (`cd taskboard && python -m pytest -q tests`)
- Notes: Health, project CRUD, structured errors, database isolation, root HTML, and static assets have real assertions.

### phase-2 — FAIL
- Test file: `taskboard/tests/test_api.py`
- Verify result: suite passed, but this does not establish phase-2 coverage.
- Notes: `test_api.py` contains no task-route assertions for task creation, listing, PATCH, deletion, invalid task payloads, missing task/project resources, or mutation protection. The phase-2 row's planned integration scenarios are therefore absent despite the file existing.

## Overall assessment

Test repair is required for the phase-2 API requirement. Add substantive API assertions to `taskboard/tests/test_api.py` for every planned task route and failure scenario, then rerun the configured pytest verification. Phase-3 remains deferred.
