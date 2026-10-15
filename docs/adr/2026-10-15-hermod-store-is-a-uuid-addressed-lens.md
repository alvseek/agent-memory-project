# ADR-030: Hermod's Project Store Is a Lens Over the Memory Rows, Addressed by an Assigned UUID

**Date**: 2026-10-15

**Status**: Accepted

---

## Problem

Hermod's project store exposed the markdown backend's shape as tool arguments: a layer passed as a `scope` value beside a conditionally required `agent`, an entry addressed by `(project, scope, theme)`, an existence check the read already answered, a size check the write already enforced, and a uuid derived from the identity that no caller ever saw. Each of those made the store a second writer of rows the memory layer already writes, with its own rules for the same fields.

---

## Decision

**We decided to**: make the project store a lens over the memory layer's records, with per-layer primitives addressed by an assigned uuid, and delegate every uuid-addressed read and write to the memory layer.

Hermod keeps discovery and creation: the two lists, the two creates, the two direction ops and the three map ops, with the coding awakening as a read. The uuid is assigned at insert and returned by every op a caller addresses by, the layer vocabulary is `shared` / `agent`, the theme is a display name rather than a key, and `live` means both lifecycle flags null. Reading a body, editing it, editing its metadata and retiring it are the memory layer's `get`, `edit` family, `edit_metadata` and `soft_delete`, which already locate these rows by uuid and needed no change to do so.

**Why we chose this:**
- One implementation per rule, because the duplicated writes were the entanglement the surface had acquired.
- A uuid is the only handle that survives a direction change, and naming a row is what makes delegation possible at all.
- The memory layer's browse and search exclude project-scoped knowledge rows by design, so a list remains the only door to them, and that list is the one thing the lens must keep.

---

## What to Build (Requirements)

**Core Requirements:**
- The ops: `list_shared_context`, `list_agent_context`, `create_shared_context_entry`, `create_agent_context_entry`, `promote_context_entry(uuid)`, `demote_context_entry(uuid, agent)`, `read_map`, `create_map`, `update_map`, and the awakening's payload.
- The assigned uuid, returned by both lists, both creates, both direction ops and the awakening's `context_index` rows.
- `db.md`'s op definitions naming the memory layer's tools for read, body edit, metadata and delete, with `§ map-exists` and `§ check-entry-size` resolving to no action.
- The vocabulary `shared` / `agent` across the procedures, both backend docs and the templates, with the entry template's stamp bumped.

**Success Criteria:**
- No Hermod op writes a body, a metadata field or a lifecycle flag.
- A row created through the lens is readable, editable and retirable through the memory layer, by the uuid the lens returned.
- The served face matches the checkout, and the store's tests pass with the database paths exercised in CI.

---

## Alternatives Rejected

- **The natural key as the address**: the caller is a language model, and a name it can state and have checked in a transcript is a better handle than a value it must copy exactly.
- **A partial unique index on the natural identity**: it would have moved the one-row-per-theme rule into a schema constraint in a third repository, and the duplicate it prevents is an accepted outcome.
- **A self-contained store with its own read, edit and delete**: three writes implemented twice, and one metadata field with two rule-sets.
- **A create that revives a retired row of the same theme**: retired rows are left alone, and a re-captured theme starts a new row.

---

**Full context**: [High Wizard plan](../../plans/2026-10-15-agent-memory-project-hermod-context-surface.md)

---

**ADR Template for Architecture Decision Records**

*This document serves as a SPECIFICATION that tells implementation agents WHAT to build. The implementation protocol (High Wizard/Quick Wizard) will figure out HOW to build it.*
