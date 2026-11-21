# Test Review — phase-1-app

## Summary
The phase verify passed (`14 passed`), but the planned API coverage is incomplete. The deferred finding for `taskboard/tests/test_api.py` remains unresolved.

## Per-requirement results

### phase-1-app — FAIL
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed (`14 passed, 1 warning`)
- Evidence: {"file":"taskboard/tests/test_api.py","line":15,"excerpt":"assert response.status_code == 200"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":117,"excerpt":"assert deleted_task.content == b\"\""}
- Notes: The file has real TestClient assertions for health, empty projects, project/task creation, ordering, partial patch preservation, missing resources, and bodyless 204 deletes. However, it does not assert root HTML or canonical static responses, response content types, documented `{\"error\": ...}` objects, a malformed-integer path returning exactly 422, the invalid status/priority/overlong title/description cases, composed status-and-priority API filters, or project-delete cascade behavior through the API. The broad assertion at line 101 (`assert response.status_code in {400, 404, 422}`) does not verify the documented status for each case and does not cover the missing cases.

## Overall assessment
FAIL. Reopen owning bead `tm-j2d` for test repair. `taskboard/tests/test_api.py` needs substantive assertions for root/static responses, error objects, malformed-integer 422, invalid field cases, composed filters, cascade behavior, and content types. Re-run `cd taskboard && python -m pytest -q tests` after repair.
