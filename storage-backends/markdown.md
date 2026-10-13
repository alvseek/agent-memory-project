# Storage Backend — Markdown (git tree)

Concrete storage mechanics for the **native markdown-over-git** world. Each `## [procedure]` section defines the `§ op`s that procedure references. See the [seam contract](README.md).

> **Paths** resolve through the [HOME contract component](../components/home-contract.md): `CONTEXT_DIR` and `KNOWLEDGE_DIR` (central by default, a localized project's values otherwise). Where an op names a central path, read it as the resolved HOME value — identical for non-localized projects, in-project for localized ones.

---

## update-project-context

### § ensure-context-dir

Create the scope dir if it is missing (resolve `CONTEXT_DIR` for shared, `KNOWLEDGE_DIR` for private):

- Shared: `mkdir -p [AGENT-MEMORY-PATH]/shared-memory/[project-name]/context`
- Private: `mkdir -p [AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]`

### § list-context-entries

List the `*.md` files in the scope dir (exclude `context-index.md`). A file whose name matches the theme is an existing entry to update; no match means a new entry. The same listing answers the collision check in the Move sub-flow.

### § read-context-entry

Read `[scope-dir]/[theme].md` with the Read tool.

### § create-context-entry

Create the entry at the scope path **with the structure the template shows** — the fenced block below the template's `template_version` line — filling the frontmatter and every placeholder:

- Shared: `[AGENT-MEMORY-PATH]/shared-memory/[project-name]/context/[theme].md`
- Private: `[AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]/[theme].md`

> **The template's `template_version` line sits outside that block.** That makes the stamp template metadata rather than entry content, so a file built from the block never carries it and there is nothing to strip afterwards.

### § update-context-entry

Write the updated content back to `[scope-dir]/[theme].md`.

### § move-context-entry

Copy the entry **verbatim** (same template) from the source scope to the target one. A **promote** goes private → shared; a **demote** goes shared → private:

- **Promote**: `cp [AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]/[theme].md [AGENT-MEMORY-PATH]/shared-memory/[project-name]/context/[theme].md`
- **Demote**: `cp [AGENT-MEMORY-PATH]/shared-memory/[project-name]/context/[theme].md [AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]/[theme].md`

> **Partial-failure cleanup.** A move is not atomic at the filesystem level: it is this copy, then the source delete (**§ delete-context-entry**), then both index updates (**§ update-context-index**). If a step fails partway:
> - **After the copy, before the delete**: both files exist. Delete the duplicate (the source one).
> - **After the delete, before the index updates**: the file is moved but the indexes are inconsistent. Finish the index updates.
>
> If any step fails, report the partial state to the user and ask before retrying.

### § delete-context-entry

Remove the entry from its scope:

- Shared: `rm [AGENT-MEMORY-PATH]/shared-memory/[project-name]/context/[theme].md`
- Private: `rm [AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]/[theme].md`

### § check-entry-size

Count the lines in the written file.

- **Under 1000** → done.
- **Over 1000** → split: create one file per distinct sub-theme (each with its own frontmatter and tags), remove the original, then index every new file (**§ update-context-index**).

### § update-context-index

Edit the scope-aware `context-index.md`:

- Shared: `[AGENT-MEMORY-PATH]/shared-memory/[project-name]/context/context-index.md`
- Private: `[AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]/context-index.md`

If it does not exist, create it with the header `# [project-name] Project Context`. Add or update the entry —

```
- [theme.md](theme.md) — description (tags: tag1, tag2, tag3)
```

— and for a move, delete the line from the private index and add it to the shared index.

---

## load-project-context

### § list-context-entries

Read the shared index (`CONTEXT_DIR/context-index.md`) and scan the private layer (`KNOWLEDGE_DIR` project subfolders, excluding `research/`) for its `context-index.md`. Parse each entry together with its scope marker (`[shared]` / `[private]`). A missing or empty layer is skipped silently.

### § read-context-entry

Read the selected entry file(s) from their source-layer path:

- Shared: `[AGENT-MEMORY-PATH]/shared-memory/[project]/context/[theme].md`
- Private: `[AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project]/[theme].md`

---

## map-orientation

### § map-exists

Test whether `MAP_PATH` exists (the resolved HOME value). A localized project whose `MAP_PATH` is missing is caught by `agent-memory-local`'s reachability guard.

### § ensure-context-dir

`mkdir -p [CONTEXT_DIR]` (the resolved HOME `CONTEXT_DIR`).

### § read-map

Read `MAP_PATH` with the Read tool.

### § write-map

Write the map back to `MAP_PATH`.

### § create-map

Write `MAP_PATH` **with the structure the template shows** — the fenced block below the template's `template_version` line — then populate its frontmatter (`project`, `description`, `created`, `last_full_scan`), replace the example entries with the project's real artifacts, and delete the Customization Notes section.

> **The template's `template_version` line sits outside that block,** so a map written from the block never carries it.

---

## awaken-coder

### § awaken-coder-payload

No call, and nothing fetched: this backend's awakening set is the files the core awakening already read, and each op below names the file that answers its part. The one thing that is *not* the core's is the map, which `§ load-maps` reads. A markdown awakening therefore costs no tool call at all — the ops under this heading are file reads.

### § load-coding-reasoning

Read `[AGENT-MEMORY-PATH]/shared-memory/coding-reasoning-memory.md` into your own context (silently skip if missing).

### § load-context-indexes

Read the shared context index (`CONTEXT_DIR/context-index.md`) and the private context index (`KNOWLEDGE_DIR/context-index.md`) — the resolved HOME values — silently skipping whichever is missing.

### § check-fleet-roster

Test for `[AGENT-MEMORY-PATH]/shared-memory/[project]/fleet-agents.md`. Present → the project has a fleet; absent → skip the fleet pointer.

### § select-project-episode

From the episodic index the core returned, take the newest entry **per project** in the set — the session's own repository first — then read each body from `[AGENT-MEMORY-PATH]/agent-[domain]/episodes/[filename]` with the Read tool. A project in the set with no entry is left out rather than filled with the newest overall's, so the report carries one carry-forward per repository.

### § load-maps

Read each project's `MAP_PATH` with the Read tool, silently skipping a project that has none. The resolved project's is the HOME value; a related repository's is the same path under its own project name (`[AGENT-MEMORY-PATH]/shared-memory/[project]/context/orientation-map.md`). Never create one here — that is `/map-orientation create`'s job.

---

## add-coding-reasoning

### § read-coding-lane

Read `[AGENT-MEMORY-PATH]/shared-memory/coding-reasoning-memory.md` into your own context (silently skip if missing).

### § template

The reasoning-pattern block format → read `[AGENT-MEMORY-PATH]/control-files/procedures/memory/resources/reasoning-pattern-template.md`.

### § generate-uuid

- **Windows**: `powershell -c "[guid]::NewGuid().ToString()"`
- **Linux/macOS**: `uuidgen` or `cat /proc/sys/kernel/random/uuid`

### § persist-coding-reasoning

Append the completed pattern as a level-3 (`###`) block to `[AGENT-MEMORY-PATH]/shared-memory/coding-reasoning-memory.md`, under an existing `## ` grouping. Transfer it with `copy-lines.sh` rather than retyping it, so the bytes arrive exactly.

## project-wrap-up

### § persist-store

Execute `/push-all <mode>` — one call covering the agent-memory store and the working project together. Its memory half captures the writes the Step 1 project push ran too early to include; its project half captures what Steps 2–3 wrote.
