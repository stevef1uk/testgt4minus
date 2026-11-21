# Test Review — phase-1-core

## Summary
Phase verify passed (`python -m pytest -q tests`).

## In-scope finding review
### taskboard/tests/test_api.py — PASS/FAIL pending evidence
- maximum description boundary: `taskboard/tests/test_api.py:135`
- Evidence: {"file":"taskboard/tests/test_api.py","line":135,"excerpt":'        json={"title": "Long description", "description": "x" * 2001},'}
- SPEC error response: no matching assertion found.
- HTTP 400 assertion: `taskboard/tests/test_api.py:91`
- Evidence: {"file":"taskboard/tests/test_api.py","line":91,"excerpt":'    assert client.patch(f"/api/tasks/{task[\'id\']}", json={}).status_code == 400'}

## Verify output
```
................                                                         [100%]
=============================== warnings summary ===============================
../.venv/lib/python3.11/site-packages/fastapi/testclient.py:1
  /home/stevef/gt/testgt4m/mayor/rig/.venv/lib/python3.11/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 0.19s
```

## Overall assessment
FAIL: the API test does not visibly cover every deferred contract finding.
