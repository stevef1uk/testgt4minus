# Test Review — Phase 1 (phase-1-core, phase-1-app)

## Summary
Phase verify `cd taskboard && python -m pytest -q tests` PASSED (16 passed, 0 failed).
Both planned active-phase test files exist with substantive (non-stub) assertions.
However, a live probe against the delivered app shows production behavior violating
SPEC sections 4 and 6 in cases the green tests do not cover, and several planned
assertions are missing or weak. Outcome: failure (tests weak/missing + production
violations found by probe).

## Per-requirement results

### phase-1-core (bead tm-ns3, test_repository.py) — PASS with one gap
- Test file: taskboard/tests/test_repository.py (exists, real assertions)
- Verify result: passed
- Notes: asserts idempotent schema, FK cascade, 80/120/1000 character boundaries with
  over-limit rejection, unknown status and priority ValueError, trim (" Alpha " becomes
  "Alpha"), +00:00 timestamps, ascending IDs, combined AND filter, cascade delete, and
  parameterized writes. Gap vs plan: partial-update test patches only the title field;
  the plan scenario "Patch each supported task field while preserving omitted fields"
  requires patching description, priority, and status too.

### phase-1-app (bead tm-rmz, test_api.py) — FAIL (gaps below; verify itself passed)
1. Whitespace-only project name: POST with name of three spaces returns 201 and
   persists an empty name (probe-verified). Violates SPEC section 4 "Trim surrounding
   whitespace for project name... Reject empty values after trim." No test covers this;
   current tests only post a truly empty name (400 via pydantic). Production fix needed
   in main.py create_project: validate after strip and return the 400 error object.
2. API timestamps are naive: probe returned created_at and updated_at as
   "2026-11-22 16:31:59" — no "T", no UTC offset. Violates SPEC section 4 "All
   timestamps have explicit UTC timezone (Z or +00:00)." test_api.py assert_timestamp
   (lines 14-16) only calls datetime.fromisoformat, which accepts naive strings —
   weaker than test_repository.py's endswith("+00:00") assertion. Root cause: main.py
   defines its own DDL and SQL with CURRENT_TIMESTAMP defaults instead of using
   db.py and repository.py (also misses busy_timeout 5000). Bead tm-lro owns main.py.
3. Plan row tm-rmz asserts the root HTML contains the TaskBoard heading, project
   creation form controls, and empty-state container. test_root_static_and_api_content_types
   only checks "TaskBoard" in root.text — the handler's placeholder fallback would also
   pass. No assertion covers the form controls or empty-state container.
4. Plan scenario "missing-project delete errors": DELETE of a missing project id (404
   with error object) is not tested anywhere in test_api.py.

Deferred (out of scope): phase-2 test_ui_content.py, phase-3 Playwright suite.

## Overall assessment
FAIL — rewind Polecat to implementation. Reopen beads:
- tm-lro (main.py): reject empty-after-trim project names with 400 error object; emit
  explicit-UTC ISO-8601 timestamps by delegating to db.py and repository.py; add
  busy_timeout 5000.
- tm-rmz (test_api.py): assert UTC offsets on API timestamps; add whitespace-only-name
  400 plus non-persistence check; assert root HTML form controls and empty-state
  container; add missing-project delete 404 test.
- tm-ns3 (test_repository.py): extend partial-update test to patch description,
  priority, and status with omitted fields preserved.
Repository boundary tests in test_repository.py themselves passed.
