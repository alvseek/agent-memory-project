# Storage Backend — DB (Hermod)

Concrete storage mechanics for the **Hermod project store**, which holds project-keyed memory: context entries and the orientation map. Each `## [procedure]` section defines the `§ op`s that procedure references. See the [seam contract](README.md).

> **Ops here are tool calls, not shell commands.** A served client has no repository to write into, so every op below names a tool the agent calls. A context entry is addressed by its **`uuid`**, which the store assigns when it is created: the listings return it, and every op that acts on one entry takes it. `scope` is no longer an argument anywhere: the layer is in the tool's own name, where `shared` (every agent of the tenant) is the counterpart of `agent` (one agent's own). There is no `[AGENT-MEMORY-PATH]`, `CONTEXT_DIR` or `KNOWLEDGE_DIR` here: the store replaces them, and the project is a column.

> **The store is the memory database's records** ([ADR-027](../../../docs/adr/2026-10-13-hermod-store-is-valaskjalf-records.md)). A context entry is a `knowledge` record carrying a `project`: a row in `shared_record` for the `shared` layer and in `memory_record` for the `agent` one, where `agent_id` carries the owner. An entry's `title` is its theme and its `content_summary` the line a listing shows beside it; the orientation map is a `shared_record` row titled `orientation-map`. That `project` column is the boundary between the two corpora, and the memory layer's own browse excludes the rows that carry it, which is why a **listing is the only door to an entry's uuid**. **Hermod issues no DDL**: one owner holds both tables, so a missing table or column surfaces on the first call rather than being created here.

> **Discovery and creation are this store's; everything addressed by an existing uuid is the memory layer's.** Reading a body is `get_memory(uuid)`, changing one is `edit_memory_body` / `multi_edit_memory_body` / `append_memory_body` / `prepend_memory_body`, changing its summary or tags is `edit_memory_metadata`, and retiring it is `soft_delete_memory`. Those ops already act on these rows, so nothing below reimplements one ([ADR-030](../../../docs/adr/2026-10-15-hermod-store-is-a-uuid-addressed-lens.md)).

> DB context entries need no directory, separate index file, or post-write line count. The size limit applies when creating a record.

---

## all-procedures

@start region id="all-procedures" ending="none"
Every operation below is a **tool call**, reading and writing `shared_record` and `memory_record` through the tenant the verified token resolves to. No op names a path and no op takes a user id: whose rows are read and written is the token's, the project is the `project` argument, and the agent, on the ops that involve an agent-owned row, is the `agent` argument. Those ops require it rather than defaulting, because the token names the person and never the agent, so no owner can be derived from the call.

**Where a tool lives.** This store's own ops are named exactly as they are here. The memory layer's ops are tools on the other connected server, so `get_memory`, `edit_memory_body`, `edit_memory_metadata` and `soft_delete_memory` below resolve against that server's tool list.

---


@end region

## update-project-context

@start region id="find-project-context-entry"
Use `list_shared_context(project)` for shared entries or `list_agent_context(project, agent)` for this agent’s entries. Shortlist by `theme` and `content_summary`, then read candidate bodies with Munnin’s `get_memory(uuid)`. Keep the selected UUID for the update; a theme is not a unique address.
@end region

@start region id="create-context-entry"
Read the template with Hermod’s `read_resource("project-context-template")`.

Before creating a record, check the length of the filled entry body. Up to 1,000 lines is valid. If it is longer, split it by topic first and create a separate entry within the limit for each topic.

Call `create_shared_context_entry(project, theme, content, template_version, content_summary, tags?)` for shared scope or `create_agent_context_entry(project, agent, theme, content, template_version, content_summary, tags?)` for agent scope. Pass only the body as `content`. Supply the description as `content_summary`, the tags as `tags`, and the template stamp as `template_version`. Valaskjalf timestamps the record and returns its UUID.
@end region

@start region id="edit-context-entry"
Keep the UUID. Read Munnin’s `get_memory(uuid, include_edit_context=true)`. For body changes, edit only the affected text with `edit_memory_body`, `append_memory_body`, `prepend_memory_body`, or `multi_edit_memory_body`.

For a description or tag change alone, call only `edit_memory_metadata`. The record fields are authoritative even if an older body contains YAML. If both body and metadata changed, save the body first and use the returned revision for the metadata write. Use the tenant and revision guards, reread on conflict, and report a partial write if the second operation fails. Valaskjalf maintains `modified_date`.
@end region

@start region id="update-project-context"
### § list-context-entries

For a move, list the relevant scope with `list_shared_context(project)` or `list_agent_context(project, agent)`. Check the target for a theme collision and identify the source by UUID.

### § move-context-entry

Call `promote_context_entry(uuid)` to move an entry into the shared layer, or `demote_context_entry(uuid, agent)` to move it into an agent's. The uuid is kept, so a handle held before the move still resolves after it. One call does both halves — the target row is written and the source row tombstoned — because the layer *is* which table the row lives in, which is why the sub-flow's next step has nothing left to do. Refused when no live entry holds the uuid, and when the entry already lives in the target layer. **It checks no theme**: two rows may carry one, so the sub-flow's own collision step is what decides whether a move should happen at all.

