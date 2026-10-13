# High Wizard Plan

## **PROJECT INFO**
- **Project**: agent-memory-project (owns the overlay, `db.md` and the family's ADRs; the code lands in `hermod-server`)
- **Date**: 2026-10-13
- **Agent**: meta
- **Theme**: Retarget Hermod's project store onto Valaskjalf's record tables (`shared_record` / `memory_record`), replacing the separate store ADR-026 put on its own database
- **Source Protocol**: `/high-wizard` — escalated from `/quick-wizard` (its Step 2 scope gate fired)

*CRITICAL INSTRUCTION: To continue this plan: load the source protocol above, then inspect which sections below are filled vs unfilled to infer your current step.*

---

## **INHERITED CONTEXT**

### From the Parent Plan
- **Parent plan**: None — not a sub-plan. Escalated from `/quick-wizard`, whose Step 1 collected the decisions recorded below.
- **Assigned scope**: N/A

### From Pre-Planning Discussion
- **Discussion**: Pre-planning discussion with Alvi, 2026-10-12/13 (the deploy session that produced `hermod-deploy`, ADR-025 and ADR-026)
- **Agreed scope**: Hermod's project memory moves out of its own store and into Valaskjalf's record tables, which the memory store already owns; the served ops keep their shape but read and write records instead of Hermod's two tables.

| # | Settled decision | Chosen | His reason | Status |
|---|------------------|--------|------------|--------|
| 1 | Where Hermod's project memory lives | Valaskjalf's `shared_record` / `memory_record`, not a table of its own | *"we don't need new project_context table. we should use memory_record instead"*, on the 2026-08-07 frame (*"Valaskjalf holds ALL memory data... both servers read/write it"*) and the `project` column already on both record tables | Settled |
| 2 | The orientation map | One `shared_record` row: `title` = `orientation-map`, `project` set, whole map as content | *"all good for orientation_map"*. A project has one map, so the title is the key and `create` refuses a second | Settled |
| 3 | Where an entry's description goes | A new `content_summary` column on **both** record tables | *"let's add new column instead. let's call it 'content_summary'... put the description in there"* | Settled — **landed**: `agent-memory-server` `0359d61`, migrations `0003` + `0002`, 545 tests green against PostgreSQL 17.11 |
| 4 | Entry key and summary source | `theme` becomes `title`; the summary is read from the column, never parsed out of the content | Follows from 3 | Settled |
| 5 | How a project row is identified | `record_type='knowledge'` with `project` set, to avoid a CHECK migration | He chose the no-schema-change option, *"yes, this one"* | **Invalidated by evidence after he chose it** — Munnin's own episodes and knowledge already carry `project` (728 of 770 episodes), so a naive filter hid real memory (9 test failures). Surfaced; this plan exists because of it. He re-affirmed it once the evidence was on the table. |
| 6 | Munnin's read paths | Add a `project IS NULL` filter | *"yes, Munnin should add project IS NULL filter"* | **Landed then reverted** — same evidence as 5. Nothing of it is in the tree. Resolved by decision 5 below. |

- **Considered and rejected**: adding `agent_id` to Hermod's own `project_context` (lost to `memory_record`, which already has it) · a `context` record type from the start (lost to "no schema change", and re-lost at the technical-core round) · deriving the summary from the content frontmatter (lost to a real column) · keeping Hermod's own Postgres database, which is ADR-026 itself (lost to Valaskjalf's tables)
- **Left open**: everything decisions 1-7 below settle.

---

## **OBJECTIVES**
Give Hermod's project-keyed memory one home instead of two: the records Valaskjalf already holds, with the same tenant resolution Munnin uses, so the same Google account sees the same data through either server. Remove the store ADR-026 built, and correct the two ADRs that describe it.

### **Related Documents**
- [ADR-024](docs/adr/2026-10-12-hermod-doc-extraction-and-hermod-server.md) - gives `hermod-server` its served form and the store it owns; the ownership clause is what this work reverses.
- [ADR-025](docs/adr/2026-10-12-hermod-auth-and-hosting.md) - the guarded hosted shape; its "Hermod has no tenancy" line is corrected here.
- [ADR-026](docs/adr/2026-10-12-hermod-store-on-the-shared-instance.md) - superseded: the store is not Hermod's own database, it is Valaskjalf's records.
- [storage-backends/db.md](storage-backends/db.md) - the store's op list, which gains the `agent` argument and loses its "local file" wording.
- [2026-08-07 boundary plan](plans/completed/2026-08-07-agent-memory-ops-to-hermod-boundary.md) - the frame this work returns to.

### **SUCCESS CRITERIA**
- [x] Hermod's served ops read and write `shared_record` and `memory_record`, filtered by `project`, and by `agent` for the private scope; `title` carries the theme and `content_summary` the summary
- [x] The tenant comes from the verified token's `(iss, sub)` read against `user_identity`, with no manually configured user id
- [x] All 167 markdown entries and 7 maps import with nothing lost, the former collisions now distinct rows because `memory_record` carries the agent
- [x] Munnin's knowledge reads exclude `project`-keyed rows; its episode, identity, reasoning and emotional reads are unchanged
- [ ] Hermod's own tables, database, volume and migration folders are gone, and `hermod-deploy` points at the memory database — **all but the volume**: no table, no migration folder, and no `hermod` database ever existed, and the DSN points at the memory database; the `hermod-data` volume is still on the host, unmounted
- [x] ADR-025 and ADR-026 corrected, `db.md` restated, and the reversal named in ADR-027
- [x] Green against PostgreSQL, which CI supplies as a service: the store has no second engine, so nothing shadows what is deployed

---

## **SCOPE**

### In Scope
- `hermod-server`: one record-backed repository replacing `SqliteProjectRepository` and `PostgresProjectRepository`, with both `migrations/` folders deleted
- The tenant resolver: `(iss, sub)` from the verified token read against Valaskjalf's `user_identity`, mirroring Munnin's resolver including its create-on-first-contact behaviour
- The `agent` argument across every op that touches the private scope, in `db.md` and in the tool signatures
- `content_summary` written by the importer from each entry's frontmatter description
- The importer retargeted to write records, with the stable uuid that keeps a re-run idempotent
- The import run itself against the live store, dry run first
- `hermod-deploy`: the DSN repointed at the memory database, the volume removed, and the `hermod` database dropped once the retarget is verified
- Corrections: ADR-025's tenancy line, ADR-026 superseded, `db.md` restated, ADR-027 written

### Out of Scope
- **The markdown tree is not deleted.** The store is a second copy until you decide otherwise.
- **The fleet roster and the general-knowledge directories.** They are not project context, and the importer's index-marker rule already excludes them.
- **Munnin's served surface.** The only change on its side is the read filter; no procedure, tool signature or prompt moves.
- **Munnin's importer refusing project-scoped directories.** It stays, now for the reason this work makes explicit: those rows are Hermod's to write.
- **The `title` / `theme` namespace sharing.** Recorded as latent, zero instances today, not fixed here.

---

## **CONFIRMED DECISIONS**
*Decisions made **by this plan**. Inherited ones live above.*

| # | Decision | Chosen | Reason |
|---|----------|--------|--------|
| 1 | How a project row is typed | `knowledge` with `project` set, no new type, no CHECK migration | His call, made twice and confirmed at the scope round: he would rather carry no schema change than a discriminator |
| 2 | What happens to ADR-026's store | Dropped once the retarget is verified: the two tables, the `hermod` database, the `hermod-data` volume and Hermod's migration folders | Nothing holds real data, and the schema is recreated on the first connection if needed again |
| 3 | What tells a project row from Munnin's project-scoped knowledge | Nothing, and that is accepted knowingly | Project-keyed ⇒ Hermod is the framework's rule, so a `knowledge` row with a `project` **is** project context. The residue is that `title` is one namespace for a theme and a display title; latent, zero instances today |
| 4 | How a private row names its agent | An explicit `agent` argument on every op that touches the private scope; `shared` ignores it | *"A ofc"*. Mirrors the markdown path, and a served client knows its own domain from its awakening. Changes `db.md`'s signatures |
| 5 | Where Munnin's `project IS NULL` filter lands | The **knowledge** reads only | Forced by the evidence: `§ select-project-episode` selects an episode *by project*, so episodes keep it, and a fleet-wide filter removed 728 of 770 episodes from Munnin's index |
| 6 | Schema ownership | Hermod issues no DDL and does no startup check; a missing table or column surfaces on the first store call | *"A, yes done it on Munnin's"*. One owner, one `migration_history`, and Hermod's migration folders go with decision 2 |
| 7 | How Hermod knows the tenant | Resolved from the verified token: `(iss, sub)` read against Valaskjalf's `user_identity`, creating a tenant on first contact exactly as Munnin does | *"get user data login from hermod from the valaskjalf... it directly loads the same user with munnin. DO NOT USE MANUAL CONFIG"*. So the token is a gate **and** an identity, and no manual config value exists |
| 8 | The shape with no login | The tenant always comes from the token; with no issuer configured, Hermod refuses to start rather than serving under a guessed account | Closed at the final review, after the question was raised and understood: *"just like Munnin, Hermod is used by I'm logging in to my google account."* The no-issuer shape is a development convenience, not a way it is used, so nothing is configured for it and nothing can drift. A silent empty store is therefore impossible. If that shape is ever wanted back, the one-line answer is to read the single account row out of the local store instead of being told it |
| 9 | Which engine Hermod's store code supports | **PostgreSQL only.** SQLite is removed from the repository, from the test fixture and from the tests, and CI supplies PostgreSQL as a service so the contract runs on every push | His call at the final review: *"Remove SQLite from Hermod"*, after the plan was found to still describe a local SQLite serving path that decision 8 had already removed. A second implementation of one contract that nothing deploys can drift with no consequence, and the CI service costs about ten lines. |
| 10 | How the offline importer names its tenant | `--iss` and `--sub`, resolved through the same `user_identity` mapping the server uses, **refusing an unmapped pair** | His call (option A). The importer has no token, and the same mechanism applied to a caller without one keeps decision 7 whole: no configured id, and it cannot import into a freshly created tenant by accident, which is a mistake that would take longest to notice. |

---

## **SOLUTION**

### Architecture Overview

One store, two accessors. Valaskjalf holds both corpora, and the boundary between them is expressed **in data** rather than in a table:

- **Munnin's**: rows with no `project`, plus every episode, identity, reasoning, emotional and RAS record.
- **Hermod's**: `record_type='knowledge'` rows that carry a `project`.

Hermod stops owning a database. It takes a DSN to Valaskjalf and a repository that reads and writes records, resolving the tenant from each verified token and taking the agent from the call.

### Component 1: The record repository (`hermod-server`)
- **Purpose**: satisfy the existing `ProjectRepository` Protocol over `shared_record` / `memory_record`, so nothing above the seam changes shape.
- **Key Files**: `src/hermod/data_repositories/record_project_repository.py` (new). Deleted: `sqlite_project_repository.py`, `postgres_project_repository.py`, `data_entities/migrations/`, `data_entities/migrations_postgres/`, `data_entities/schema_migrations.py`, `data_entities/postgres_migrations.py`.

| Hermod's entity | Table | Key | Columns written |
|---|---|---|---|
| shared context entry | `shared_record` | `project` + `title` (= theme) | `user_id`, `record_type='knowledge'`, `content_summary`, `tags`, dates, `full_content` |
| private context entry | `memory_record` | the above + `agent_id` | the same, plus `agent_id` |
| the orientation map | `shared_record` | `project` + `title='orientation-map'` | the same as a shared entry |

The tenant is injected at the seam, never passed by a caller. The agent is a caller argument for the private scope only.

### Component 2: The tenant resolver (`hermod-server`)
- **Purpose**: turn a verified token into the `user_id` Valaskjalf already knows, so the same Google account reads the same rows through either server.
- **Key Files**: `src/hermod/business_services/tenant_resolver.py` (new); wired in `app.py` and `api_mcp/server.py`.
- Behaviour mirrors Munnin's `TokenTenantResolver`: read `user_identity` by `(iss, sub)`; on a pair never seen, create the account and the mapping exactly as Munnin does. Nothing is read from config.

### Component 3: The importer, retargeted (`hermod-server`)
- **Purpose**: write the markdown tree into those same tables, once.
- **Key Files**: `src/hermod/data_migrations/markdown_importer.py` (rewritten against the record repository).
- Each entry gets a `uuid5` over `agent | project | scope | theme`, so a re-run upserts rather than duplicating. The frontmatter already supplies `content_summary`, `tags` and the dates.

### Component 4: The deployment and Munnin's filter
- **Purpose**: point Hermod at the memory database, take the old store out, and close Munnin's knowledge leak.
- **Key Files**: `hermod-deploy/config/deploy.yml` (DSN target repointed, volume removed); `agent-memory-server`'s two repositories (the knowledge-read filter only).

### Integration Architecture

| Component | Integrates with | Data flow | Depends on |
|---|---|---|---|
| Hermod's MCP face | the token guard | a call carries a token in; `(iss, sub)` out | Logto |
| Tenant resolver | `user_identity`, `account` | `(iss, sub)` → `user_id` | Valaskjalf's schema, Munnin having created it |
| Record repository | `shared_record`, `memory_record` | op → filtered rows | the tenant from the resolver, the agent from the call |
| Importer | the record repository, the markdown tree | 167 files + 7 maps → rows | the uuid5 identity |
| Munnin's knowledge reads | the same tables | rows where `project IS NULL` | the filter |

### Cross-System Contract Impact (Blast-Radius Check)

**Change classification**: ☑ new field (`content_summary`) ☑ semantics changed (a `knowledge` row with a `project` is Hermod's) ☑ consumer behaviour changed (Munnin's knowledge reads)

| # | Consumer | How it couples | Breaks how | Verified / mitigated |
|---|---|---|---|---|
| 1 | Munnin's repositories (both engines) | reads the record tables | silent-wrong if the filter lands on the wrong reads: fleet-wide it hid 728 episodes | filter on the knowledge reads only, pinned by the suite |
| 2 | Munnin's importer | writes `project` on episodes and knowledge | none; it keeps writing what it writes | untouched |
| 3 | Munnin's served ops (`query`, `search`) | read records | a project row leaks into a chat agent's knowledge view | closed by the filter; episode reads unaffected |
| 4 | Hermod's repository | reads and writes the same tables | crash when a table or column is absent | decision 6: it fails on the first store call |
| 5 | Munnin's migration runner | owns the DDL | a Hermod write arrives before the column exists | deploy ordering: Munnin migrates first |
| 6 | `hermod-deploy` | the DSN and the volume | points at a database this work removes | repointed in the same change |

- **Deploy ordering**: Munnin first, since it applies `0003` / `0002` on boot; Hermod second.
- **Existing data**: `content_summary` is NULL on every Munnin row, which is the intended state. Hermod's rows arrive through the import.

### Technical Considerations
- **Two writers on one database.** Munnin and Hermod both write `shared_record` and `memory_record`, and on a first contact `account` and `user_identity`. Postgres handles the concurrency; what matters is that the shape has one owner (decision 6).
- **Hermod's tests need a schema it does not own.** Hermod has no local serving path at all (decision 8: no login, no tenant, so it refuses to start), so the record tables exist for it only in tests, and a test fixture must create them. Carrying a minimal copy of Munnin's DDL into Hermod's tests is the honest option, pinned by a test that fails when the copy drifts from the columns the code uses. This is the one place the boundary costs something.
- **Create-on-first-contact is inherited, not introduced.** An unknown `(iss, sub)` creates a tenant, in both servers, which is Munnin's behaviour today.
- **`title` serves two jobs**, theme and display title, so one namespace holds two kinds of row. Latent, zero instances today.

### Solution Options & Evaluation

| # | Solution | Description |
|---|---|---|
| 1 | Valaskjalf's records, `knowledge` + `project` | this plan |
| 2 | Valaskjalf's records, a new `context` record type | the same, with a CHECK migration on `shared_record` |
| 3 | Hermod's own `project_context` table | the state ADR-026 built |
| 4 | Hermod's own table with an `agent_id` column | fixes the per-agent collision without leaving the table |
| 5 | A second database on Munnin's instance | what ADR-026 as written describes |
| 6 | A separate Postgres server for Hermod | its own failure domain |

| Solution | Pros | Cons |
|---|---|---|
| 1 | one store; the frame's own shape; the agent axis free via `memory_record`; no DDL | the two corpora share a table, so the boundary is a convention rather than a constraint |
| 2 | the schema enforces the boundary | one rebuild migration, and `record_type` is coarse where `project` already exists |
| 3 | simplest to read | cannot hold two agents' private entries (167 rows become 164) |
| 4 | fixes the collision inside Hermod's own table | keeps two homes for project memory, which is what the frame rejects |
| 5 | separate schemas, one engine | keeps project memory out of Valaskjalf, and two migration runners in one instance |
| 6 | full isolation | a second service to provision, back up and patch for a store this small |

- **Chosen**: 1.
- **Rationale**: the 2026-08-07 frame already says Valaskjalf holds all memory data, the `project` column was put there for it, and `memory_record` carries the agent Hermod's private half needs. Options 2 and 4 each buy a constraint at the price of a migration or a second home. Option 1 was chosen knowing its cost: the boundary is a convention two queries have to keep.

### ADR Output
- **ADR File**: [ADR-027](docs/adr/2026-10-13-hermod-store-is-valaskjalf-records.md)
- **Decision Summary**: Hermod's project memory is Valaskjalf's records, typed `knowledge` and scoped by `project`, with `agent_id` carrying the owner for the private half; the store ADR-026 built is removed and the tenant is resolved from the token.

---

## **IMPLEMENTATION PHASES**

### Phase 1: The record repository (crosses: DB)
- [x] **Step 1.1**: The record-backed repository
  - **Action**: Implement `ProjectRepository` over `shared_record` / `memory_record` for both engines.
  - **Implementation**: One class, two SQL dialects behind a small seam, mirroring the two classes it replaces: `%s` and `?`, an identity column instead of lastrowid, `deleted_date` as the tombstone. Reads filter on `record_type='knowledge'`, `project`, and `agent_id` for the private scope; writes carry `user_id`, `title`, `content_summary`, `tags` and dates. The map is a `shared_record` row with `title='orientation-map'`.
  - **Testing**: A contract test parametrized over SQLite and a real PostgreSQL, running the same assertions as `tests/test_store_backends.py` does today, plus a fixture that creates the record tables (the minimal DDL copy from Technical Considerations) and a test that fails when the copy drifts from the columns the code uses.
  - **Success Criteria**: Both engine suites green; create, read, update, move, delete and both map writes round-trip.
- [x] **Step 1.2**: Config, wiring and the deletions
  - **Action**: Point Hermod's store at Valaskjalf and delete the old one.
  - **Implementation**: `db_backend` / `db_url` become the Valaskjalf DSN and no local serving path (decision 8); `HERMOD_DB_PATH`/`db_path` lose their own-store meaning. Delete the two repositories, the two migration folders, the two runners and their tests, and update `app.py`'s factory.
  - **Testing**: Hermod's suite green with the deletions; a test that the app builds with no DDL of its own.
  - **Success Criteria**: No file under `hermod-server` creates a table; the suite passes.

### Phase 2: The tenant resolver (crosses: DB)
- [x] **Step 2.1**: `(iss, sub)` → `user_id`
  - **Action**: Resolve the tenant per request from the verified token, mirroring Munnin's resolver.
  - **Implementation**: A resolver reading `user_identity` and creating the account plus the mapping on a first contact. The MCP server pulls `(iss, sub)` off the verified token and hands it to the store layer; nothing reads a configured user id. With no issuer there is no token, so it refuses to start rather than naming a tenant by default (decision 8).
  - **Testing**: An isolated test proving two distinct subjects get two tenants and a returning subject keeps one, plus a test that the store layer never sees a caller-supplied `user_id`.
  - **Success Criteria**: A verified token alone determines whose rows are read and written.

### Phase 3: The importer, retargeted (crosses: DB)
- [x] **Step 3.1**: Write records instead of rows
  - **Action**: Retarget `markdown_importer.py` at the record repository.
  - **Implementation**: `uuid5` over `agent | project | scope | theme` for idempotence; `content_summary` from the frontmatter description; the map into a `shared_record` row titled `orientation-map`. Discovery and reporting stay as they are, including the collision block, which should now report none.
  - **Testing**: The existing importer tests against both engines, plus a dry run over the real markdown tree asserting **167 entries and 7 maps with 0 collisions**.
  - **Success Criteria**: A dry run reports nothing lost; a second run is a no-op.

### Phase 4: Munnin's knowledge filter
- [x] **Step 4.1**: `project IS NULL` on the knowledge reads only
  - **Action**: Close the leak without touching episode reads.
  - **Implementation**: Add the condition in `_filtered_sql` and `_search_rows` for `record_type=knowledge` on both repositories, with the reason inline. Leave episode, identity, reasoning, emotional and RAS reads alone.
  - **Testing**: Munnin's full suite (it was 9 failures when the filter was fleet-wide); a test that an episode with a project is still returned, and one that a `knowledge` row with a project is not.
  - **Success Criteria**: Both suites green, and the two new tests fail if the filter is widened or removed.

### Phase 5: The records (docs, no code)
- [x] **Step 5.1**: `db.md` restated
  - **Action**: Give the ops their `agent` argument and their record mechanics.
  - **Implementation**: Each op names its table and its filters; `§ ensure-context-dir` and `§ update-context-index` stay no-ops; the "local file" wording goes.
  - **Testing**: The seam's op-coverage test, which fails when a referenced op has no section.
  - **Success Criteria**: Every op resolves, and the served prompt compiles.
- [x] **Step 5.2**: The ADRs
  - **Action**: Record the reversal.
  - **Implementation**: ADR-027 written; ADR-026 marked superseded; ADR-025's "no tenancy" line corrected; ADR-024's store-ownership clause corrected.
  - **Testing**: Links resolve; the plan link from ADR-027 works.
  - **Success Criteria**: A reader arriving at any of the four lands on the current shape.

### Phase 6: Deploy, import, remove (crosses: DB, network)
- [x] **Step 6.1**: Deploy and import
  - **Action**: Put it live and move the data.
  - **Implementation**: Munnin deploys first (it applies the migrations), then Hermod with the repointed DSN; then the importer runs against the live store, dry run first.
  - **Testing**: `/health`, a 401 with the discovery pointer, and a store round trip with a real token; the dry run's counts against the live store.
  - **Success Criteria**: The import reports 167 entries and 7 maps with nothing lost.
- [ ] **Step 6.2**: Remove the old store
  - **Action**: Execute decision 2.
  - **Implementation**: Drop the `hermod` database, remove the volume from `config/deploy.yml`, confirm no migration folder survives.
  - **Testing**: The deployed server still answers and reads its rows after the drop.
  - **Success Criteria**: Nothing references Hermod's own store.

---

## **EXECUTION LOG**
**Execution Protocol for AI**:
I have to use this document as my **ONLY** source of truth to execute and track the plan steps iteratively. I should **NOT** use additional tools like ToDos because it lacks the context of what should I do. Everytime I want to implement a step I have to check the reference to the original step plan above. Everytime a step has been finished I need to go back to this document to log what was done.

**Definition of Done (applies to ALL steps)**:
- ✅ **Code Quality**: Code compiles/runs without errors
- ✅ **Testing**: Tests written and passing
- ✅ **Logged**: Implementation and testing logged below
- 🚫 **Blocked**: Get input from [USER-NAME] before assuming

### Phase 1:
- [x] **Step 1.1**: The record-backed repository
  - **Implementation Log**: `src/hermod/data_repositories/record_project_repository.py` — one class over both engines; connection, cursor, placeholder character and duplicate/foreign-key translation differ, everything else is shared. Identity is `uuid5` over `user_id | project | scope | theme` (`entry_uuid`) and over `user_id | project | orientation-map` for the map (`map_uuid`). A shared entry is a `shared_record` row, a private entry a `memory_record` row, and the map a `shared_record` row titled `orientation-map`, excluded from listings by its title. The private scope requires `agent` and refuses without it. No DDL anywhere. Supporting files: `tests/valaskjalf_schema.py` (the minimal record schema, both engines) and `tests/test_record_repository.py` (17 tests, parametrized).
  - **Testing Log**: **17 passed on SQLite; 34 passed with PostgreSQL 17.11 active; the full suite 165 passed with a service and 134 passed + 31 skipped without it, which is what CI runs.** Four defects were found and fixed getting there: SQLite refuses an inline foreign key that references a composite key, so it moved to a table-level clause; `sqlite3.Cursor` has no context-manager support on Python 3.12, so `_cursor` closes it by hand; a create over a tombstone collided instead of reviving; and the obvious fix for that (catching the violation) would have aborted the Postgres transaction, so existence is now checked before the insert.
  - **Success Criteria**: PASS — both engine suites green, and create, read, update, list both scopes, move between tables, tombstone-and-revive, and both map writes all round-trip.
  - **Result**: Done. Two behaviour changes against the store this replaces, recorded rather than inherited: (1) a create over a **tombstoned** theme revives that row instead of making a new one, because the identity is the uuid, so the old contract's "a re-created theme is a new entry with a different id" cannot hold and its assertion was replaced; (2) `list_context_entries` **requires** `agent` once the private scope is involved rather than answering with every agent's rows.
  - **Tech Debts**: `create_context_entry` still builds its shared column list by string-removing `agent_id` and splicing the matching parameter. It works and is tested, but it is fragile and wants a cleaner split at the quality review.
  - **Revision (same day, decision 9)**: the engine choice changed after this step was logged. The repository, `tests/valaskjalf_schema.py` and the contract are now **PostgreSQL-only**, and `.github/workflows/ci.yml` gained a `postgres:17` service with `HERMOD_PG_TEST_URL` set, because without it every store test skips and the job would go green by omission. Re-verified Postgres-only: **17 passed** for the contract, **148 passed** for the full suite with a service, and **117 passed + 31 skipped** without one. A fifth defect surfaced during the rewrite and was found the same way as the others, by reading the pass/fail split: `create_context_entry` passed 13 values to the 12-column shared table, so every shared create failed while every map create and every private create passed. The string-surgery tech debt is gone with the rewrite and the per-table value tuple is now written out.

- [x] **Step 1.2**: Config, the resolver and the wiring, then the deletions — **complete**
  - **Implementation Log**: `src/hermod/business_services/tenant_resolver.py`, mirroring Munnin's mechanism rather than approximating it: `user_identity` keyed on `(iss, sub)`, a new tenant minted as `uuid4().hex` and never taken from the issuer's subject, the account created with the claims' labels, the write re-read afterwards because two simultaneous first logins settle on one row, and a WARNING on creation because admission belongs to the authorization server and a new tenant should appear only when somebody was invited. `current_user_id()` reads the verified token through FastMCP's accessor and refuses with `MissingTokenError` when there is none, or when it names no subject. The test fixture gained `user_identity` and the `account` label columns.
  - **Testing Log**: `tests/test_tenant_resolver.py`, 6 tests against a real PostgreSQL: a new pair is stable on the second resolve; the same subject under another issuer is another tenant; the id is minted rather than taken from the subject; labels are stored for a new tenant only and are never a lookup key (two pairs sharing an email get two tenants); a second resolve leaves stored labels alone; and a call with no token names no tenant. **6 passed, the full suite 154 passed with a service, ruff clean.**
  - **Success Criteria**: PARTIAL — the resolver is done and verified; the config fields, the `app.py` wiring and the deletions are not started.
  - **Result**: In progress. The rest cannot land before the wiring, and the wiring cannot land before the config change, so the next piece is config plus per-request resolution, and the deletions of both repositories and both migration folders follow in one move.
  - **Config half (same day)**: `db_path` and `db_backend` are gone from `Config`; `db_url` is the store, `validate_backend` now refuses a config with no DSN (naming decision 9 in the message), and `build_project_repository` returns the PostgreSQL repository unconditionally. The old store is still what that repository is, because the swap belongs with the wiring.
  - **Config half, testing**: the change reached further than expected, and the reason is worth keeping: `build_app` validates the DSN at build time, so **every test that builds a config broke, not just the store tests** (21 failures at first). Six sites needed changing. Three never call a store tool, so a placeholder DSN satisfies the validator and the repository never connects: `test_auth.py` and `test_app.py` each carry one, with the reason in a comment. Two genuinely drive the store *being replaced*, so they record a skip rather than a fake pass, each naming where it converts: `test_end_to_end.py`'s live server (at the wiring) and `test_markdown_importer.py`'s CLI test (at the importer retarget in Phase 3). **Final: 153 passed + 1 skipped with a service, 111 passed + 43 skipped without one, ruff clean.**
  - **Wiring blocked on one question (found by mapping the references)**: `ContextService` holds a repository, and the repository now needs a *resolved tenant*, so the service has to build one per call from the token. That is mechanical. What is not is the **importer**: `markdown_importer.py` imports `build_project_repository`, and it runs as an offline CLI with **no token**, so nothing names the tenant it writes for. It is also coupled in the other direction, because the same factory serves both, and the importer's own tests (8 sites) construct the store directly. So the wiring, the importer retarget and the deletions are one move, not two: 8 source references, 2 repository files, 2 runner files, 2 migration folders, and `test_store.py` plus `test_store_backends.py` (whose coverage moves to `test_record_repository.py`). **Answered the same day (decision 10): `--iss` and `--sub`, resolved through the same `user_identity` mapping, refusing an unmapped pair** — his call, option A. `TenantResolver.resolve_existing` implements it together with the refusal, and two tests cover it: a mapped pair returns its tenant, and an unmapped pair raises rather than inventing one, including the same subject under another issuer. 8 resolver tests pass, the full suite 155 passed + 1 skipped, ruff clean. The rest of the move is unchanged: the service factory, the `app.py` wiring, the importer's CLI and its agent-carrying writes, the two test conversions, then the deletions and the two test files that go with them.
  - **Wiring done, and the store is gone (same day) — Step 1.2 complete, and with it Phase 2.** `ContextService` takes a factory and builds the repository per call from the resolved tenant; `app.py` wires `TenantResolver` and that factory; `build_project_repository(config, *, user_id)`; the six private-touching ops carry `agent` through the service and the tools; the importer takes `--iss`/`--sub` through `resolve_existing` and carries each private entry's agent from the markdown path that held it. Deleted: both repositories, both migration runners, both migration folders, `test_store.py` and `test_store_backends.py`.
  - **Two defects, the same shape, and both about identity rather than data.** The agent was missing from an *identity* twice: first in the importer's claim key, which still reported two agents' files as a collision the store no longer has, and then in `entry_uuid` itself, where omitting it gave two agents' rows one uuid so the second was silently skipped as a duplicate. The second one is the more instructive: it presented as `theirs is None`, a missing row, with nothing raised and nothing logged, and it was found only by asserting that both agents' rows exist. A third, smaller one is worth noting for the same reason: `test_end_to_end.py`'s round trip failed on a missing `agent` argument, which is what made the tool half of decision 4 necessary rather than optional.
  - **Wiring, testing**: **111 passed with a service, 70 passed + 41 skipped without one, ruff clean.** The service-level coverage that had to outlive the deletion was moved into `test_record_repository.py` in the same pass, three tests: the stamp gate's three refusals, the line cap refusing rather than splitting, and reads answering with no overlay checkout while a write names why it cannot. `test_end_to_end.py` converted to the guarded, record-backed shape with a seeded mapping, so the resolver lands on the tenant whose agent rows exist rather than minting one with no agents. `test_mcp_surface.py` builds its service over a repository that is never connected, which is honest for a file that drives registration and reaches no store.

### Phase 2:
- [x] **Step 2.1**: The tenant resolver — **done, and logged at Step 1.2 above**
  - **Implementation Log**: `src/hermod/business_services/tenant_resolver.py`. `(iss, sub)` read against Valaskjalf's `user_identity`; a new tenant minted as `uuid4().hex` and never taken from the issuer's subject; the account created with the claims' labels; the write re-read afterwards because two simultaneous first logins settle on one row; a WARNING when a tenant appears; `current_user_id()` reading the verified token and refusing with `MissingTokenError` when there is none or when it names no subject; and `resolve_existing`, which refuses an unmapped pair for a caller with no token.
  - **Testing Log**: `tests/test_tenant_resolver.py`, 8 tests against a real PostgreSQL — a new pair is stable on the second resolve, another issuer is another tenant, the id is minted not taken, labels are stored once and never looked up, a second resolve leaves them alone, no token means no tenant, and `resolve_existing` finds a mapped pair while refusing an unmapped one.
  - **Success Criteria**: PASS — a verified token alone determines whose rows are read and written, with no configured user id anywhere.
  - **Result**: Done. It was built before Step 1.2 rather than with it, because 1.2 could not land without a tenant to construct its repository with; the log at 1.2 records it as that step's first half, so a reader of either phase finds it.

### Phase 3:
- [x] **Step 3.1**: Write records instead of rows — **done and verified against the real tree**
  - **Implementation Log**: `markdown_importer.py` retargeted. Discovery carries the owner: a private source records the domain from its `agent-<domain>` folder, and the importer passes it on every private read, write and presence check. The CLI names the tenant with `--iss`/`--sub` through `resolve_existing`, refusing an unmapped pair, and reports the tenant it resolved rather than a backend. The claim key and the repository's `entry_uuid` both gained the agent — the two defects this step found, recorded at Step 1.2.
  - **Testing Log**: `tests/test_markdown_importer.py` converted to the record repository with a real store and a seeded login: 13 tests, including one that asserts what the move was for, that the same theme under two agents is two rows rather than a reported collision, and one that asserts the importer refuses a pair nobody has signed in with. **Real-tree dry run against a real store: 167 entries, 7 maps, 0 colliding, 2 frontmatter mismatches reported and imported under their directories.**
  - **Success Criteria**: PASS — nothing is lost, and the three collisions the old identity produced are gone because the owner is part of the identity.
  - **Result**: Done. The count is the same 167 the markdown holds, which is the point: the store can now represent all of it.

### Phase 4:
- [x] **Step 4.1**: [link to step above]
  - **Implementation Log**: The predicate is one clause, `(record_type <> 'knowledge' OR project IS NULL)`, added to the shared filter builder (`_filtered_sql`) and to the full-text reader (`_search_rows`) in **both** Munnin repositories. It is written as a read invariant beside tenancy and lifecycle, so it holds for every caller and every requested `record_type` rather than being a branch each read has to remember: a bare `query()` or `search()` is the path `awaken` and the served tools actually use, and those pass no `record_type` at all. The predicate is stated as *not* `(knowledge with a project)`, not as `project IS NULL`, because the column is load-bearing for episodes — `awaken` selects a project's latest episode by it.
  - **Testing Log**: Two tests in `tests/data_repositories/test_repository_contract.py`, parametrized over both engines. The first asserts a project-keyed **episode** is still returned by `query()`, by `query(record_type=episode)` and by `search()`. The second asserts a project-keyed **knowledge** row is returned by nothing: not `query_shared`, not `query(record_type=knowledge)`, not `query(project=...)`, not `search_shared`, not `search` — with the unfiltered sibling asserted in the same test, so a filter that excluded everything would fail there too rather than pass quietly. **Mutation-proved in both directions**: deleting the predicate reddens the knowledge test (`test_a_project_keyed_knowledge_row_is_not_munnin_memory`, the `query(record_type=knowledge)` assertion), and widening it to a bare `project IS NULL` reddens the episode test — each mutation applied by a self-verifying script that asserts a single match and exits non-zero on a miss, and the file restored from a byte copy afterwards with `git diff` read to confirm no residue. **Full suite: 549 passed with PostgreSQL 17 (no skips), 525 passed + 24 skipped on SQLite alone, ruff clean.**
  - **Success Criteria**: PASS — both engine suites green, and both new tests fail under the mutation that should break them.
  - **Result**: Done. Nothing above the seam changed: the filter lives in the repository, the service and the served tool signatures are untouched, and `awaken`'s episode reads are unaffected by construction. After the retarget the two corpora are distinguished by data alone (the agent axis arrives via `memory_record`, the project axis via `project`), and this predicate is the one place Munnin keeps its half of that boundary.

### Phase 5:
- [x] **Step 5.1** / **Step 5.2**: [links above]
  - **Implementation Log**: `storage-backends/db.md` restated as one flow. Its header now says the store *is* the memory database's records and links ADR-027, and a new note states the mapping a reader needs to act: a context entry is a `knowledge` row with a `project` (in `shared_record` for the shared scope, `memory_record` for the private one), the orientation map is a `shared_record` row titled `orientation-map`, `title` carries the theme and `content_summary` the description, the two derived identities, that `project` is the whole boundary between the corpora and the memory store's own reads exclude the rows that carry it, and that **Hermod issues no DDL**. `all-procedures` lost *"SQLite for a local run, a PostgreSQL database in a deployment"* (stale twice: decision 9 removed SQLite, and there is no store of Hermod's to configure) and gained the split the ops work on — whose rows are the token's, the project is an argument, the agent is an argument where a private row is involved. Every op now names its table and its filters, and the **six** ops that touch the private scope carry `agent`: `list_context_entries(project, scope?, agent?)`, `read_context_entry`, `create_context_entry`, `update_context_entry`, `move_context_entry` and `delete_context_entry`. Three op bodies say something the old text got wrong: the update is a stated wholesale replace that clears `content_summary` and `tags` when they are not passed; the move is two row operations across two tables, with the markdown path's own copy-then-delete exposure rather than "no partial state"; and the delete's tombstone revives on the same derived identity. Corrections, all naming ADR-027 as their authority: **ADR-026** marked *Superseded* (it described two tables and a sibling database that were never built); **ADR-024**'s store-ownership clause corrected in both the Decision and the Requirements bullet; **ADR-025**'s *"minus its tenancy"* corrected where it is decided; and **ADR-027**'s own two-engine Success Criterion corrected to PostgreSQL-only, because decision 9 removed SQLite after the ADR was written. The two ADRs keep their original sentences with an inline *Corrected by* marker rather than being rewritten, so the record still shows what was decided then.
  - **Two false statements in `hermod-server`'s served text, fixed rather than filed.** `INSTRUCTIONS` told every connecting client that project context and the map *"live in this server's own store"*, and `_register_store`'s docstring justified its registration independence by *"the store is a local file"* — the same claim this step removes from the documentation, in the one place a client reads first. Both corrected in place. The `openWorldHint: False` annotations were **left alone** and are raised as a question instead: whether a tool that reaches a database counts as an open world is a design call with a real consequence for client confirmation prompts, not a wording fix.
  - **Testing Log**: The overlay suite, **52 passed**. The op-coverage check was proven to be reading the restated file rather than passing by omission: renaming one op heading in `db.md` reddens `tests/test_fidelity.py::test_no_served_prompt_leaves_an_op_unresolved`, and the file was restored from a byte copy afterwards (**0 CR, 119 LF, 10,089 bytes**) with the loader and fidelity modules green again at 23 passed. `hermod-server`'s suite re-run against the modified content with PostgreSQL active: **111 passed, ruff clean** — that is the suite that composes `db.md` into the served prompts and asserts no op is left unresolved.
  - **Success Criteria**: PASS — every op resolves, the served prompt compiles, and a reader arriving at any of the four ADRs lands on the current shape.
  - **Result**: Done. "Docs, no code" held except for the two served-text corrections, which state what the system is rather than changing what it does. Residue worth carrying: the ADRs' inline markers mean four documents must be read for the store's full history, and ADR-024's Rejected section still argues the family split against a store shape that no longer exists — deliberate, since an ADR records a decision made at a time.
  - **Tech Debts**: **New** — the MCP annotations assert `openWorldHint: False` on the store tools while those tools now reach a database over the network; the question is whether that flag should change, and it is left for [USER-NAME] rather than decided here. **New** — `hermod-server`'s pinned overlay pointer moved only when this plan's commits did, so the checkout was already ahead of the pin at the start of the step.

### Phase 6:
- [x] **Step 6.1**: Deploy and import — **done and verified from outside the box**
  - **Implementation Log**: The repository side landed first (`hermod-deploy@94d3e73`, then `@48c93d8`): `config/deploy.yml` lost `HERMOD_DB_PATH`, `HERMOD_DB_BACKEND` and the `hermod-data` volume, its DSN comment now names the **memory** database, and `hermod-server` is pinned at `3792b0b`. The deploys themselves were run from infra, in the order this plan requires: Munnin (`ccfe2ae`) then Hermod (`3792b0b`). The import then ran from the box against the running release, using the product's own image: `--source /import --iss https://auth.lok.quest/oidc --sub iw9vvijlhs8k --dry-run`, then the same command without `--dry-run`. The tree travelled as a 2.4 MB tarball (`shared-memory` plus 33 `agent-*/knowledge-base` directories), because the source repo is private and the box cannot fetch it; the tarball and its extracted tree were removed from the box afterwards.
  - **Testing Log**: **From outside, after the deploy**: `/health` answers 200 on both hosts; `POST /mcp` on Hermod answers 401 with `Www-Authenticate: Bearer resource_metadata="https://hermod.lok.quest/.well-known/oauth-protected-resource/mcp"`, and that document answers 200 naming `resource=https://hermod.lok.quest/mcp` and `authorization_servers=["https://auth.lok.quest/oidc"]`. **On the box**: `docker ps` shows `hermod-web-3792b0b` and `munnin-web-ccfe2ae`, which is the ordering and the exact tags; `information_schema` returns **`content_summary` on both `shared_record` and `memory_record`**, the column Hermod writes and Munnin had never deployed. **The import**: the dry run reported `entries: 168 (168 written, 0 already present, 0 colliding)` and `maps: 7 (7 written, 0 already present)`, with the tenant resolving to `alvi` through the tokenless `(iss, sub)` path; the apply reported the same; a second dry run then reported `168 (0 written, 168 already present)` and `7 (0 written, 7 already present)`, which is the idempotence the derived identity exists for. **Counted in the database**: 65 shared entries, 7 maps and 104 private knowledge entries, over 18 and 38 distinct projects. **The arithmetic closes against the tree**: discovery yields 65 shared (90 context files − 7 maps − 18 `context-index.md` projections) and 103 private (only directories holding a `context-index.md`, the marker that separates a project-context home from general knowledge), which is the importer's 168 exactly.
  - **Success Criteria**: PASS, with the count moved. The import reports **168** entries and 7 maps rather than 167, because the markdown tree gained an entry since the retarget session measured it; nothing is lost, and there are 0 collisions where the old identity produced three.
  - **Result**: Done. The store is live, owned by the memory database, written by the product's own importer, and re-readable without writing anything.
  - **Tech Debts**: **New and real** — one row is now reachable from neither server: `memory_record`, project `munnin-deploy`, agent `infra`, titled *Munnin VPS Shared Host*. It is Munnin's own knowledge entry whose frontmatter carries a `project`, so Munnin's new filter excludes it from every knowledge read, while Hermod never imported it because its directory holds no `context-index.md` and is therefore general knowledge. Decision 3 accepted this residue as *"latent, zero instances today"*; there is one instance, and it is identified rather than counted. The ADRs' annotations question stands. Two files disagree with their own directory and were imported under the directory, reported rather than hidden.

- [ ] **Step 6.2**: Remove the old store — **the database is already gone; the volume is not**
  - **Implementation Log**: The file half is done: no `volumes:` entry and no SQLite env in `config/deploy.yml`, and no migration folder, runner or schema file survives in `hermod-server`. On the box, `pg_database` lists **`munnin` only** — there is no `hermod` database, so the drop this step names has nothing to act on: the setup in `deploy/README.md` was written out rather than run. The `hermod-data` volume still exists and nothing mounts it.
  - **Testing Log**: `docker volume ls` on the box shows `hermod-data` beside `munnin-data` and `munnin-pgdata`; the running Hermod container was started without it, and the import wrote and read rows with it unmounted, which is the check that mattered.
  - **Success Criteria**: PARTIAL — nothing in either repo references Hermod's own store, and no database of its own exists; one orphan volume remains on the host.
  - **Result**: Left open deliberately. Removing a volume destroys the last copy of the SQLite file, which is irreversible and is [USER-NAME]'s call rather than mine. It holds no real data, so there is no hurry.
  - **Tech Debts**: `hermod-data` is an orphan volume; the `probe` nginx container is still running on the box.

---

## **QUALITY REVIEW**
*Filled by procedure Step 16 (delegated to `/analyze-code-quality` in embedded mode) after all execution phases are complete. **Static** review.*

- **Scope**:
- **Quality Standard**:
- **Findings**:
- **Fixed**:

---

## **QA HANDOFF**
*Filled by procedure Step 17 after Quality Review is resolved. This plan is **not** runtime-verified.*

- **Scope**: `hermod-server`'s store layer and importer; `agent-memory-server`'s knowledge reads; `hermod-deploy`'s config
- **QA instrument**: NOT SET UP — `hermod-server` has no `qa/` directory, so there is no map and no bench
- **Integration coverage**: NONE — `hermod-server` has no `qa/` directory, so there is no map and no bench, and Phases 1, 2, 3 and 6 cross a real database boundary. Confirmed with [USER-NAME] on 2026-10-13 (*"yes, no qa"*), before implementation, and recorded here rather than left silent.
- **Checklist**: none — will be recorded at Step 17
- **Coverage split**: TBD
- **Runtime verification**: **NOT DONE.** Next action: set up the instrument first: `/map-qa-instrument create` → `/build-qa-bench`

> Do not read a filled checklist as a passed one. This section says a verification *plan* exists, nothing more.

---

## **POST-COMPLETION**
After all phases are executed, logged, and both **Quality Review** + **QA Handoff** are filled, move this plan to `plans/completed/`:
`mkdir -p ./plans/completed && mv ./plans/[this-file].md ./plans/completed/[this-file].md`
