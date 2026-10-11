# Storage Backend — DB (Hermod)

**Declared, not implemented.** This file exists so the seam has two sides; it carries no
mechanics yet, and nothing serves the overlay with it. `markdown.md` is the only working
backend until a Hermod store exists.

**Target**: a project store for project-keyed memory (context, orientation map), owned by
the overlay's own server or a co-hosted Hermod+Munnin server. The store's shape is not
decided, so the mechanics below are deliberately absent — writing them now would invent a
schema this backend does not yet target.

## Ops each procedure must implement here

The op set is fixed by the procedures; only the mechanics are this backend's to choose.
Some will resolve to explicit no-ops, exactly as the memory core's db backend no-ops its
derived index, directory and size steps.

### update-project-context

- `§ ensure-context-dir` — no directory concept expected
- `§ list-context-entries` — select the project's context entries
- `§ read-context-entry` — fetch one entry
- `§ create-context-entry` — insert an entry
- `§ update-context-entry` — edit an entry
- `§ move-context-entry` — change an entry's scope (private → shared)
- `§ delete-context-entry` — tombstone an entry
- `§ check-entry-size` — no length cap expected
- `§ update-context-index` — derived; expected no-op

### load-project-context

- `§ list-context-entries` — select context entries across both scopes
- `§ read-context-entry` — fetch the selected entries

### map-orientation

- `§ map-exists` — whether the project has a map
- `§ ensure-context-dir` — no directory concept expected
- `§ read-map` — fetch the map
- `§ write-map` — edit the map
- `§ create-map` — insert the map

### awaken-coder

- `§ load-coding-reasoning` — the coding-only reasoning layer (never part of Munnin's shared import)
- `§ load-context-indexes` — the project's context index projection
- `§ check-fleet-roster` — whether the project has a roster
- `§ select-project-episode` — the newest episode whose project is in the resolved set, body by uuid
