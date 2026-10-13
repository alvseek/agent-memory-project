# Storage Backend — DB (Hermod)

Concrete storage mechanics for the **Hermod project store**, which holds project-keyed memory: context entries and the orientation map. Each `## [procedure]` section defines the `§ op`s that procedure references. See the [seam contract](README.md).

> **Ops here are tool calls, not shell commands.** A served client has no repository to write into, so every op below names the tool the agent calls on the Hermod server. An entry is addressed by `(project, scope, theme)` with `scope` ∈ `shared` | `private`, and there is no `[AGENT-MEMORY-PATH]`, `CONTEXT_DIR` or `KNOWLEDGE_DIR` here: the store replaces them, and the project is a column.

> **The store is the memory database's records** ([ADR-027](../docs/adr/2026-10-13-hermod-store-is-valaskjalf-records.md)). A context entry is a `knowledge` record carrying a `project`: a row in `shared_record` for the `shared` scope and in `memory_record` for the `private` one, where `agent_id` carries the owner the markdown path kept in a folder name. An entry's `title` is its theme and its `content_summary` the description the index shows; the orientation map is a `shared_record` row titled `orientation-map`. That `project` column is also the whole boundary between the two corpora — a `knowledge` row without one is the memory store's own general knowledge, and its reads exclude the ones that have it, so a project entry is never served as general knowledge. **Hermod issues no DDL**: one owner holds both tables, so a missing table or column surfaces on the first call rather than being created here, and Hermod has no schema of its own to migrate.

> **Two ops resolve to no action**, and that is not an omission. The markdown backend needs a directory before it can write a file and an index file beside it; a store has neither, so `§ ensure-context-dir` and `§ update-context-index` do nothing. This is the same resolution the memory core's db backend gives its own directory and derived-index steps.

---

## all-procedures

Every operation below is a **tool call on this server**, reading and writing `shared_record` and `memory_record` through the tenant the verified token resolves to. No op names a path and no op takes a user id: whose rows are read and written is the token's, the project is the `project` argument, and the agent, on the ops that involve a private row, is the `agent` argument. Those ops require it rather than defaulting, because the token names the person and never the agent, so no owner can be derived from the call.

---

## update-project-context

### § ensure-context-dir

No action. A store has no directories; the project, the scope and the owner are columns on the row.

### § list-context-entries

Call `list_context_entries(project, scope?, agent?)`. Omit `scope` to list both layers, and then pass `agent`, because the private rows are owned. Each row carries `scope`, `theme`, `description` and `tags` — that list **is** the context index, so check the theme against it: a row whose `theme` matches is the entry to update, and no match means a new entry. The same call answers the move sub-flow's collision check.

### § read-context-entry

Call `read_context_entry(project, scope, theme, agent?)`, naming `agent` for a private entry. `found: false` means no live entry holds that identity.

### § create-context-entry

Call `create_context_entry(project, scope, theme, content, template_version, description?, tags?, agent?)`, with `content` the whole entry document built from [project-context-template.md]([path-to-agent-memory-project]/templates/project-context-template.md) — frontmatter included — and `template_version` the stamp that template carries below its title. Pass `description` and `tags` from that frontmatter: they land in the row's `content_summary` and `tags`, which is what the listing reads. **The stamp is declared, never stored**: it sits outside the template's fenced block, so the entry cannot carry it. The row's identity is derived from `user_id | project | scope | agent | theme`, so the same theme under two agents is two entries rather than one. Refused when a live entry already holds the identity, when `template_version` is missing or does not match the served template, and when a private create names no `agent`.

### § update-context-entry

Call `update_context_entry(project, scope, theme, content, template_version, description?, tags?, agent?)` with the entry's full new content and the template's current stamp. It replaces the row's `full_content`, `content_summary` and `tags` wholesale, so a caller that passes only `content` clears the other two. An update restates the whole document, so it carries the same gate the create does. Refused when no live entry holds the identity, so an update can never become a create, and when `template_version` is missing or stale.

