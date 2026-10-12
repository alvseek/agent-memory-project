# Map Orientation

Maintain a per-project index of orientation artifacts (READMEs, architecture docs, flow diagrams, ADRs, sub-project maps) with staleness + role tracking.

Map file: `shared-memory/[PROJECT-NAME]/context/orientation-map.md`. Format: [orientation-map-template.md]([path-to-agent-memory-project]/templates/orientation-map-template.md).

*How* the map is physically read and written is delegated to the active **storage backend** (see [Storage Mechanics](#storage-mechanics)).

---

## Arguments

`$ARGUMENTS`

- `/map-orientation` — **Load mode** (default, read-only). Load map + mtime check + write only if entries flagged stale. If map missing: report and exit.
- `/map-orientation create` — **Create mode**. Full scan + classify + write. For first-time setup.
- `/map-orientation --session-touched [path1,path2,...]` — **Update mode**. Update the named entries' verification. Silent no-op if map missing.
- `/map-orientation --rescan` — **Rescan mode**. Full rescan preserving status/verified_by where paths unchanged. No-op if map missing.
- `/map-orientation [project-name]` — **Project override**. Combines with any mode; targets the named project instead of cwd detection.

---

## Step 1: Prelude (all modes)

1. **Identify project** — match cwd against known project mappings (`shared-memory/[project]/` existence + `shared-memory/integrations/external-integrations.md` task-system mapping). If a project-name arg is passed, use it. If neither: skip silently.
2. **Compute central map path** — `[AGENT-MEMORY-PATH]/shared-memory/[PROJECT-NAME]/context/orientation-map.md`. Record `CENTRAL_MAP_EXISTS`.
3. **Resolve the home** — apply the [HOME contract component]([path-to-agent-memory-project]/components/home-contract.md). `MAP_PATH` and `CONTEXT_DIR` are the active values. `MAP_EXISTS` = whether `MAP_PATH` exists (**§ map-exists**).

> **All mode blocks below operate on `MAP_PATH` / `CONTEXT_DIR`.** Where a block names `shared-memory/[PROJECT-NAME]/context/orientation-map.md`, read it as `MAP_PATH`.

Then jump to the matching mode block below — read only that block.

---

## Load Mode (bare arg, default)

> Read-only by default. Writes only if mtime check flags entries stale.

### L1: Branch on existence

- `MAP_EXISTS = false` → report `"No orientation map for [PROJECT-NAME] yet — use '/map-orientation create' to scan and create."` and exit.
- `MAP_EXISTS = true` → continue.

### L2: Read map + apply role filter

Read the map (**§ read-map**). For each entry, apply [Role Filter Rules](#role-filter-rules) — load only entries the current agent's role qualifies for. For each `orientation-map-link` entry that passes the filter: ALSO read the linked child map (same rules apply). If a linked child map is missing: flag the parent entry with `[child map missing — run /map-orientation --rescan when ready]` and continue.

### L3: mtime check

For each loaded entry, compare the file's actual mtime to its `last_verified`:

```sh
stat -c %Y "[entry-path]"
```

- `file_mtime > last_verified` → set `status: unverified` + add `staleness_reason: "mtime > last_verified"`.
- File missing → set `status: obsolete` + `notes: "file no longer exists at path"`. Don't delete (breadcrumb).

### L4: Write if changed

If L3 flagged any entries: write the updated map back (**§ write-map**). Else: skip the write.

### L5: Report

```
Orientation map loaded: [MAP_PATH]
  - N entries total
  - M unverified (need agent verification on next relevant task)
  - K stale-but-valuable | L obsolete
  - P sub-map links: [filenames]
```

---

## Create Mode (`create` arg)

> Explicit user action. Triggered only by `create` arg. Never runs automatically.

### C1: Branch on existence

- `MAP_EXISTS = true` → confirm with [USER-NAME]: *"map already exists, did you mean `--rescan`?"* Wait for confirmation.
- `MAP_EXISTS = false` → ensure the context dir exists (**§ ensure-context-dir**), continue.

### C2: Scan for orientation artifacts

**Scan scope**: project root (depth 1), **all `**/docs/` folders recursive** (any depth, bounded by the skip-list below), optional submodule roots (depth 1 each). The recursive `**/docs/` glob is what catches co-located module docs (e.g. `src/orders/docs/`) per the Placement Contract.

> **Placement Contract**: docs follow **scope = location** — module docs co-locate in `[module]/docs/`; cross-cutting docs live at the **Lowest Common Ancestor** of what they interconnect (ADRs bias to root `/docs/adr/`). This map is the **navigation layer** — it indexes docs wherever they physically sit and is where flow/playbook ordering is imposed without moving files.

**File patterns** (case-insensitive):
- `README*.md`
- `ARCH*.md`
- `ADR-*.md` or `*-adr.md`
- `*.mmd`, `*.mermaid`
- `*.md` under any `docs/flows/` folder (carry `doc_type: flow` frontmatter)
- `*.md` under any `docs/domain/` folder (carry `doc_type: domain` frontmatter)
- `*.md` under any `docs/architecture/` folder (carry `doc_type: architecture-map` / `architecture-overview` frontmatter)
- `CONTRIBUTING.md`, `GLOSSARY.md`, `CHANGELOG.md` (optional, `type: other`)

**Skip**: `.git/`, `node_modules/`, `vendor/`, `build/`, `dist/`, `.next/`, `target/`, `bin/`, `obj/`, hidden folders (except `.github/`).

**Submodule boundary rule**: the `**/docs/` glob will surface `docs/` folders that live **inside a git submodule** (path under a `.gitmodules` entry, or a nested `.git` file). A submodule is a separate repo whose docs have a natural home in its own map — do **NOT** silently fold them into the root project map. When a discovered `docs/` is inside a submodule, ASK [USER-NAME]:

> *"`docs/` at `[path]` is inside submodule `[name]`. Index it via **A) a sub-map inside the submodule** (`[sub-path]/orientation-map.md` — ships with the submodule on standalone clone), or **B) directly in the root project map**?"*

This is the same A/B placement choice as [C3](#c3-detect-sub-projects) (sub-map inside sub-project vs root). Default recommendation: **A** for real git submodules (keeps the map with the repo that owns the docs); **B** for small projects that prefer a single flat root map. In-project module docs that are NOT inside a submodule (e.g. `src/orders/docs/`) are indexed directly in the root/nearest map with no ask.

### C3: Detect sub-projects

**Sub-map triggers** (any): `.gitmodules` at root; sub-folder under `apps/`, `services/`, `packages/`, `submodules/` with ≥5 orientation docs.

For each detected, ask user *"Sub-project `[path]` has N orientation docs. Create sub-map?"* with placement options:

- **A) Inside the sub-project**: `[sub-path]/orientation-map.md` — fits git submodules and self-contained sub-projects; the map ships with the sub-project (standalone clones get it too). No filename suffix needed.
- **B) Sibling to root map**: `shared-memory/[PROJECT-NAME]/context/orientation-map-[name].md` — fits non-submodule sub-folders; everything stays under the parent's `context/`. Filename suffix required to disambiguate from root.
- **No** → docs stay in root map.

If A or B:
- Recursive scan within sub-project boundary (same C2 patterns).
- Write sub-map at the chosen location.
- Add `type: orientation-map-link` entry to the ROOT map with `child_map` as a path relative to the root map's folder:
  - A) `child_map: ../../../[sub-path]/orientation-map.md` (three `../` to climb out of `shared-memory/[PROJECT-NAME]/context/` to the project root, then descend into the sub-project).
  - B) `child_map: orientation-map-[name].md` (same folder, filename only).

