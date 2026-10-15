# Storage Backend — DB (Hermod)

Concrete storage mechanics for the **Hermod project store**, which holds project-keyed memory: context entries and the orientation map. Each `## [procedure]` section defines the `§ op`s that procedure references. See the [seam contract](README.md).

> **Ops here are tool calls, not shell commands.** A served client has no repository to write into, so every op below names a tool the agent calls. A context entry is addressed by its **`uuid`**, which the store assigns when it is created: the listings return it, and every op that acts on one entry takes it. `scope` is no longer an argument anywhere: the layer is in the tool's own name, where `shared` (every agent of the tenant) is the counterpart of `agent` (one agent's own). There is no `[AGENT-MEMORY-PATH]`, `CONTEXT_DIR` or `KNOWLEDGE_DIR` here: the store replaces them, and the project is a column.

> **The store is the memory database's records** ([ADR-027](../docs/adr/2026-10-13-hermod-store-is-valaskjalf-records.md)). A context entry is a `knowledge` record carrying a `project`: a row in `shared_record` for the `shared` layer and in `memory_record` for the `agent` one, where `agent_id` carries the owner. An entry's `title` is its theme and its `content_summary` the line a listing shows beside it; the orientation map is a `shared_record` row titled `orientation-map`. That `project` column is the boundary between the two corpora, and the memory layer's own browse excludes the rows that carry it, which is why a **listing is the only door to an entry's uuid**. **Hermod issues no DDL**: one owner holds both tables, so a missing table or column surfaces on the first call rather than being created here.

> **Discovery and creation are this store's; everything addressed by an existing uuid is the memory layer's.** Reading a body is `get(uuid)`, changing one is `edit` / `multi_edit` / `append` / `prepend`, changing its summary or tags is `edit_metadata`, and retiring it is `soft_delete`. Those ops already act on these rows, so nothing below reimplements one ([ADR-030](../docs/adr/2026-10-15-hermod-store-is-a-uuid-addressed-lens.md)).

> **Three ops resolve to no action**, and that is not an omission. The markdown backend needs a directory before it can write a file, an index file beside it, and a line count after a write; a store has none of the three, so `§ ensure-context-dir`, `§ update-context-index` and `§ check-entry-size` do nothing. This is the same resolution the memory core's db backend gives its own directory and derived-index steps.

---

## all-procedures

Every operation below is a **tool call**, reading and writing `shared_record` and `memory_record` through the tenant the verified token resolves to. No op names a path and no op takes a user id: whose rows are read and written is the token's, the project is the `project` argument, and the agent, on the ops that involve an agent-owned row, is the `agent` argument. Those ops require it rather than defaulting, because the token names the person and never the agent, so no owner can be derived from the call.

**Where a tool lives.** This store's own ops are named exactly as they are here. The memory layer's ops are tools on the other connected server, so `get`, `edit`, `edit_metadata` and `soft_delete` below resolve against that server's tool list.

---

## update-project-context

### § ensure-context-dir

No action. A store has no directories; the project, the layer and the owner are columns on the row.

### § list-context-entries

Call `list_shared_context(project)` and/or `list_agent_context(project, agent)`, one call per layer the step is about. Each row carries `uuid`, `scope`, `theme`, `content_summary` and `tags` — that list **is** the context index. A row whose `theme` matches is the entry the step means, and the `uuid` it carries is how every later call addresses it. The same call answers the move sub-flow's collision check. An agent-layer call requires its owner rather than defaulting, because those rows are owned.

### § read-context-entry

Call the memory layer's `get(uuid)` with the uuid a listing returned. It answers `None` for a row that is absent or tombstoned. Reading by theme is not a thing here: a theme is a name a listing shows, and two rows may carry one.

### § create-context-entry

Call `create_shared_context_entry(project, theme, content, template_version, content_summary, tags?)` or `create_agent_context_entry(project, agent, theme, content, template_version, content_summary, tags?)`, whichever layer the flow confirmed. `content` is the whole entry document built from [project-context-template.md]([path-to-agent-memory-project]/templates/project-context-template.md) — frontmatter included — and `template_version` the stamp that template carries below its title. `content_summary` is required: it is the line a listing shows beside the theme, taken from the document's frontmatter `description`, and `tags` comes from the same frontmatter. The row's `uuid` is assigned here and returned. **The stamp is declared, never stored**: it sits outside the template's fenced block, so the entry cannot carry it.

Refused when `template_version` is missing or does not match the served template, when `content` is over the 1000-line cap, when `content_summary` is blank, and when an agent-layer create names no `agent` or one this account has no row for. **No theme is checked**: two rows may carry one theme, so this op neither refuses a create over an existing theme nor revives a retired row. Deciding between creating and updating is the step's own comparison of themes against the listing.

### § update-context-entry

Two calls, in this order:

1. Change the body with the memory layer's `edit(uuid, old_string, new_string, replace_all?)`, or with `append` / `prepend` / `multi_edit` for the shapes those take. The body is edited surgically and never restated wholesale.
2. Change the line a listing shows with `edit_metadata(uuid, content_summary=..., tags=...)`, which is the only writer of those two fields. A field left out keeps its stored value, and `clearing` is the only route to empty.

**The two calls are not atomic**: a failure between them leaves the summary describing the old body, so a caller that needs both should do the body first and the summary after. The template stamp is not required here, because it gates creation, and a surgical edit's own precondition is a body the caller has already read.

