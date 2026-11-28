# Storage Backend — Markdown (git tree)

Concrete storage mechanics for the **native markdown-over-git** world. Each `## [procedure]` section defines the `§ op`s that procedure references. See the [seam contract](README.md).

> **Paths** resolve through the [HOME contract component](../../components/home-contract.md): `CONTEXT_DIR` and `KNOWLEDGE_DIR` (central by default, a localized project's values otherwise). Where an op names a central path, read it as the resolved HOME value — identical for non-localized projects, in-project for localized ones.

---

## update-project-context

@start region id="ensure-project-context-directory"
Use `CONTEXT_DIR` for shared entries and `KNOWLEDGE_DIR` for agent entries. Create the destination directory if it does not exist.
@end region

@start region id="find-project-context-entry"
Use `context-index.md` in the selected directory to shortlist by name and description. Check the entry files as well if the index is missing or incomplete; exclude the index itself. Read each plausible file and keep its path for an update. For a new entry, use an unused filename; never overwrite a different entry with the same name.
@end region

@start region id="create-context-entry"
Read the [Project Context Template]([path-to-agent-memory-project]/templates/project-context-template.md).

Write the filled template block to a new `[theme].md` in the selected directory (`CONTEXT_DIR` for shared, `KNOWLEDGE_DIR` for agent). Do not include the template version line or overwrite an existing file.
@end region

@start region id="edit-context-entry"
Save the changes to the same file. Its modification time records the edit; do not maintain an `updated` frontmatter field. If an older entry has that field, remove it when editing the file.
@end region

@start region id="update-project-context"
### § list-context-entries

For a move, list the entry files in the relevant scope (exclude `context-index.md`). Check the target directory for a filename collision before copying.

### § move-context-entry

Copy the entry **verbatim** (same template) from the source scope to the target one. A **promote** goes agent → shared; a **demote** goes shared → agent:

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
- Agent: `rm [AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]/[theme].md`

### § check-entry-size

Count the lines in the written file.

- **Under 1000** → done.
- **Over 1000** → split: create one file per distinct sub-theme (each with its own frontmatter and tags), remove the original, then index every new file (**§ update-context-index**).

### § update-context-index

Edit the scope-aware `context-index.md`:

- Shared: `[AGENT-MEMORY-PATH]/shared-memory/[project-name]/context/context-index.md`
- Agent: `[AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]/context-index.md`

If it does not exist, create it with the header `# [project-name] Project Context`. Add or update the entry —

```
- [theme.md](theme.md) — description (tags: tag1, tag2, tag3)
```

— and for a move, delete the line from the agent index and add it to the shared index.

---
@end region

## load-project-context

@start region id="load-project-context"
### § list-context-entries

Read the shared index (`CONTEXT_DIR/context-index.md`) and scan the agent layer (`KNOWLEDGE_DIR` project subfolders, excluding `research/`) for its `context-index.md`. Parse each entry together with its scope marker (`[shared]` / `[agent]`). A missing or empty layer is skipped silently.

### § read-context-entry

Read the selected entry file(s) from their source-layer path:

- Shared: `[AGENT-MEMORY-PATH]/shared-memory/[project]/context/[theme].md`
- Agent: `[AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project]/[theme].md`

---
@end region

## map-orientation

@start region id="map-orientation"
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
@end region

## awaken-coder

@start region id="load-awakening"
Reuse the memory and episodic index that Munnin loaded. Read the coding reasoning file, the shared and agent project context indexes, the newest indexed episode for each project, and each available orientation map as directed below.
@end region

@start region id="load-coding-reasoning"
   Read `[AGENT-MEMORY-PATH]/shared-memory/coding-reasoning-memory.md` into your own context. If the file is missing, skip this step.
@end region

@start region id="load-context-indexes"
   Read the shared index (`CONTEXT_DIR/context-index.md`) and the agent index (`KNOWLEDGE_DIR/context-index.md`) at their resolved HOME paths. Skip missing indexes.
@end region

@start region id="load-maps"
   Read `MAP_PATH` for the home project and `[AGENT-MEMORY-PATH]/shared-memory/[project]/context/orientation-map.md` for each related project. Skip missing files.
@end region

@start region id="check-fleet-roster"
   Check whether `[AGENT-MEMORY-PATH]/shared-memory/[project]/fleet-agents.md` exists.
@end region

@start region id="load-task-workflow"
   Find `task-workflow` in `CONTEXT_DIR/context-index.md`. For a single match, read `CONTEXT_DIR/task-workflow.md`.
@end region

@start region id="select-project-episode"
     Use the episodic index Munnin loaded to select the newest entry for each project. Read each selected body from `[AGENT-MEMORY-PATH]/agent-[domain]/episodes/[filename]`.
@end region

## add-coding-reasoning

@start region id="add-coding-reasoning"
### § read-coding-lane

Read `[AGENT-MEMORY-PATH]/shared-memory/coding-reasoning-memory.md` into your own context (silently skip if missing).

### § template

The reasoning-pattern block format → read `[AGENT-MEMORY-PATH]/control-files/procedures/memory/resources/reasoning-pattern-template.md`.

### § generate-uuid

- **Windows**: `powershell -c "[guid]::NewGuid().ToString()"`
- **Linux/macOS**: `uuidgen` or `cat /proc/sys/kernel/random/uuid`

### § persist-coding-reasoning

Append the completed pattern as a level-3 (`###`) block to `[AGENT-MEMORY-PATH]/shared-memory/coding-reasoning-memory.md`, under an existing `## ` grouping. Transfer it with `copy-lines.sh` rather than retyping it, so the bytes arrive exactly.
@end region

## project-wrap-up

@start region id="project-wrap-up"
Run `/push-all <mode>` to capture files written after Step 1. Include the agent-memory repository in the push report and use the results from both pushes.
@end region
