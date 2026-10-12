# ADR-024: The Artifact-Generation Family Leaves the Overlay, and the Overlay Gets a Served Form

**Date**: 2026-10-12

**Status**: Accepted

**Extends**: ADR-012 (*Memory Core / Coding-Skill Decoupling*), ADR-020, ADR-021 and ADR-022 (the family splits) and ADR-023 (the overlay storage-backend seam).

---

## Problem

The coding overlay holds two concerns that change for different reasons. The first is the shell plus project memory, which every coding session needs. The second is the artifact-generation family, which produces documentation and container files on demand: it references only itself and the orientation map, and it owns ADR-004's docs-placement contract, so it is the overlay's largest self-contained part and the least related to memory.

Separately, the overlay has no served form at all. The memory core has been served by Munnin since 2026-08, so a plain chat client can awaken from it, while a client that cannot install markdown gets nothing from the overlay. ADR-012 named this as the target delivery model and left it unbuilt.

---

## Decision

**We decided to**: extract the artifact-generation family into its own repo, `agent-memory-doc` (`hermod-doc`), move `dockerize` into `agent-memory-wizards`, and give what remains a served form through `hermod-server`, which mirrors the Munnin server's composition pipeline without its HTTP face and owns the project store ADR-023 deferred.

`hermod-server` serves the overlay alone. It does not connect to Munnin: the client composes the two layers itself, so the memory write stays Munnin's and hermod holds no memory credential. Its registry is expressed as a source list rather than a single content root, which is what makes a Munnin proxy a later one-provider addition rather than a rewrite.

**Why we chose this:**
- One repo per concern, following the pattern ADR-020, ADR-021 and ADR-022 each set.
- The extraction is nearly free: the family's components and templates each have exactly one consumer, so they travel with it and leave no shared asset behind.
- The served form is the half of ADR-012's target model that has never existed, and the project store is already specified as a per-op checklist, so the server has a defined job rather than an invented one.

---

## What to Build (Requirements)

- New public repo `agent-memory-doc`: six procedures (`generate-readme`, `generate-docs`, `generate-architecture-docs`, `generate-domain-docs`, `generate-flow-docs`, `discovery-contract`), two components and six templates, with its own copy-and-adapted compile and install tooling. The adapted compiler carries **no seam stage**, which is the shape the wizards, fleet and local copies already have and the reason none of them ships a `seam.py`.
- `dockerize` moves into `agent-memory-wizards`, crossing the boundary ADR-021 drew; the wizards' `MIGRATION.md` gains a dated entry recording the arrival and naming this ADR as the family model's record.
- The seven producer clauses are dropped from `map-orientation` and its template, and `discovery-contract`'s map references are reworded to name the map path rather than another repo's procedure, so neither repo names the other.
- `hermod-server`: FastMCP mounted at `/mcp` on a Starlette app carrying one `/health` route; local mode only, with no issuer and no `/api`; the content root pinned as a submodule with an env override; the seam imported by path; the inliner and discovery carried, with a fidelity test comparing mechanic accounting against the overlay's own compiler; a registry shaped as a source list.
- The project store, implementing `storage-backends/db.md`'s ops for the four seamed procedures, and `§ persist-store` on `project-wrap-up` resolving to `/push-all` on markdown and `/push-project` on the db. Two tables — `project_context`, addressed by `(project, scope, theme)`, and `orientation_map`, keyed by `project` — behind a migration runner and a `ProjectRepository` Protocol, with one MCP tool per op. Two ops resolve to **no-ops** and say so: a store has no directories (`§ ensure-context-dir`) and the context index is a projection of the rows (`§ update-context-index`). An entry over **1000 lines** is **refused** rather than split — the markdown backend's threshold, with the opposite remedy, because a row has no second file to divide into.

**Success Criteria:**
- The overlay holds 9 procedures; `hermod-doc` holds the 6 with their 2 components and 6 templates; every installer, manifest and test across the three repos is consistent
- `hermod-server` runs locally: a client connects over `/mcp`, reads a composed procedure and the two remaining templates, and `/health` answers
- A project context entry round-trips through the server's tools
- The unserved procedures are absent from the prompt list, and no served prompt carries an unresolved op

---

## Alternatives Rejected

- **Keep the family in the overlay**: couples a documentation concern to a repo whose job is the shell and project memory.
- **Delete the family**: it owns the docs-placement contract and produced the store's own `docs/README.md`, `docs/architecture/agent-memory.md` and `docs/flows/journey-map.md`.
- **Extract it into `agent-memory-wizards`**: reverses ADR-021's boundary, which moved these procedures out and deliberately left them falling back to the core's `wait-options`.
- **Let `hermod-server` join Munnin now** (static fetch or full proxy): buys nothing today, since the one shared item is not in Munnin's store, and costs a credential plus an availability dependency in a process that reads the working repo. **What not joining costs is now visible in three ops**: `§ select-project-episode` (episodes are Munnin's records), `§ load-coding-reasoning` and `§ check-fleet-roster` all resolve to a delegation to the memory layer rather than a store read. That is the strongest single argument for revisiting this decision, and it is recorded rather than hidden.
- **Give `hermod-server` a FastAPI `/api` face**: nothing calls it, and the MCP face plus `/health` is the whole surface this phase needs.
- **Copy the seam into `hermod-server`**: a third copy of a file whose own header asks for one home, when loading it by path costs nothing.
- **Exclude `push-all` and `pull-all` and repoint `project-wrap-up`**: the installed markdown form would then never push the memory it just wrote, and the completion gate would report a store that was never saved.

---

**Full context**: [High Wizard plan](../../plans/completed/2026-10-12-agent-memory-project-hermod-server.md)

---