**One-way reference rule**: parent map → child map via `orientation-map-link`. Child maps DO NOT reference the parent. A sub-map is a self-contained orientation view of its own scope; standalone consumers (e.g., someone cloning just the submodule) should not need the parent to use it.

### C4: Extract purpose per file

For each file, extract a 1-line purpose:
- **Markdown**: first non-trivial paragraph after the title heading.
- **Mermaid**: first comment block, or diagram title.
- Failure → `[unverified - needs read]`.

Use `head -20` / first 500 chars only. Do NOT read full file content.

### C5: Classify type + scope + roles (heuristic)

**Type** (path + filename + frontmatter — **match top-to-bottom; a specific `doc_type` wins over a folder fallback**):

| Pattern | Type |
|---|---|
| `*.md` with `doc_type: 7q-readme` frontmatter | `7q-readme` |
| `README*.md` with 7Q structure (≥4 of 7 questions present) | `7q-readme` (fallback for READMEs without `doc_type`) |
| `README*.md` without 7Q structure | `other` (note: "non-7Q README") |
| `ARCH-map.md` or `architecture-map.md` | `architecture-map` |
| `ARCH-*.md` (domain/overhead/governance) | `architecture-overview` |
| `*.mmd`, `*.mermaid` | `flow-diagram` |
| `*.md` with `doc_type: flow-journey-map` frontmatter | `flow-journey-map` |
| `*.md` with `doc_type: flow` frontmatter (or other `docs/flows/` `*.md`) | `flow-diagram` |
| `*.md` with `doc_type: domain-context-map` frontmatter | `domain-context-map` |
| `*.md` with `doc_type: domain` frontmatter (or other `docs/domain/` `*.md`) | `domain-model` |
| `*.md` with `doc_type: architecture-map` frontmatter | `architecture-map` |
| `*.md` with `doc_type: architecture-overview` frontmatter (or other `docs/architecture/` `*.md`) | `architecture-overview` |
| `ADR-*.md` or `*-decision.md` | `adr` |
| Sub-map reference (from C3) | `orientation-map-link` |
| Anything else | `other` |

