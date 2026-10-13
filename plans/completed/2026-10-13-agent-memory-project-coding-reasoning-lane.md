# High Wizard Plan

## **PROJECT INFO**
- **Project**: agent-memory-project (Hermod)
- **Date**: 2026-10-13
- **Agent**: meta (Claude Meta)
- **Theme**: Coding-reasoning lane: a real store home for `coding-reasoning-memory.md`, a Hermod write command, a read the coding awakening loads through, and an importer that carries the file in.
- **Source Protocol**: `/high-wizard` — escalated from `/quick-wizard` (scope gate fired)

*CRITICAL INSTRUCTION: To continue this plan: load the source protocol above, then inspect which sections below are filled vs unfilled to infer your current step.*

---

## **INHERITED CONTEXT**
*Filled at investigation step 0 with whatever was settled before this plan existed. The two sources are recorded separately and never merged — write "None" under a part that does not apply.*
*These decisions are **not yours to reopen**. If one looks wrong, STOP and surface it to [USER-NAME] — do not silently re-decide it here or in Confirmed Decisions below.*

### From the Parent Plan
- **Parent plan**: None — not a sub-plan. Escalated from `/quick-wizard` at its Step 2 scope gate (multi-repo, schema change, ADR warranted).
- **Assigned scope**: n/a.
- **Integration contracts**: None.
- **Pushed-down open items**: None.

### From Pre-Planning Discussion
- **Discussion**: Pre-planning discussion with Alvi, 2026-10-13 (evolved across the session; several calls were corrected mid-flight and the corrected form is recorded here).
- **Agreed scope**: give `coding-reasoning-memory.md` a real home in the store, so a coding agent loads it and a command writes it, instead of the file being hand-edited and invisible to the DB.

| # | Settled decision | Chosen | His reason | Status |
|---|------------------|--------|------------|--------|
| 1 | Is the layer a resource or memory? | Shared memory, not a resource | It changes; patterns are promoted into it, so it is data an agent writes, not a static template/script. | Settled |
| 2 | Lane marker in the store | `record_type = "coding_reasoning"` | He chose the explicit type over a `project` sentinel or a tag. It makes the chat-agent leak structurally impossible: `awaken` selects shared reasoning by `record_type is RecordType.reasoning`, so a `coding_reasoning` row never enters it. | Settled |
| 3 | Read surface | A dedicated read (a `coding_reasoning()` tool on Munnin), not an `awaken` parameter | Keeps `awaken` project-blind; the lane is reachable only by a deliberate ask. | Settled |
| 4 | Write command home | A new **Hermod** command `/add-coding-reasoning`; the core `/add-reasoning` is untouched | "Munnin = core, Hermod specific for project coding." The write for a coding concept must not sit on the core's command surface. | Settled |
| 5 | How far this plan goes live | Code + tests + local/dev import here; the deployed store is migrated and imported by the deploy path (`munnin-deploy`) | Keeps a live schema write inside the release path, which already has the rollout/rollback rehearsal. | Settled |

- **Considered and rejected**:
  - **`project`-column sentinel lane** (no migration) → lost when he chose the explicit `record_type`. Also independently unsafe: the corpus boundary predicate `(record_type <> 'knowledge' OR project IS NULL)` does **not** hide a `reasoning` row with a `project`, so such a row would leak through `awaken`.
  - **`tags = ["coding"]` lane** (no migration) → lost: a tag is metadata, so the lane's identity lives in something easier to strip.
  - **Moving the lane into Hermod's `knowledge` corpus** (my over-correction) → withdrawn. `record_type = "coding_reasoning"` in `shared_record` is the chosen home.
  - **A scope branch on the core `/add-reasoning`** → rejected: that puts a coding concept into Munnin's command surface, the boundary he flagged. Note this **supersedes** the 2026-08-15 call ("a scope argument on the one command, never a sibling command"), whose reason was about a *core* sibling; a Hermod command is a layer split, not a destination split.