**A theme cannot be renamed in place here.** Giving an entry a different theme means creating it under the new one and retiring the old row with `soft_delete_memory`, because the theme is what `title` holds.

### § delete-context-entry

Call the memory layer's `soft_delete_memory(uuid)`. The row is tombstoned rather than removed: gone from every read, and the same theme can be created again afterwards, which adds a new row rather than reviving the old one.

**Inside the move sub-flow this op has nothing to do**, because `§ move-context-entry` already tombstoned the source. The uuid now names the row that moved, so calling it there would retire the entry the caller just moved, which is why the sub-flow's step is "ensure the source is gone" rather than "call delete".

---
@end region

## load-project-context

@start region id="load-project-context"
### § list-context-entries

Call `list_shared_context(project)` and `list_agent_context(project, agent)`, one per layer, and read each row's own `scope` to tell them apart. A layer is its own op now, so this step is two calls where it used to be one. `agent` is required, because those rows are owned. An empty result is the silent skip.

### § read-context-entry

Call the memory layer's `get_memory(uuid)` for each selected entry and load its `full_content`.

---
@end region

## map-orientation

@start region id="map-orientation"
### § map-exists

No action. `§ read-map` answers the existence question: a project with no map comes back as `found: false`, so nothing checks for one first.

### § ensure-context-dir

No action. A store has no directories.

### § read-map

Call `read_map(project)`; `found: false` means the project has no map. `content` is the whole map, frontmatter included.

### § create-map

Call `create_map(project, content, template_version, content_summary?)` with the map built from [orientation-map-template.md]([path-to-agent-memory-project]/templates/orientation-map-template.md) and the stamp that template carries below its title. Declared, never stored: the stamp sits outside the template's fenced block, so the map cannot carry it. The row's `uuid` is assigned here, and its identity for this flow is the project plus the reserved title, so a second create is refused: a project has one map, and it is updated thereafter.

### § write-map

Call `update_map(project, content, template_version, content_summary?)` with the full map text and the template's current stamp. It rewrites that one row and touches no other. Refused when the project has no map, so writing never creates one, and when `template_version` is missing or stale.

---
@end region

## awaken-coder

@start region id="load-awakening"
Call `awaken_coder(domain, projects)` in the same step as Munnin’s memory load, without waiting for its result. If Munnin uses MCP, the two calls are `awaken(domain)` and `awaken_coder(domain, projects)`. Pass the home project first, followed by its related projects. The read-only response covers the whole set.
@end region

@start region id="load-coding-reasoning"
   Read `coding_lane` from the awakening response. If it is empty, skip this step.
@end region

@start region id="load-context-indexes"
   Read `context_index` for the whole project set. Each entry carries its project, scope (shared or agent), and the UUID to use for later reads.
@end region

@start region id="load-maps"
   Read `maps` from the awakening response. Each entry contains the whole map and its dates. A project without an entry has no map.
@end region

@start region id="check-fleet-roster"
   Look for a `fleet-agents` entry in the project context index.
@end region

@start region id="load-task-workflow"
   Select rows from `context_index` whose `project` is `projects[0]`, `scope` is `shared`, and `theme` is exactly `task-workflow`. For a single match, call Munnin’s `get_memory(uuid)` with the row’s UUID and read its `content`.
@end region

@start region id="select-project-episode"
     ### § select-project-episode

     Use the pages already in `episodes`, one per project that has an episode. Each page contains up to three timestamp groups. If `next_cursor` is non-null, report the row's UUID and cursor so the reader knows the episode continues. A null cursor marks the final page even if `blocks_returned` is less than `blocks_total`.

     Only if older entries are needed, call the memory layer's `get_memory(uuid, cursor=…)` with that row's values. To read a different episode, use its UUID from `episode_index`. Index entries and search snippets are not episode bodies.
@end region

## add-coding-reasoning

@start region id="add-coding-reasoning"
### § read-coding-lane

Call the memory layer's `coding_reasoning()` tool and load the patterns it returns. An empty list is the silent skip: a store that has not adopted the lane yet is a valid store.

### § template

Read the `reasoning-pattern-template` resource off the memory layer (`read_resource`), and note the `template_version` stamp it carries: the write in Step 4 must declare it.

### § generate-uuid

The pattern's cited UUID is content, so any 8-4-4-4-12 will do; the write also returns the record's own `uuid` if you prefer to cite that.

### § persist-coding-reasoning

Call the memory layer's `insert_memory(scope="shared", record_type="coding_reasoning", title=..., content=..., template_version=<the template's stamp>)`. The record is fleet memory owned by nobody, and its `record_type` is the whole reason a chat agent's `awaken` never carries it.
@end region

## project-wrap-up

@start region id="project-wrap-up"
Steps 2–3 write directly to the database. Check their write results and use the project push result from Step 1. No second push or agent-memory Git report is needed.
@end region