**Scope + Roles** (path heuristic, editable after):

| Path | Scope | Roles |
|---|---|---|
| Root docs (`README.md`, `docs/architecture/*`, `docs/decisions/*`) | `shared` | `[]` |
| `apps/api/`, `backend/`, `server/`, `api/` | `role-private` | `[backend]` |
| `apps/web/`, `frontend/`, `client/`, `web/` | `role-private` | `[frontend]` |
| `apps/mobile/`, `mobile/`, `ios/`, `android/` | `role-private` | `[mobile]` |
| `apps/admin/`, `admin/` | `role-private` | `[admin]` |
| `docs/integration-*`, `docs/contracts/`, `*-contract.md` | `cross-readable` | best guess from path |
| Ambiguous | `shared` (note: "auto-classified — verify scope") |

### C6: Write map (+ sub-maps)

Create the map from [orientation-map-template.md]([path-to-agent-memory-project]/templates/orientation-map-template.md) (**§ create-map**). Populate frontmatter:

```yaml
---
project: "[PROJECT-NAME]"
description: "..."
created: "[TODAY-DATE]"
last_full_scan: "[TODAY-DATE]"
---
```

Per entry initial values:
- `status: unverified`
- `last_verified: ""` + `verified_by: ""` + `update_trigger: ""`
- `notes: <1-line purpose from C4>`
- `scope` + `roles`: from C5

Write each sub-map (from C3) to its chosen path (A: inside sub-project, B: sibling to root). Root map gets the `orientation-map-link` entries with `child_map` resolved per the placement choice.

### C7: Report

```
Orientation map created: [MAP_PATH]
  - N entries total (all unverified — will verify as future tasks touch their scope)
  - P sub-map links: [filenames]
```

---

## Update Mode (`--session-touched [paths]` arg)

> Internal to `/wrap-up`. Silent — no user-facing report.

### U1: Branch on existence

