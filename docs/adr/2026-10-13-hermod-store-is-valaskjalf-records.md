# ADR-027: Hermod's Project Store Is Valaskjalf's Records

**Date**: 2026-10-13

**Status**: Accepted

**Extends**: ADR-023 (*The Overlay Storage-Backend Seam*), and **supersedes ADR-026**. Corrects two clauses elsewhere: the store-ownership sentence in ADR-024, and *"Hermod has no tenancy"* in ADR-025.

---

## Problem

ADR-026 put Hermod's project memory on **its own database**, a second one on the instance the memory store runs on. Three things were wrong with that.

The 2026-08-07 boundary frame says the opposite in one line: *"Valaskjalf, the storage base... holds ALL memory data. Both servers read/write it."* The store built in October kept project-keyed memory outside Valaskjalf, and the store's own docstring recorded the anomaly without acting on it: *"Munnin's `project` column is reserved and unused by Munnin."* Reserved is the tell; the column was already there for this.

The store also could not hold what the markdown it replaced already held. Its identity was `(project, scope, theme)` with no agent anywhere, while the markdown layout keeps private context per agent (`agent-<domain>/knowledge-base/<project>/`). Two agents holding a theme for one project had one row between them: 167 markdown entries became 164 rows, and the two that vanished were genuinely different documents.

And its tenancy was a gate rather than an identity, so nothing tied a caller to the rows they were reading.

## Decision

**We decided to**: make Valaskjalf's record tables the only home for project-keyed memory, and remove the store entirely.

A project-context entry is a `knowledge` record that carries a `project`. Which table holds it is which half of the pair it belongs to: a **shared** entry is a `shared_record` row, a **private** entry is a `memory_record` row, whose `agent_id` carries the owner the old table had no column for. The **orientation map** is a `shared_record` row titled `orientation-map`, one per project, which is why a project cannot have two.

The **tenant** is resolved from the verified token, not configured: the token's `(iss, sub)` is read against `user_identity`, exactly as Munnin resolves it, so the same Google account reads the same rows through either server. Hermod **issues no DDL**; the record tables have one owner and it is Munnin's migration runner.

**Why we chose this:**
- It is the frame the family already agreed, and the column it needs was already in the schema.
- `memory_record` is `shared_record` plus the owner, so the private half's agent axis arrives for free. The collision above disappears rather than being answered.
- One store means one corpus, one backup target, and one place a project's memory can be found, which is the boundary the served ops already assume.

## What to Build (Requirements)

**Core Requirements:**
- `hermod-server`: one record-backed repository behind the existing `ProjectRepository` Protocol, reading and writing `shared_record` / `memory_record`; both current repositories, both migration folders and both runners deleted.
- A tenant resolver reading `user_identity` by `(iss, sub)` and creating the account and the mapping on a first contact, mirroring Munnin's `TokenTenantResolver`. No configured user id exists.
- An explicit `agent` argument on every op that touches the private scope, in `db.md` and in the tool signatures; `shared` ignores it. The token names the person, the argument names the agent, and the two are orthogonal.
- The importer retargeted at records, with `uuid5` over `agent | project | scope | theme` so a re-run upserts, and `content_summary` filled from each entry's frontmatter.
- Munnin's **knowledge** reads gain `project IS NULL`; its episode, identity, reasoning, emotional and RAS reads are untouched.
- `hermod-deploy` repointed at the memory database, its volume removed, the `hermod` database dropped after the retarget is verified.
- `db.md` restated, ADR-026 marked superseded, ADR-024 and ADR-025 corrected.

**Success Criteria:**
- All 167 markdown entries and 7 maps import with nothing lost, the former collisions now distinct rows.
- Both engine suites green, Hermod's against SQLite and against a real PostgreSQL.
- An episode carrying a `project` is still returned by Munnin's reads, and a `knowledge` row carrying one is not.
- No file under `hermod-server` creates a table.

---

## Alternatives Rejected

- **A `record_type` of its own for project rows** (`context`): the schema would enforce the boundary rather than a convention, and it was rejected at cost, not on merit; it needs a table rebuild on `shared_record` because that table's CHECK admits only four types, where `project` already expresses the same thing.
- **Hermod's own `project_context` table** (the state ADR-026 built): two homes for one kind of memory, and it cannot represent two agents' private entries for one project.
- **Hermod's own table plus an `agent_id` column**: fixes the collision while keeping two homes, which is the frame's own objection.
- **A second database on Munnin's instance** (ADR-026 as written): keeps project memory out of Valaskjalf and puts two migration runners on one instance with nothing comparing them.
- **A separate PostgreSQL server for Hermod**: a second service to provision, back up and patch for a store that holds one row per theme.
- **A manually configured user id**: the same Google account must land on the same tenant in both servers, and a config value can drift from the login it is meant to mirror.
- **Munnin's filter applied fleet-wide**: it empties the episode index, because 728 of 770 episodes legitimately carry a `project`; the filter belongs on the reads where the leak is, which is knowledge.

---

**Full context**: [2026-10-13 Hermod store retarget plan](../../plans/2026-10-13-agent-memory-project-hermod-store-retarget.md)
