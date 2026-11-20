# Test Review — Phase 1 core/app

## Summary
Phase verification passed, but the TEST_PLAN.md active app row requires plan correction and additional assertions before approval.

## Per-requirement results
### phase-1-core — PASS
- Test file: taskboard/tests/test_repository.py
- Verify result: `16 passed`
- Notes: The file exists and contains substantive assertions for schema initialization, project/task persistence, ordering, filtering, partial updates, cascade deletion, validation, and parameterized special-character values.

### phase-1-app — FAIL pending plan correction
- Test file: taskboard/tests/test_api.py
- Verify result: `16 passed`
- Notes: The plan scenario requests project update behavior, but SPEC defines no project update route. The plan also claims isolation plus visible heading/form assertions that the current API tests do not cover.

## Overall assessment
The pytest gate is green, but the active TEST_PLAN.md app requirement is not an accurate acceptance plan. Rewrite it to remove unsupported project-update behavior, align with the documented project routes, and explicitly map tests for database isolation and the required visible heading/project form.
