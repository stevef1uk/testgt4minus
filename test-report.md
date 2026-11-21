# Test Review — phase-1 app/core

## Summary
Phase verification passed (`15 passed`), but the repaired API test file still lacks substantive coverage for the reported API findings. This is a failure requiring implementation-bead repair, not a plan or architecture failure.

## Per-requirement results

### phase-1-app — FAIL
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed (`cd taskboard && python -m pytest -q tests`; 15 passed)
- Notes: Root/static response and some content-type assertions exist, but the file does not test the required JavaScript asset response, nonempty root/static bodies, or runtime-database isolation. The invalid-create parametrization only asserts a broad status set (`{400, 404, 422}`), so it does not prove documented error objects or the specific invalid status, invalid priority, overlong title, or overlong description cases. There is no malformed-integer path assertion for exact 422 behavior. There is no composed status+priority API filter assertion, no project-delete cascade assertion through the API, and no task JSON content-type assertion.

- Evidence: {"file":"taskboard/tests/test_api.py","line":116,"excerpt":"assert response.status_code in {400, 404, 422}"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":21,"excerpt":"assert static.headers[\"content-type\"].startswith(\"text/css\")"}

### phase-1-core — DEFERRED
- Test file: `taskboard/tests/test_repository.py`
- Notes: The deferred `tm-ns3` repository finding is outside this re-review's requested in-scope file check.

## Overall assessment
FAIL. Reopen `tm-j2d` for `taskboard/tests/test_api.py` and add real assertions covering root/static bodies and both asset content types, documented error objects, malformed-integer 422 behavior, each invalid status/priority/overlong title/description case, composed API filters, project-delete cascade, relevant JSON content types, and runtime-db isolation. Re-run `cd taskboard && python -m pytest -q tests`. The plan and SPEC/architecture are consistent; this is a test repair.
