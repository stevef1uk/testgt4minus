# Test Review — phase-1

## Summary
Phase verification passed, but the active-phase test coverage is incomplete.

## Per-requirement results

### phase-1-core — FAIL
- Test file: `taskboard/tests/test_repository.py`
- Verify result: passed (`23 passed`)
- Notes: The suite covers basic persistence, ordering, filters, partial updates, timestamps, and cascade deletion, but it does not assert several planned/spec-required invariants: required tables, `foreign_keys`, `busy_timeout`, the `tasks.project_id` index, invalid descriptions/statuses/priorities, or the complete documented field/type contract.

### phase-1-app — FAIL
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed (`23 passed`)
- Notes: The suite covers health, basic project CRUD, isolation, task behavior, and asset reachability, but does not cover the planned overlong project-name case, project ordering with multiple projects, documented content requirements such as the `TaskBoard` heading and project form, or appropriate static content types. The root assertions only check an element ID and asset references.

## Overall assessment
The pytest gate is green, but the active phase requirements are not fully covered by substantive assertions. Strengthen the two planned test files and rerun the phase gate.
