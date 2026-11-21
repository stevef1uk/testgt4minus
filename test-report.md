# Test Review — phase-1-core

## Summary
Phase verify command was executed; requirement-level review follows.

## phase-1-core
### phase-1-core
Requirement: Persist projects and tasks in SQLite and expose the repository operations specified by the store contract.
Level: unit
Test file: taskboard/tests/test_repository.py
Bead ID: tm-ns3
Phase: phase-1-core
Scenarios:
- Initialize an isolated database, create a project, and list and retrieve it with its tasks.
- Create, update, list, and delete tasks, including filtering by project and status and deleting a project with its tasks.
- Verify empty results, missing identifiers, invalid status values, and parameterized persistence across a reopened connection.
Assertions:
- Returned records contain the contract fields and preserve task status, priority/position, descriptions, and timestamps.
- Mutations affect only the addressed project/task; missing records produce the repository's specified not-found result and invalid values are rejected.
- Schema initialization is idempotent and foreign-key cascade behavior is enforced.

- Test file: `taskboard/tests/test_repository.py` — exists=True; substantive_assertions=True