- `MAP_EXISTS = false` → silent no-op. Exit.
- `MAP_EXISTS = true` → continue.

### U2: Read map

Read the map into memory (**§ read-map**).

### U3: Update touched entries

For each path in the arg:
- Find matching entry (or add new entry if not present).
- Set `last_verified: [TODAY-DATE]`.
- Set `verified_by: [current-agent-role] / [session context]`.
- Confirm status (`useful` / `stale-but-valuable` / `obsolete`) — auto-set if clear from session context, else prompt agent.
- Update `notes` if session generated relevant info.

### U4: Write updated map

Write back (**§ write-map**). No report — `/wrap-up` aggregates results in its final summary.

---

## Rescan Mode (`--rescan` arg)

> Explicit refresh after major restructure. Preserves human-verified state where paths unchanged.

### R1: Branch on existence

- `MAP_EXISTS = false` → report `"No map to rescan — run '/map-orientation create' first."` and exit.
- `MAP_EXISTS = true` → continue.

### R2: Snapshot existing state

Read the current map (**§ read-map**). Capture `(path → {status, last_verified, verified_by, update_trigger, notes})` per entry — this is what we preserve.

### R3: Scan + classify

Execute **C2 → C3 → C4 → C5** as in Create Mode.

### R4: Merge

For each newly-scanned entry:
- **Path matches snapshot** → preserve snapshot's `status`, `last_verified`, `verified_by`, `update_trigger`. Update `notes` only if newly extracted purpose differs.
- **Path is new** → initialize as in C6 (unverified, blank metadata).

For each snapshot entry whose path was NOT scanned:
- Mark `status: obsolete` + `notes: "file no longer exists at path (rescan)"`.

### R5: Write merged map

Write back (**§ write-map**). Update `last_full_scan: [TODAY-DATE]`.

### R6: Report

```
Orientation map rescanned: [MAP_PATH]
  - N entries total | A added | O obsoleted | P preserved
```

---

## Role Filter Rules

Used by **Load Mode L2** when reading entries:

- `scope: shared` → load (everyone).
- `scope: role-private` → load if current agent's role ∈ `roles`, else skip.
- `scope: cross-readable` → load if current agent's role ∈ `roles` OR current agent is Architect or QA.
- **Architect / QA exception** — both cross-read all entries regardless of scope.
- **Single-role projects** (e.g., agent-memory framework) — all entries get `scope: shared, roles: []`. Filter is a no-op.

---

## Integration With Other Procedures

- **/awaken-agent** — calls `/map-orientation` (bare, load-only) after project detection.
- **/wrap-up** — calls `/map-orientation --session-touched [paths]` for orientation docs the session touched. Silent no-op if map missing.
- **/update-project-context** — preferred path when a session DISCOVERED an entry's status is wrong. Direct edit; mtime check picks it up on next awakening.

---

## Anti-Patterns

1. **Marking entries `useful` because they exist.** Useful = "verified accurate and future tasks will rely on it." Existence ≠ verification.
2. **Bloating the map with every markdown file.** Map covers ORIENTATION artifacts (README/architecture/flow/ADR/cross-cutting). Implementation docs, change logs, meeting notes belong elsewhere.
3. **Flattening submodule docs into the root map when sub-map makes sense.** ≥5 docs under a sub-folder → sub-map + `orientation-map-link` from root.
4. **Auto-creating child maps when parent's `orientation-map-link` points to missing file.** Flag the parent entry and let user trigger `--rescan` when ready.

---

## Storage Mechanics

The operations referenced above — **§ map-exists**, **§ ensure-context-dir**, **§ read-map**, **§ write-map**, **§ create-map** — are defined by the **active storage backend**:

- **Markdown (native)** — follow `storage-backends/markdown.md` → its `map-orientation` section.
- **DB (Hermod)** — the equivalents live in `storage-backends/db.md` → its `map-orientation` section (not yet implemented).

See the seam contract at `storage-backends/README.md` for how this swap works.
