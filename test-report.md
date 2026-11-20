# Test Review — Foundation and projects (phase-1-core, phase-1-app)

## Summary
Partial tests pass; the configured phase verify passed (`16 passed, 1 warning`).

## Per-requirement results

### phase-1-core — FAIL
- Test file: `taskboard/tests/test_repository.py`
- Verify result: passed
- Notes: The repository tests contain real assertions for persistence, ordering, filters, partial updates, validation, timestamps, and cascade deletion. However, the planned special-character persistence scenario is not exercised, and the test set does not directly verify the schema/index/foreign-key invariants required by the phase contract.

### phase-1-app — FAIL
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed
- Notes: The API tests contain real assertions for health, project CRUD, validation, 204/404 behavior, and static delivery. They do not test isolation between two separately configured app instances, and the root assertion checks only `id="project-page"` plus asset links rather than the required visible `TaskBoard` heading and project form.

## Overall assessment
The pytest gate is green, but active-phase planned coverage is incomplete. Reopen implementation beads `te-7yg` and `te-c2c`: strengthen `taskboard/tests/test_repository.py` with the planned special-character and schema/invariant assertions, and strengthen `taskboard/tests/test_api.py` with two-app database isolation plus explicit heading/form assertions. Re-run `cd taskboard && python -m pytest -q tests`.
