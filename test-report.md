# Test Review — phase-1-core

## Summary
Partial tests pass; phase verify passed, but the active phase requirement is not adequately covered.

## Per-requirement results
### phase-1-core — FAIL
- Test file: taskboard/tests/test_repository.py
- Verify result: passed (`4 passed in 0.01s`)
- Notes: The file contains real assertions for basic idempotent initialization, project/task creation, filtering, partial update preservation, and cascade deletion. However, it does not assert several planned and SPEC-required foundation behaviors: schema/index presence, `foreign_keys` and `busy_timeout=5000`, validation/mapping and length/Unicode rules, explicit UTC timezone offsets, persistence across separate repository connections, parameterized-write behavior, or missing project/task not-found results. The four tests also use unsupported `priority` assertions in the current SPEC contract's phase-1-core test requirements.

## Overall assessment
FAIL. Repair the active repository coverage in taskboard/tests/test_repository.py under bead tm-ns3, adding substantive assertions for every planned phase-1-core scenario, then rerun the configured phase verification.