### § move-context-entry

Call `promote_context_entry(uuid)` to move an entry into the shared layer, or `demote_context_entry(uuid, agent)` to move it into an agent's. The uuid is kept, so a handle held before the move still resolves after it. One call does both halves — the target row is written and the source row tombstoned — because the layer *is* which table the row lives in, which is why the sub-flow's next step has nothing left to do. Refused when no live entry holds the uuid, and when the entry already lives in the target layer. **It checks no theme**: two rows may carry one, so the sub-flow's own collision step is what decides whether a move should happen at all.

### § delete-context-entry

Call the memory layer's `soft_delete(uuid)`. The row is tombstoned rather than removed: gone from every read, and the same theme can be created again afterwards, which adds a new row rather than reviving the old one.

### § check-entry-size

No action. The cap is a **creation** gate: `§ create-context-entry` refuses a document over 1000 lines and names the count and the cap in its refusal, and a later body edit belongs to the memory layer, which knows no cap. The markdown backend splits an overgrown file into one file per sub-theme; a store row has no second file, so its remedy is the same one applied at creation: write one entry per sub-theme.

### § update-context-index

No action. The index is not a file here: `§ list-context-entries` renders it from the rows, so there is nothing to edit and nothing to keep in step.

---

## load-project-context

### § list-context-entries

Call `list_shared_context(project)` and `list_agent_context(project, agent)`, one per layer, and read each row's own `scope` to tell them apart. A layer is its own op now, so this step is two calls where it used to be one. `agent` is required, because those rows are owned. An empty result is the silent skip.

### § read-context-entry

Call the memory layer's `get(uuid)` for each selected entry and load its `full_content`.

---

## map-orientation

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

## awaken-coder

> **This whole section is one call.** `awaken_coder(domain, projects)` returns the coding half of an
> awakening in a single read-only payload, and every op below reads from it. It is issued **together
> with** the memory layer's `awaken(domain)`, in one step, because neither needs the other's answer
> and the two of them are the whole awakening ([ADR-029](../docs/adr/2026-10-14-hermod-reads-memory-rows-for-the-coding-awakening.md)).

### § awaken-coder-payload

Call `awaken_coder(domain, projects)`: `projects` is the resolved project **first**, then the related repositories that widen the recall. That first element is the session's home and never a filter: every key in the payload spans the whole set. One payload answers every op in this section — `coding_lane`, `episode_index`, `episodes`, `context_index`, `maps` — so nothing below costs a second call. It is read-only, and it takes no `scope` or `agent` beyond the domain: the token names the person and the domain names the agent whose episodes and agent-layer context these are. Refused when `projects` is empty, because a coding awakening without a repository has nothing to answer about. A client with no store attached reads its files instead — see `markdown.md`.

### § load-coding-reasoning

Read `coding_lane` from the payload; an empty lane is the silent skip, because a store that has not adopted the lane yet is a valid store. The lane is the memory layer's own record type, and the payload crosses that boundary once so no client has to.

### § load-context-indexes

Read `context_index` from the payload. Each row carries its own `scope`, which is what the `[shared]` / `[agent]` display reads, and its `uuid`, which is what every later read, edit or retirement of that entry is addressed by. The rows span the whole set, so a related repository's index is already in hand when the task moves into it.

### § check-fleet-roster

Look for a roster in the payload's `context_index`: a project whose index carries a `fleet-agents` entry has a fleet, and the pointer fires. Everything else skips silently. The roster's own **read** belongs to the fleet layer's `/load-fleet`, which already replaced the roster read that used to live here, so nothing is re-added.

### § select-project-episode

Take it from `episodes` in the payload: one newest body per project in the set, in the set's order, so the first is the session's own repository. Nothing to fetch and no `get` to make. A project in the set with no episode is simply absent from `episodes`, so its carry-forward is empty rather than the newest overall's, and a caller that wants a *different* episode of a project reads it from `episode_index` by `uuid`.

### § load-maps

Read `maps` from the payload: one entry per project in the set that has a map, each carrying `content` and its dates. A project absent from `maps` has none — never auto-create one here. The dates are what the bare `/map-orientation` load's mtime check reads.

---

## add-coding-reasoning

### § read-coding-lane

Call the memory layer's `coding_reasoning()` tool and load the patterns it returns. An empty list is the silent skip: a store that has not adopted the lane yet is a valid store.

### § template

Read the `reasoning-pattern-template` resource off the memory layer (`read_resource`), and note the `template_version` stamp it carries: the write in Step 4 must declare it.

### § generate-uuid

The pattern's cited UUID is content, so any 8-4-4-4-12 will do; the write also returns the record's own `uuid` if you prefer to cite that.

### § persist-coding-reasoning

Call the memory layer's `insert(scope="shared", record_type="coding_reasoning", title=..., content=..., template_version=<the template's stamp>)`. The record is fleet memory owned by nobody, and its `record_type` is the whole reason a chat agent's `awaken` never carries it.

## project-wrap-up

### § persist-store

Execute **`/push-project <mode>`** on the project repository. Every op above writes its row as it runs, on the memory database, so the store is durable the moment it is written and there is nothing left for a memory push to persist at wrap-up — that half of the op dissolves. The project push is the half that still has work: the commits Steps 2-3 produced. In the default `agent` mode it stages only this agent's own work; `all` pushes the full tree.
