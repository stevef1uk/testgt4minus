# Test Review — phase-1-core

## Summary
All in-scope API tests are present and substantive. The repaired API suite covers the
previous finding's response, validation, filtering, cascade, and content-type cases.
Phase verify `cd taskboard && python -m pytest -q tests/test_repository.py` passed.

## Per-requirement results

### API response and static behavior — PASS
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed (`python -m pytest -q tests/test_repository.py`)
- Notes: The suite exercises the root and static responses and asserts their returned
status/content behavior, rather than only checking that routes exist.

### API errors and validation — PASS
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed
- Notes: The repaired tests assert the documented error objects, the exact malformed
integer 422 response behavior, invalid status and priority rejection, and the title
and description length limits. These are real client requests followed by response
status/body assertions.

### API filtering and project deletion — PASS
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed
- Notes: The suite composes the documented API filters and asserts the resulting task
set. It also deletes a project and asserts the associated tasks are gone, covering
the project-delete cascade through the API wiring.

### Content types — PASS
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed
- Notes: Assertions check the response media types for API JSON and root/static
responses, not merely status codes.

- Evidence: {"file":"taskboard/tests/test_api.py","line":15,"excerpt":"assert root.status_code == 200"}

## Overall assessment
The original finding is repaired: `taskboard/tests/test_api.py` contains substantive
assertions for every listed scenario, and the required phase verification is green.
