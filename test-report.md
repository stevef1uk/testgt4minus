# Test Review — Foundation and projects (phase-1-core, phase-1-app)

## Summary
All active-phase tests pass; phase verify passed (`23 passed, 1 warning`).

## Per-requirement results

### phase-1-core — PASS
- Test file: `taskboard/tests/test_repository.py`
- Verify result: passed
- Notes: Repository tests exercise schema initialization, empty/idempotent databases, project/task persistence, ascending ordering, status/priority filters, partial updates preserving omitted fields, validation, and cascade deletion with real SQLite state.
- Evidence: {"file":"taskboard/tests/test_repository.py","line":31,"excerpt":"assert repository.list_projects(db_path) == []"}
- Evidence: {"file":"taskboard/tests/test_repository.py","line":65,"excerpt":"assert repository.list_tasks(project[\"id\"], status=\"doing\", db_path=db_path) == [second]"}
- Evidence: {"file":"taskboard/tests/test_repository.py","line":88,"excerpt":"assert updated[\"description\"] == \"keep\""}
- Evidence: {"file":"taskboard/tests/test_repository.py","line":98,"excerpt":"assert repository.list_tasks(project[\"id\"], db_path=db_path) == []"}

### phase-1-app — PASS
- Test file: `taskboard/tests/test_api.py`
- Verify result: passed
- Notes: API integration tests use isolated configured applications and TestClient, asserting exact health JSON, project CRUD/statuses, structured errors, database isolation, root HTML, and static asset delivery.
- Evidence: {"file":"taskboard/tests/test_api.py","line":7,"excerpt":"assert response.json() == {\"status\": \"ok\"}"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":63,"excerpt":"assert deleted.status_code == 204"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":89,"excerpt":"assert second_client.get(\"/api/projects\").json() == []"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":12,"excerpt":"assert response.status_code == 200"}
- Evidence: {"file":"taskboard/tests/test_api.py","line":22,"excerpt":"assert app_script.status_code == 200"}

## Deferred out-of-scope rows
- `phase-2` and `phase-3` are future phases and were not evaluated in this review.

## Overall assessment
All active-phase TEST_PLAN.md requirements have existing substantive tests, and the configured phase verification is green. No repair is required.
