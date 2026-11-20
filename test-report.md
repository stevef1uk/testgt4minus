# Test Review — phase-1 core/application

## Summary
Partial tests pass; the configured phase verify passed, but the repaired API test remains incomplete for several reported findings.

## Per-requirement results
### phase-1-core — PASS
- Test file: taskboard/tests/test_repository.py
- Verify result: passed — 11 passed, 1 warning
- Notes: Repository tests are substantive and cover schema setup, persistence, ordering, filtering, updates, validation, cascade deletion, field shapes, and an explicit UTC offset.
- Evidence: {"file":"taskboard/tests/test_repository.py","line":44,"excerpt":"assert created_at.utcoffset() == timezone.utc.utcoffset(created_at)"}

### phase-1-app — FAIL
- Test file: taskboard/tests/test_api.py
- Verify result: phase repository verify passed, but API coverage review failed
- Notes: The test file exists and has real assertions, but it does not reject an overlong project name, does not assert multiple projects are returned in ascending-ID order, and does not assert the rendered root contains the visible `TaskBoard` heading or project form. It checks the HTML content type, but does not assert the canonical JavaScript and CSS content types.
- Evidence: {"file":"taskboard/tests/test_api.py","line":13,"excerpt":"assert \"text/html\" in response.headers[\"content-type\"]"}

## Overall assessment
FAIL. Test repair: taskboard/tests/test_api.py — add real assertions for overlong project-name rejection, multi-project ascending-ID ordering, the visible TaskBoard heading, the project form, and canonical content types for both static assets; reopen owning bead te-c2c. The repository repair is adequate, including explicit UTC-offset coverage; no repository test repair is required.
