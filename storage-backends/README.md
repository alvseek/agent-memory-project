# Storage-Backend Seam — Contract

Overlay procedures that touch **project memory** are **storage-agnostic**: each carries its *judgment* (heuristics, WAIT confirms, formats) in its body and delegates its *storage mechanics* (where and how project memory is physically read/written) to a swappable **backend**. This mirrors the memory core's seam (`control-files/procedures/memory/storage-backends/`) — one procedure "core", two concrete backends.

**Procedures are not the same as data.** Only project-**memory** access is seamed. A procedure that reads the *working project repo* (its docs, for a scan) or commits it with git is doing repo work, not memory storage, and is not seamed. That is why the push/pull family is out of scope: it persists the user's code, and delegating memory persistence to the core's `/push-memory`. `/project-wrap-up` carries exactly **one** op (`§ persist-store`), because its served form may not name an unserved `/push-all`.

## The two backends

- **[markdown.md](markdown.md)** — project memory lives as a markdown tree over git: the resolved `HOME` dirs (`CONTEXT_DIR`, `KNOWLEDGE_DIR`, `MAP_PATH`), a hand-maintained `context-index.md`, `cp` from templates.
- **[db.md](db.md)** — project memory lives in a **Hermod** store, reached through tool calls on the Hermod server. Implemented; it is the backend a served client composes onto.

## The seam (how a procedure connects to a backend)

1. **Marker**: every seamed procedure has exactly **one** `## Storage Mechanics` section — the swap point. It sits after the procedure body.
2. **Reference by name**: the procedure body calls storage operations abstractly as **`§ op-name`** (e.g. *"create the folder (§ ensure-context-dir)"*). It never spells out files or commands inline.
3. **Markdown resolution (now)**: the overlay compiler swaps the `## Storage Mechanics` body for `markdown.md → ## [procedure]`, so the installed command carries the concrete file mechanics. The `§` sigils are kept in the output as provenance.
4. **DB resolution (now)**: the Hermod server composes the same procedure body with `db.md → ## [procedure]` instead, so a served client gets tool calls where an installed command gets file mechanics.

## Substitution rule (for tooling)

Replace everything from the line **after** the `## Storage Mechanics` header up to (but not including) the next `## ` header or end-of-file. This is the single, unique swap region — see `seam.py::substitute_storage_mechanics`.

## Backend file structure

Each backend file is organized by procedure:

```
## [procedure-name]              e.g. ## update-project-context
### § op-name                    e.g. ### § ensure-context-dir
<concrete steps for this backend>
### § op-name
...
```

The op names are defined by each procedure's own core (they are procedure-scoped, not a global namespace). A backend **must** implement the same `§ op` set a procedure references — `markdown.md` with the git/file mechanics, `db.md` with the tools (or an explicit no-op + reason where the operation dissolves). A backend may also define `## all-procedures` (prose owed to every composed procedure) and a `## [component]` section for ops arriving via an inlined component.

## `seam.py` is a vendored duplicate

`seam.py` in this folder is a **copy** of the memory core's
`control-files/procedures/memory/storage-backends/seam.py`, vendored so the overlay stays
standalone (no path into the core checkout). It is a known duplication and a tech debt:
the intended end state is one shared package imported by the core compiler, Munnin and this
overlay. Until then, keep the two copies byte-identical and change both together.
