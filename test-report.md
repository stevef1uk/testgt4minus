# Test Review — phase-1-app

## Summary
The complete phase verification command `cd taskboard && python -m pytest -q tests` passed with 16 tests, but the deferred API finding is not repaired. The API test file contains substantive assertions, yet its validation assertions contradict the SPEC-required application error contract and accept an overlong description.

## Per-requirement results
### phase-1-app — FAIL
- Test file: taskboard/tests/test_api.py
- Verify result: pytest passed (`16 passed`)
- Notes: The test does not assert that an overlong description returns HTTP 400 with `{"error": ...}`. It instead expects a 201 response and persists the 2001-character description. The missing-project and validation checks assert FastAPI `detail` responses, not the SPEC-required application-level `error` object. The test also does not verify that rejected writes leave persisted state unchanged.

- Evidence: {"file":"taskboard/tests/test_api.py","line":111,"excerpt":"assert missing.json() == {\"detail\": \"project not found\"}"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":129,"excerpt":"assert response.status_code == 422"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":137,"excerpt":"assert preserved.status_code == 201"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":138,"excerpt":"assert preserved.json()[\"description\"] == \"x\" * 2001"}

## Overall assessment
FAIL. Implementation repair: taskboard/tests/test_api.py — the test contract currently accepts the invalid 2001-character description and checks undocumented `detail` errors. Reopen bead tm-ssd, add assertions for the SPEC-required HTTP 400 `{"error": ...}` responses and verify invalid writes do not create or partially update records, then rerun the phase gate.