### § move-context-entry

Call `move_context_entry(project, theme, from_scope, to_scope, agent?)`, naming `agent` for whichever side is private. **The direction is a choice, not a built-in**: a *promote* is `from_scope="private", to_scope="shared"` and a *demote* is the reverse. One call, two row operations — the scope *is* which table the row lives in, so the target table gains the row and the source's is tombstoned, the same copy-then-delete shape the markdown backend has and the same exposure if it fails between the two. The body is untouched. Refused when the source holds no live entry of that theme, when the target scope already holds one (the collision the move sub-flow stops on), and when a private side names no `agent`.

### § delete-context-entry

Call `delete_context_entry(project, scope, theme, agent?)`. The row is tombstoned rather than removed: gone from every read, and the same theme can be created again afterwards — over the same identity, which revives that row instead of adding a second one.

### § check-entry-size

Call `check_entry_size(content)` for the measurement. `create` and `update` enforce it: an entry over **1000 lines** is refused. The markdown backend splits an overgrown file into one file per sub-theme; a store row has no second file to split into, so the store refuses instead — same threshold, different remedy, and the fix is the same either way: write one entry per sub-theme.

### § update-context-index

No action. The index is not a file here: `§ list-context-entries` renders it from the rows, so there is nothing to edit and nothing to keep in step.

---

## load-project-context

### § list-context-entries

Call `list_context_entries(project, agent)` — both scopes in one call, each row carrying its own `scope`, which is what the `[shared]` / `[private]` display reads. `agent` is required, because the private rows are owned. An empty result is the silent skip.

### § read-context-entry

Call `read_context_entry(project, scope, theme, agent?)` for each selected entry, naming `agent` for a private one, and load `content`.

---

## map-orientation

### § map-exists

Call `map_exists(project)` and read `exists`: whether `shared_record` already holds this project's row titled `orientation-map`.

### § ensure-context-dir

No action. A store has no directories.

### § read-map

Call `read_map(project)`; `found: false` means the project has no map. `content` is the whole map, frontmatter included.

### § write-map

Call `write_map(project, content, template_version, description?)` with the full map text and the template's current stamp. It rewrites that one row and touches no other. Refused when the project has no map — writing never creates one — and when `template_version` is missing or stale.

### § create-map

Call `create_map(project, content, template_version, description?)` with the map built from [orientation-map-template.md]([path-to-agent-memory-project]/templates/orientation-map-template.md) and the stamp that template carries below its title. Declared, never stored: the stamp sits outside the template's fenced block, so the map cannot carry it. The row's identity is derived from the project and the title, so a second create collides rather than adding a map. Refused when the project already has a map, and when `template_version` is missing or stale.

---

## awaken-coder

### § load-coding-reasoning

Call the memory layer's `coding_reasoning()` tool and load the patterns it returns. The lane is memory, not project context, so this store does not hold it: it is delegated to the memory layer, the same way the core's shared content is read. This is a visible cost of the no-join decision (the store carries no episodes and no fleet memory). A client with no memory layer attached skips the layer, exactly as the markdown backend does when the file is missing.

### § load-context-indexes

Call `list_context_entries(project, agent)` — the rows are the index projection for the resolved project, and they span both scopes, so this is both indexes in one call. `agent` is required here for the same reason it is in `update-project-context`.

### § check-fleet-roster

The roster is store memory rather than project context, so the project store does not hold it: ask the memory layer whether the project has a roster, and skip the fleet pointer when there is none.

### § select-project-episode

From the index the core returned, take the newest entry whose `project` is in the resolved set, then load that episode's body from the memory layer with `get(uuid)` when it is not the payload's `latest_episode`. `awaken` is project-blind, so its `latest_episode` is the newest overall and the index carries `project` on every entry. No entry in the set → the project has none yet: keep the payload's `latest_episode`, say it is not project-specific, and skip open items. Episodes remain Munnin's records, so a body beyond the default costs one memory-layer read.

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
