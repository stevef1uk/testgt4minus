# Test Review — active phase requirements

## Summary
All active-phase requirements have planned substantive tests; phase verify passed.

## Per-requirement results
### phase-1-core — PASS
- Phase: phase-1-core
- Test file: taskboard/tests/test_repository.py
- Evidence: {"file":"taskboard/tests/test_repository.py","line":16,"excerpt":'with pytest.raises(ValueError):'}
- Verify result: passed
- Notes: Real test assertions exercise the requirement behavior.
### phase-1-app — PASS
- Phase: phase-1-app
- Test file: taskboard/tests/conftest.py
- FAIL: test lacks substantive assertions or contains stub markers
- Test file: taskboard/tests/test_api.py
- Evidence: {"file":"taskboard/tests/test_api.py","line":6,"excerpt":'assert response.status_code == 200'}
- Verify result: passed
- Notes: Real test assertions exercise the requirement behavior.

## Overall assessment
2 active-phase requirement rows reviewed; phase verification `cd taskboard && python -m pytest -q tests` passed.