- **Left open**: none. (The plan's own home repo was noted in conversation as Hermod; this file lives there.)

---

## **OBJECTIVES**
Give `coding-reasoning-memory.md` a first-class home in the store: a `coding_reasoning` shared record type that `awaken` never surfaces to a chat agent, a Hermod command that writes it, a read the coding awakening loads it through, and an importer that carries the existing file into it. End state: coding patterns stop being hand-edited into a file the database never sees, and a coding agent loads them instead of reporting them absent.

### **Related Documents**
- Project context `coding-reasoning-layer.md` (agent-memory project) - the scope test and the 2026-08-15/2026-08-20 decisions this plan supersedes or completes.
- Project context `memory-mcp-server-build.md` - records that `import_shared` never reads the file, and the `__coding__` lane shape.
- ADR-027 (`hermod-server/agent-memory-project/docs/adr/2026-10-13-hermod-store-is-valaskjalf-records.md`) - the store is the memory database's records; the `project` column is the corpus boundary.
- `C:\Work\IM\@agent-memory\shared-memory\coding-reasoning-memory.md` - the layer itself (31,233 B, modified 2026-10-13).

### **SUCCESS CRITERIA**
- [ ] `coding_reasoning` is a legal `shared_record` type on both engines: `RecordType`, `SHARED_RECORD_TYPES`, the SQL `CHECK`, a SQLite `0004` rebuild and a Postgres constraint swap; `test_schema.py`'s pin covers the new value.
- [ ] `awaken(domain)` output is **unchanged** for a chat agent: no coding row appears in `shared.reasoning`.
- [ ] A read returns the coding lane, and the overlay's `§ load-coding-reasoning` (`storage-backends/db.md`) uses it.
- [ ] `/add-coding-reasoning` (Hermod) writes a `coding_reasoning` shared row end to end.
- [ ] `import_shared` carries `coding-reasoning-memory.md` into the lane; a missing file skips quietly.
- [ ] Unit tests for every step with testable logic; static quality review completed; QA handoff completed.

---

## **SCOPE**

### In Scope
- **Munnin (`agent-memory-server`)**: `RecordType.coding_reasoning` + `SHARED_RECORD_TYPES`; the SQLite `0004_shared_record_coding_reasoning.sql` rebuild and the Postgres constraint swap; `insert` accepting `coding_reasoning` for `scope="shared"`; the `coding_reasoning()` read tool; `import_shared` fifth read plus its parser; template gating for the new type.
- **Hermod (`agent-memory-project`)**: the `/add-coding-reasoning` procedure and its ops in both storage backends; the `§ load-coding-reasoning` line in `storage-backends/db.md` pointing at the read.

### Out of Scope
- **Retiring Munnin's SQLite** — a much larger decision of its own. SQLite is the default backend and the engine the whole test suite runs on, so the `0004` migration is required, not optional.
- **A plain `shared` reasoning write on the core `/add-reasoning`** — its recorded debt stands; nothing in this plan needs it.
- **Landing on the deployed store** — the deploy path owns the migration and the live import (see decision 5).
- **Any change to `awaken`'s output** — it must stay byte-for-byte for a chat agent.

---

## **CONFIRMED DECISIONS**
*Decisions made **by this plan** — both **asked-and-confirmed** by [USER-NAME] AND **written-through** (Zone A and B decisions made by the agent, recorded with their reasoning). The reasons serve as the analysis record.*
*Decisions settled before this plan existed belong in INHERITED CONTEXT above, not here.*

| # | Decision | Chosen | Reason |
|---|----------|--------|--------|
| 1 | Importer shape | A fifth read in `import_shared` for `coding-reasoning-memory.md`, guarded by existence so a missing file skips quietly | Mirrors the user-profile read, the one other file that may legitimately be absent. The other four are framework invariants and stay unguarded. |
| 2 | Migration shape | SQLite `0004` copies the `0002` table-rebuild pattern (CHECK widening, indexes and FTS triggers recreated, `shared_fts` rebuilt); Postgres gets an in-place `DROP CONSTRAINT` / `ADD CONSTRAINT` | SQLite cannot ALTER a CHECK, so a rebuild is the only route and `0002` is the working precedent. Postgres lists `ras` in its CHECK from day one and can alter it without a rebuild. |
| 3 | Identity of a coding row | `stable_uuid` derives from a distinct first component (not `"shared"`), so a re-import is idempotent and cannot collide with a universal row | `_to_shared_record` currently fixes the first component for all shared rows; the new lane needs its own, or two different records share an id. |
| 4 | Template gate | `coding_reasoning` is gated like `reasoning`, against the same `reasoning-pattern-template` | The lane holds reasoning patterns; the gate exists so a pattern is built against a declared template version. |
| 5 | Read tool shape | The `coding_reasoning()` tool returns the whole lane (all `coding_reasoning` shared rows), no query argument | The layer is loaded whole at awakening, the same way `shared.reasoning` is; nothing needs a filtered read. |
| 6 | Command name | `/add-coding-reasoning` | One term across all three artifacts: `coding-reasoning-memory.md`, `record_type = "coding_reasoning"`, `/add-coding-reasoning`. Chosen over the `-coding` suffix so the command names the same object the file and the type do. |

---

## **SOLUTION**

### Architecture Overview

The coding-reasoning lane is a `shared_record` row with `record_type = "coding_reasoning"` and `project = NULL`. It lives in Munnin's store but is marked by a type distinct from `reasoning`, and that is the whole safety property: `awaken` builds the universal layer with `record_type is RecordType.reasoning`, so the new type can never match and never reaches a chat agent. The write lives in Hermod (`/add-coding-reasoning`), which preserves Munnin = core and Hermod = project/coding. The read is a Munnin tool the Hermod awakening calls, and the importer carries the existing markdown file into the lane.

### Component 1: Munnin store type and schema
- **Purpose**: admit `coding_reasoning` as a legal `shared_record` type on both engines, without touching any read a chat agent uses.
- **Key Files**: `src/munnin/data_entities/memory_record.py` (`RecordType`, `SHARED_RECORD_TYPES`); `migrations/0004_shared_record_coding_reasoning.sql`; `migrations_postgres/0003_shared_record_coding_reasoning.sql`; `data_repositories/sqlite_memory_repository.py` and `postgres_memory_repository.py` (insert acceptance); `tests/data_entities/test_schema.py` (the pin).

### Component 2: Munnin importer
- **Purpose**: carry `shared-memory/coding-reasoning-memory.md` into the lane; a missing file skips quietly.
- **Key Files**: `src/munnin/data_migrations/importer.py` (`import_shared`); `markdown_parser.py` (a `coding_reasoning` parser); `tests/test_fidelity.py`.

### Component 3: Munnin read tool
- **Purpose**: return the whole lane on a deliberate ask.
- **Key Files**: `business_services/memory_service.py`; `data_repositories/memory_repository.py`; `api_mcp/server.py`; `api_http/api.py`.

### Component 4: Hermod write command
- **Purpose**: `/add-coding-reasoning` authors a pattern and writes it as a `coding_reasoning` shared row through Munnin's `insert`.
- **Key Files**: `procedures/add-coding-reasoning.md`; `storage-backends/db.md` and `storage-backends/markdown.md`; `tests/`.

### Component 5: Hermod load line
- **Purpose**: `§ load-coding-reasoning` reads the lane instead of pointing at nothing.
- **Key Files**: `storage-backends/db.md` (and `markdown.md` for the file form).

<!-- OPTIONAL SECTION A -->
### Integration Architecture

| Component | Integrates With | Data Flow | Dependencies |
|-----------|----------------|-----------|--------------|
| Munnin store type | both engines, both repositories | schema + enum in, rows stored | `0004` / Postgres migration |
| Munnin importer | the markdown store file | `coding-reasoning-memory.md` in, `coding_reasoning` rows out | Component 1 |
| Munnin read tool | Hermod awakening | lane rows out | Component 1 |
| Hermod command | Munnin `insert` | draft pattern in, `insert(scope="shared", record_type="coding_reasoning")` | Component 1 |
| Hermod load line | Munnin read tool | read call out, lane into the coding awakening | Component 3 |

<!-- OPTIONAL SECTION A2 -->
### Cross-System Contract Impact (Blast-Radius Check)

*A producer-side change to shared data silently breaks consumers nobody updated in the same pass. Enumerate every consumer of the changed shape and how each is verified BEFORE shipping. Producer and consumers are usually separate deploys.*

**Change classification**: [x] enum value added (`shared_record.record_type` gains `coding_reasoning`)

| # | Consumer (system + path) | How it couples | Breaks how on this change? | Verified / mitigated |
|---|--------------------------|----------------|----------------------------|----------------------|
| 1 | Munnin `awaken` (`memory_service.py`) | DB-read, filters by `record_type is reasoning` | none (the new type cannot match the filter) | The filter predicate; a test asserts a chat agent's payload is unchanged |
| 2 | Munnin `query` / `search` shared reads | DB-read, returns all shared rows | none breaking: the lane becomes visible to a general query | Accepted: the lane is fleet knowledge, just not auto-loaded |
| 3 | Hermod `list_context_entries` | DB-read, `knowledge` + `project` only | none (a `coding_reasoning` row is invisible there) | The store's read predicate (`knowledge`-gated) |
| 4 | The importer | parses the file, writes the type | n/a (it is the producer) | Round-trip fidelity test on the real file |
| 5 | Existing deployed rows | none carry the value | none | Additive; no backfill, no historical data |

- **Deploy ordering**: Munnin first (schema + read tool), Hermod second (command + load line). The command calls an `insert` the store must accept, and the load line calls a read that must exist.
- **Existing data**: additive. No row carries `coding_reasoning` before this, and no parser must handle a mixed format.
- **Project registry**: none for this project.

<!-- OPTIONAL SECTION C -->
### Technical Considerations

- **Why the marker is a type, not a project**: the corpus boundary predicate is `(record_type <> 'knowledge' OR project IS NULL)`. A `reasoning` row carrying a `project` is **not** hidden by it, so a project marker would leak through `awaken`. A distinct type is the only marker that is safe without changing Munnin's read rule.
- **SQLite cannot ALTER a CHECK**: the `0004` migration is a table rebuild, following the working `0002` pattern (recreate the table, copy rows, drop, rename, recreate indexes and FTS triggers, rebuild `shared_fts`). Postgres can swap the constraint in place.
- **Identity**: `_to_shared_record` fixes `stable_uuid`'s first component to `"shared"` for every shared row. The lane needs its own first component, or a coding row and a universal row could share an id across re-imports.
- **`awaken` must be untouched**: the success criterion is a byte-comparable payload for a chat agent, so a test asserts it rather than trusting the filter by inspection.
- **Template gate**: `coding_reasoning` is gated, against the same `reasoning-pattern-template` the `reasoning` type uses.

<!-- OPTIONAL SECTION F -->
### Solution Options & Evaluation

| # | Solution | Description |
|---|----------|-------------|
| 1 | New `record_type = coding_reasoning` | A distinct shared type; `awaken` excludes it by construction |
| 2 | `project` sentinel on `reasoning` rows | Reuse the boundary column; no migration |
| 3 | `tags = ["coding"]` on `reasoning` rows | No migration; filter by tag |
| 4 | Hermod `knowledge` corpus item | Store it as a project-marked knowledge row |
| 5 | Keep the markdown file only | No store change; the overlay reads the file |

| Solution | Pros | Cons |
|----------|------|------|
| 1 (chosen) | No leak by construction; self-documenting; reads 1:1 with the file | One core enum value + two migrations |
| 2 | No migration | The boundary predicate does not hide `reasoning` + project, so it leaks unless a core read rule changes |
| 3 | No migration | Identity lives in metadata, easy to strip |
| 4 | No Munnin change | The lane is reasoning, not knowledge; wrong corpus and load semantics |
| 5 | No change at all | The served overlay has no file channel, so the layer stays absent online |

#### Selected Approach
- **Chosen**: Solution 1, `record_type = "coding_reasoning"`, `project = NULL`, in `shared_record`.
- **Rationale**: It is the only option that keeps the chat-agent leak impossible without changing Munnin's read rule, and it keeps the core's `project` boundary untouched. The write command lives in Hermod, so the layering (Munnin = core, Hermod = project/coding) holds at the command surface.

<!-- OPTIONAL SECTION G -->
### ADR Output

- **ADR File**: [`docs/adr/2026-10-13-coding-reasoning-lane.md`](docs/adr/2026-10-13-coding-reasoning-lane.md)
- **Decision Summary**: The coding-reasoning layer is a `coding_reasoning` shared record type in Munnin's store, written by a Hermod command and read by a Munnin tool; it supersedes the 2026-08-15 "never a sibling command" call, whose reason was about a core sibling rather than a layer split.

---

## **IMPLEMENTATION PHASES**

### Phase 1: Munnin store type and schema
- [ ] **Step 1.1**: Add the `coding_reasoning` type to the enum and the pin
  - **Action**: Add `RecordType.coding_reasoning` and its entry in `SHARED_RECORD_TYPES`.
  - **Implementation**: `memory_record.py`; update `tests/data_entities/test_schema.py` so the pin covers the new value.
  - **Testing**: The schema pin test must fail before the SQL `CHECK` matches and pass after; run the entity tests.
  - **Success Criteria**: `coding_reasoning` is a legal shared type in code, and the pin test asserts it against the SQL.
- [ ] **Step 1.2**: SQLite migration `0004`
  - **Action**: Widen the SQLite `CHECK` to admit `coding_reasoning`.
  - **Implementation**: New `0004_shared_record_coding_reasoning.sql`, copying the `0002` rebuild shape (table copy, drop, rename, indexes, FTS triggers, `shared_fts` rebuild).
  - **Testing**: `tests/data_entities/test_migrations.py`; migrate a populated DB and confirm rows and FTS survive.
  - **Success Criteria**: a `coding_reasoning` insert succeeds on SQLite; a fresh and a migrated DB agree.
- [ ] **Step 1.3**: Postgres migration
  - **Action**: Swap the Postgres `CHECK` in place.
  - **Implementation**: New `migrations_postgres/0003_shared_record_coding_reasoning.sql` (`DROP CONSTRAINT` / `ADD CONSTRAINT`).
  - **Testing**: `tests/test_postgres_migrations.py` (runs when a URL is present).
  - **Success Criteria**: the constraint admits `coding_reasoning` on Postgres; the migration is idempotent.
- [ ] **Step 1.4**: `insert` accepts the type for shared scope
  - **Action**: Let `insert(scope="shared", record_type="coding_reasoning")` through, and gate it like `reasoning`.
  - **Implementation**: repository insert validation plus the `_check_template` mapping in `server.py`.
  - **Testing**: `tests/business_services/test_write_ops.py`; a missing `template_version` is refused, a valid one is accepted.
  - **Success Criteria**: the lane can be written through the service and the tool, and the gate fires.

### Phase 2: Munnin importer
- [ ] **Step 2.1**: Parser for the coding-reasoning file
  - **Action**: A `parse_coding_reasoning` alongside `parse_shared_reasoning`.
  - **Implementation**: `markdown_parser.py`, reusing the level-3 section split.
  - **Testing**: A unit test on a small fixture, and a fidelity test on the real 31 KB file.
  - **Success Criteria**: every pattern in `coding-reasoning-memory.md` parses as one item.
- [ ] **Step 2.2**: Fifth read in `import_shared`, guarded
  - **Action**: Read the file and write the lane; skip quietly if absent.
  - **Implementation**: `importer.py`, following the user-profile guard; give the lane a distinct `stable_uuid` first component.
  - **Testing**: Re-import is idempotent (same uuids, no duplicates); a missing file imports zero of that type without raising.
  - **Success Criteria**: the lane imports on first run and re-imports with no change.

### Phase 3: Munnin read tool
- [ ] **Step 3.1**: The lane read
  - **Action**: A `coding_reasoning()` read returning the whole lane.
  - **Implementation**: `memory_repository.py` (protocol + both engines), `memory_service.py`.
  - **Testing**: Repository test on both engines.
  - **Success Criteria**: the read returns only `coding_reasoning` rows, whole.
- [ ] **Step 3.2**: Expose it on both faces
  - **Action**: Register the tool/route.
  - **Implementation**: `api_mcp/server.py`, `api_http/api.py`.
  - **Testing**: `tests/api_mcp/` and route-coverage tests.
  - **Success Criteria**: the tool is callable and returns the lane.
- [ ] **Step 3.3**: Prove `awaken` is unchanged
  - **Action**: Assert a chat agent's payload excludes the lane.
  - **Implementation**: extend the awaken tests with a seeded `coding_reasoning` row.
  - **Testing**: the payload's `shared.reasoning` is byte-identical with and without the lane present.
  - **Success Criteria**: the isolation is asserted, not assumed.

### Phase 4: Hermod command and load line
- [ ] **Step 4.1**: `/add-coding-reasoning` procedure
  - **Action**: A new Hermod command that drafts a pattern from `reasoning-pattern-template` and writes it.
  - **Implementation**: `procedures/add-coding-reasoning.md`, with a `## Storage Mechanics` seam section.
  - **Testing**: the overlay's procedure tests (compile + seam coverage).
  - **Success Criteria**: the command compiles for both backends and names its ops.
- [ ] **Step 4.2**: Backend ops
  - **Action**: Define the command's `§` ops in both backends.
  - **Implementation**: `storage-backends/db.md` (calls Munnin `insert` with the lane type) and `storage-backends/markdown.md` (writes the file).
  - **Testing**: the seam tests.
  - **Success Criteria**: both backends have the ops, and the DB one names the concrete `insert` call.
- [ ] **Step 4.3**: `§ load-coding-reasoning` points at the read
  - **Action**: Replace the "read it from the memory layer" prose with the concrete read call.
  - **Implementation**: `storage-backends/db.md`.
  - **Testing**: the seam tests.
  - **Success Criteria**: a coding awakening has a real source.

### Phase 5: Local import and end-to-end check
- [ ] **Step 5.1**: Import the lane into the local/dev store
  - **Action**: Run `import_shared` against a local DB.
  - **Implementation**: the existing importer entrypoint.
  - **Testing**: the lane row count matches the file's pattern count.
  - **Success Criteria**: the local store holds the lane.
- [ ] **Step 5.2**: End-to-end read
  - **Action**: Exercise the read the overlay will use, and re-check `awaken`.
  - **Implementation**: call the read tool against the imported store; call `awaken` for a chat agent.
  - **Testing**: the lane returns; the chat payload is unchanged.
  - **Success Criteria**: the lane loads end to end and the boundary holds.

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
- [x] **Step 1.1**: Add the `coding_reasoning` type to the enum and the pin
  - **Implementation Log**: `RecordType.coding_reasoning` added, with a docstring paragraph on why it is its own type; `SHARED_RECORD_TYPES` widened to five in the DDL's order.
  - **Testing Log**: the pin (`test_schema.py::test_the_declared_shared_types_match_the_schema_check`) failed with `At index 1 diff: 'coding_reasoning' != 'knowledge'` before the SQL matched, then passed after `0004`. The accepts test now covers five types.
  - **Success Criteria**: Pass.
  - **Tech Debts**: none.
  - **Result**: Done.
- [x] **Step 1.2**: SQLite migration `0004`
  - **Implementation Log**: `migrations/0004_shared_record_coding_reasoning.sql`, a rebuild modelled on `0002`. **Deviation from the plan worth recording**: `0002`'s column list predates `0003`'s `content_summary`, so a verbatim copy would have dropped that column on every existing row; the rebuild names and copies it too.
  - **Testing Log**: new `test_migrations.py::test_the_coding_reasoning_migration_preserves_content_summary` runs the file directly on a 0003-shaped store and asserts the value survives; the retrofit test updated for a fourth migration; row and FTS preservation already covered.
  - **Success Criteria**: Pass.
  - **Tech Debts**: the schema pin parsed the CHECK with a whitespace-sensitive split that a rebuild breaks; made whitespace-tolerant (assertion unchanged).
  - **Result**: Done.
- [x] **Step 1.3**: Postgres migration
  - **Implementation Log**: `migrations_postgres/0003_shared_record_coding_reasoning.sql`: `DROP CONSTRAINT` / `ADD CONSTRAINT` on `shared_record_record_type_check`, in place, no rebuild.
  - **Testing Log**: not run here. The Postgres suite skips without a URL (24 skipped), so the constraint swap is unverified in this environment.
  - **Success Criteria**: written, not runtime-verified.
  - **Tech Debts**: the Postgres migration is unexercised locally; it belongs to QA Handoff scope and the deploy path.
  - **Result**: Partial (code complete, not runtime-verified).
- [x] **Step 1.4**: `insert` accepts the type for shared scope
  - **Implementation Log**: acceptance follows from `SHARED_RECORD_TYPES` and the CHECK; `TEMPLATE_BY_RECORD_TYPE` gained `"coding_reasoning": "reasoning-pattern-template"`; the served docstrings (MCP `insert`, HTTP `insert`, both repositories) widened to name the new type.
  - **Testing Log**: `test_write_ops.py::test_insert_shared_scope_accepts_the_coding_reasoning_lane` round-trips a shared `coding_reasoning` insert; `test_template_versions.py` asserts the mapping set; full suite 527 passed, 24 skipped.
  - **Success Criteria**: Pass.
  - **Tech Debts**: none.
  - **Result**: Done.

### Phase 2:
- [x] **Step 2.1**: Parser for the coding-reasoning file
  - **Implementation Log**: `parse_coding_reasoning` added beside `parse_shared_reasoning`; both call `_patterns`, so the lane shares the level-3 shape and the embedded-UUID key rule.
  - **Testing Log**: `test_markdown_parser.py::test_parse_coding_reasoning_shares_the_pattern_shape`.
  - **Success Criteria**: Pass.
  - **Tech Debts**: `_patterns`' second argument is unused; left as found, out of scope.
  - **Result**: Done.
- [x] **Step 2.2**: Fifth read in `import_shared`, guarded
  - **Implementation Log**: the coding lane is read after core-reasoning and written as `RecordType.coding_reasoning`; absence logs and skips, like the profile. **Plan correction**: confirmed decision 3 (a distinct `stable_uuid` first component) is unnecessary: `_to_shared_record` already passes `record_type.value` as the second component, so a coding row and a universal row derive different uuids from the same key.
  - **Testing Log**: `test_fidelity.py::test_the_coding_lane_imports_and_stays_out_of_a_chat_awakening` imports the real 31 KB file, asserts the lane count matches the parsed file and the count map, and asserts the lane uuids do not intersect `shared.reasoning`.
  - **Success Criteria**: Pass.
  - **Tech Debts**: none.
  - **Result**: Done.

### Phase 3:
- [x] **Step 3.1**: The lane read
  - **Implementation Log**: `MemoryService.coding_reasoning()` returns the lane whole. **Plan simplification**: no repository op was needed. `query_shared(record_type=...)` already exists on both engines, so the planned "protocol + both engines" step collapsed to one service method.
  - **Testing Log**: `test_write_ops.py::test_the_coding_lane_is_readable_but_absent_from_a_chat_awakening`.
  - **Success Criteria**: Pass.
  - **Tech Debts**: none.
  - **Result**: Done.
- [x] **Step 3.2**: Expose it on both faces
  - **Implementation Log**: MCP tool `coding_reasoning` (read-only annotation, title "Read the coding-reasoning lane") and HTTP `GET /api/coding-reasoning`.
  - **Testing Log**: the pinned-surface tests updated (`test_tool_annotations.py` READ_ONLY, `test_route_coverage.py` EXPECTED_OPERATIONS 21 to 22, `test_twin_parity.py` data_tools 20 to 21).
  - **Success Criteria**: Pass.
  - **Tech Debts**: none.
  - **Result**: Done.
- [x] **Step 3.3**: `awaken` is unchanged
  - **Implementation Log**: nothing to change: `awaken` filters its universal layer by `record_type is reasoning`, and the lane is a different type. Asserted, not assumed.
  - **Testing Log**: `test_the_coding_lane_is_readable_but_absent_from_a_chat_awakening` (deterministic) and `test_fidelity.py::test_the_coding_lane_imports_and_stays_out_of_a_chat_awakening` (real file). Full suite 530 passed, 24 skipped.
  - **Success Criteria**: Pass.
  - **Tech Debts**: none.
  - **Result**: Done.

### Phase 4:
- [ ] **Step 4.1**: [pending]
- [ ] **Step 4.2**: [pending]
- [ ] **Step 4.3**: [pending]

### Phase 5:
- [x] **Step 5.1**: Import the lane into a local/dev store
  - **Implementation Log**: ran `import_shared` against the real markdown store (`~/.claude/@agent-memory`) into a fresh local SQLite DB. Counts: `reasoning: 32`, `coding_reasoning: 12`, `knowledge: 33`, `ras: 2`, `user_profile: 1`. The lane holds **12** patterns today; the project-context doc's "6" is from 2026-08-20.
  - **Testing Log**: the importer's log line and the returned count map agree; `repo.query_shared(record_type=coding_reasoning)` returns 12.
  - **Success Criteria**: Pass.
  - **Tech Debts**: a scratch DB was the target; the working local `data/valaskjalf-memory.db` was deliberately not touched.
  - **Result**: Done.
- [x] **Step 5.2**: End-to-end read
  - **Implementation Log**: `MemoryService.coding_reasoning()` returned 12, and `awaken("meta")` returned 32 universal patterns with **zero** uuid overlap against the lane.
  - **Testing Log**: the run's output; `test_fidelity.py` exercises the same path in-suite.
  - **Success Criteria**: Pass.
  - **Tech Debts**: none.
  - **Result**: Done.

---

## **QUALITY REVIEW**
*Filled by procedure Step 16 (delegated to `/analyze-code-quality` in embedded mode) after all execution phases are complete.*

- **Scope**: Munnin: `api_http/api.py`, `api_mcp/server.py`, `business_services/memory_service.py`, `content/loader.py`, `data_entities/memory_record.py`, `data_migrations/importer.py`, `data_migrations/markdown_parser.py`, `data_repositories/{sqlite,postgres}_memory_repository.py`, `migrations/0004_shared_record_coding_reasoning.sql`, `migrations_postgres/0003_shared_record_coding_reasoning.sql`; Hermod: `procedures/add-coding-reasoning.md`, `storage-backends/{db,markdown}.md`. Reconciled against `git diff --name-only` in both repos: no discrepancy (the untracked files are the new ones on the log).
- **Quality Standard**: not found in either repo (`**/quality-standard.md` resolves only in other projects); freeform analysis, Dimension 8 skipped.
- **Findings**: 0 Critical, 0 Medium, 5 Low.
  1. `src/munnin/api_http/api.py:254` E501 line too long (105 > 100).
  2. `src/munnin/data_repositories/postgres_memory_repository.py:129` E501 (105).
  3. `tests/data_entities/test_migrations.py:108` E501 (103).
  4. `src/munnin/api_mcp/server.py:202-215` the reflowed `insert` docstring breaks mid-sentence ("the universal RAS / triggers,").
  5. `src/munnin/data_migrations/markdown_parser.py:203` `_patterns`' `record_type` parameter is unused, so `parse_coding_reasoning` and `parse_shared_reasoning` are literally the same function (pre-existing; my change adds a third caller that passes an ignored value).
- **Fixed**: all five. Findings 1-4 wrapped or reflowed. Finding 5 removed `_patterns`' unused parameter, and I fixed **all five** call sites: the first pass fixed three and missed the internal caller in `parse_agent_core`, which the suite caught (28 failed), then 531 passed after the fix. `ruff check` clean.

---

## **QA HANDOFF**
*Filled by procedure Step 17 after Quality Review is resolved.*

- **Scope**: Munnin (store type + schema, importer, read tool) and Hermod (command, load line)
- **QA instrument**: Set up in Munnin: `qa/qa-map.md` present, R/I/A/O scripts documented, loop last run end to end 2026-08-21
- **Integration coverage**: NONE for this sweep — bench built, but the local stack is down (nothing listening on :8200). Phases 1.3 (Postgres migration) and 5.2 (end-to-end read) cross a real boundary and cannot run now; continued with [USER-NAME]'s knowledge that this ships with no integration coverage
- **Checklist**: `agent-memory-server/qa/checklists/coding-reasoning-lane.md`
- **Coverage split**: 9 automated rows (each naming its test) / 9 manual checks, of which 0 are UI-bound
- **Runtime verification**: **NOT DONE.** Next action: `/run-qa-test --checklist qa/checklists/coding-reasoning-lane.md` once the stack is up

---

## **POST-COMPLETION**
After all phases are executed, logged, and both **Quality Review** + **QA Handoff** are filled, move this plan to `plans/completed/`:
`mkdir -p ./plans/completed && mv ./plans/[this-file].md ./plans/completed/[this-file].md`
