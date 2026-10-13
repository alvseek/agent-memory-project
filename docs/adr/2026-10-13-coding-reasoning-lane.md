# ADR-028: The Coding-Reasoning Layer Is a `coding_reasoning` Shared Record Type, Written by a Hermod Command

**Date**: 2026-10-13

**Status**: Accepted

**Extends**: ADR-027 (*Hermod's Project Store Is Valaskjalf's Records*). **Supersedes** the 2026-08-15 call recorded in the `coding-reasoning-layer.md` project context ("a scope argument on the one command, never a `/add-coding-reasoning` sibling").

---

## Problem

`coding-reasoning-memory.md` holds the reasoning patterns that only fire for a coding agent (patterns that name repo artifacts, plan logs, foreign code, or fleet teammates). It is hand-edited today, and Munnin's importer deliberately never reads it, so the layer has no representation in the database and stays absent when a coding agent awakens online.

It cannot simply be imported like the universal reasoning set: `awaken()` returns `shared.reasoning` to **every** agent, chat agents included, so putting coding patterns there would hand coding patterns to agents that have no use for them and undo the 2026-08-15 core/coding split.

---

## Decision

**We decided to**: give the layer its own record type. `shared_record` gains `record_type = "coding_reasoning"` with `project = NULL`; a Munnin read tool returns the lane; and a **Hermod** command, `/add-coding-reasoning`, is what writes it. The core's `/add-reasoning` is untouched.

**Why we chose this:**
- The type is the only marker that makes the chat-agent leak structurally impossible without changing Munnin's read rule. `awaken` selects the universal layer by `record_type is RecordType.reasoning`, so a distinct type can never match. A `project` marker on a `reasoning` row is **not** safe: the corpus-boundary predicate `(record_type <> 'knowledge' OR project IS NULL)` does not hide it, so it would leak.
- It keeps the layering the framework runs on: Munnin is the core (universal fleet memory), Hermod is project/coding. The type is the one core-vocabulary addition; the coding-specific *command* lives in the coding layer.
- The type name reads 1:1 with the file it represents (`coding-reasoning-memory.md`), so file, type and command are one term.

---

## What to Build (Requirements)

**Core Requirements:**
- `RecordType.coding_reasoning` plus its entry in `SHARED_RECORD_TYPES`, with the SQLite `CHECK` and both engines' migrations (SQLite `0004` table rebuild, Postgres in-place constraint swap) admitting it.
- `insert(scope="shared", record_type="coding_reasoning")` accepted, and template-gated against the same `reasoning-pattern-template` the `reasoning` type uses.
- An `import_shared` fifth read for `shared-memory/coding-reasoning-memory.md`, existence-guarded so a missing file skips quietly, with a `stable_uuid` first component distinct from `"shared"`.
- A Munnin read returning the whole lane.
- A Hermod `/add-coding-reasoning` command that writes the lane through Munnin's `insert`, with ops defined in both storage backends.
- Hermod's `§ load-coding-reasoning` calling that read.

**Success Criteria:**
- `awaken(domain)` output is unchanged for a chat agent: no coding row appears in `shared.reasoning`.
- The lane imports into the store and re-imports idempotently.
- `/add-coding-reasoning` writes a `coding_reasoning` shared row end to end.
- A coding awakening loads the lane instead of reporting it absent.

---

## Alternatives Rejected

- **`project` sentinel on `reasoning` rows**: the boundary predicate does not hide `reasoning` + `project`, so the lane would leak through `awaken` unless a core read rule changed.
- **`tags = ["coding"]` on `reasoning` rows**: no migration, but identity lives in metadata, which is easy to strip.
- **A Hermod `knowledge` corpus item**: stores reasoning as project context, the wrong corpus and the wrong load semantics.
- **Keeping the markdown file only**: no store change, but the served overlay has no file channel, so the layer stays absent online (the gap that started the work).
- **A scope branch on the core `/add-reasoning`**: puts a coding concept into Munnin's command surface, breaking Munnin = core. This is the call it supersedes; the 2026-08-15 reason was about a *core* sibling, whereas a Hermod command is a layer split, not a destination split.

---

**Full context**: [High Wizard plan 2026-10-13 agent-memory-project coding-reasoning-lane](../../plans/completed/2026-10-13-agent-memory-project-coding-reasoning-lane.md)

---

**ADR Template for Architecture Decision Records**

*This document serves as a SPECIFICATION that tells implementation agents WHAT to build. The implementation protocol (High Wizard/Quick Wizard) will figure out HOW to build it.*
