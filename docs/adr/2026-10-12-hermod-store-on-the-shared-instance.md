# ADR-026: Hermod's Project Store Is a Second Database on the Store's Instance

**Date**: 2026-10-12

**Status**: Accepted

**Extends**: ADR-023 (*The Overlay Storage-Backend Seam*), and resolves a question the `munnin-deploy` Postgres plan left as "later".

---

## Problem

Three records disagreed about where the overlay's project-keyed data lives, and the newest one asserted over the oldest without saying so.

- **2026-08-07** (`plans/completed/2026-08-07-agent-memory-ops-to-hermod-boundary.md`) settled *store ≠ server*: Valaskjalf is the storage base and *"holds ALL memory data"*, Munnin is the project-blind memory server, and Hermod is a **peer accessor of Valaskjalf** owning project-context and orientation-map. Under the markdown backend that was literal: both servers read `@agent-memory`.
- **2026-10-09** (`munnin-deploy`, the Postgres plan) moved the memory store to PostgreSQL and left Hermod's store in its decision table as *"a second database on the same instance, later"*.
- **2026-10-12** (ADR-024) built Hermod's project store and implemented it as a **local SQLite file**, with `storage-backends/db.md` describing that as the design: *"The store is a local file."*

Nothing recorded that the 2026-08-07 frame had stopped applying, so Hermod was left owning project-keyed data in a third place — not the markdown tree, and not the instance the fleet had just moved its store to. The cost is concrete: the project store had no dump and no home on the box the fleet backs up.

## Decision

**We decided to**: give Hermod a PostgreSQL backend for its project store and point the deployment at **a second database on the same instance**, reached by Hermod's own DSN, with the SQLite implementation kept for local runs and tests.

- One project store, one engine in the deployment, one instance: the instance the memory store already runs on, being *"one engine and one box"*, which is the record's own phrasing.
- **Not a schema inside the memory database.** Two stores in one database means two migration runners writing one `migration_history` table, and the alternative resolution — the memory core's migration list carrying the overlay's two tables — puts the overlay's data model inside the memory server, which is the boundary ADR-012 drew and ADR-023 seamed.
- **Not a second Postgres server.** A second instance would be a second failure domain and a second thing to provision, back up and monitor, for a store that holds one row per theme.
- The backend is a **setting, not a rewrite**: both implementations satisfy the existing `ProjectRepository` Protocol, and one contract test runs against both engines, so a behaviour that diverges is a failing test.

The 2026-08-07 frame is **narrowed, not reversed**: Valaskjalf remains the memory store, and Hermod remains a peer rather than a subordinate — it just keeps its project-keyed rows in a sibling database on the same instance instead of inside the memory store.

## What to Build (Requirements)

- `hermod-server`: `PostgresProjectRepository` behind the existing Protocol, `postgres_migrations.py` (its own runner and history table, mirroring the SQLite runner's discipline), and `migrations_postgres/0001_init.sql`. Dates stay TEXT (ISO-8601) and tags a JSON array in TEXT, matching the entities and the SQLite rows exactly, as the memory store's Postgres schema chose for the same reason.
- Config grows `db_backend` and `db_url`, with an unknown backend refused at startup rather than silently read as SQLite, and a Postgres backend without a DSN refused for the same reason.
- `tests/test_store_backends.py`: one contract, parametrized over both engines; the Postgres parameter is marked and skips without `HERMOD_PG_TEST_URL`, so the default suite needs no service.
- `hermod-deploy`: `HERMOD_DB_BACKEND=postgres`, a `HERMOD_DB_URL` secret written into `.kamal/secrets` by the deploy workflow, and the database created on the instance. The `hermod-data` volume stays, because the SQLite file is the rollback, exactly as the memory store keeps its own.
- `storage-backends/db.md` stops naming an engine, because the op list was never engine-specific: every op is a tool call, and the project is an argument rather than a path.

**Success Criteria:**
- The SQLite suite is unchanged and green without a service; the same contract passes against a real PostgreSQL with `HERMOD_PG_TEST_URL` set.
- A fresh database needs no separate step: the schema applies on the store's first connection.
- `HERMOD_DB_BACKEND=postgres` with no DSN refuses to start, and an unknown value refuses to start.

## Alternatives Rejected

- **Keep SQLite permanently.** Leaves project-keyed data on a volume with no dump, and contradicts the store location the fleet's own record expects of it.
- **A schema inside the memory database.** The shared `migration_history` table above; and it inverts the boundary either way it is resolved.
- **A separate PostgreSQL instance.** A second service for a store this small, with a second backup target and a second thing to keep patched.
- **Store project context as records in the memory tables.** Project memory is not memory records: the memory store's importer already excludes project-scoped knowledge by design, which is the same line drawn from the other side.
- **Write a data migration first.** There is nothing to migrate: the store has never run in production.

---

**Full context**: the store-location question was raised while deploying Hermod (`hermod-deploy`), whose `config/deploy.yml` carried the SQLite volume until this decision.
