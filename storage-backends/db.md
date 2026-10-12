# Storage Backend — DB (Hermod)

Concrete storage mechanics for the **Hermod project store** — a small store Hermod serves over MCP, holding project-keyed memory: context entries and the orientation map. Each `## [procedure]` section defines the `§ op`s that procedure references. See the [seam contract](README.md).

> **Ops here are tool calls, not shell commands.** A served client has no repository to write into, so every op below names the tool the agent calls on the Hermod server. An entry is addressed by `(project, scope, theme)` with `scope` ∈ `shared` | `private`, and there is no `[AGENT-MEMORY-PATH]`, `CONTEXT_DIR` or `KNOWLEDGE_DIR` here: the store replaces them, and the project is a column.

> **Two ops resolve to no action**, and that is not an omission. The markdown backend needs a directory before it can write a file and an index file beside it; a store has neither, so `§ ensure-context-dir` and `§ update-context-index` do nothing. This is the same resolution the memory core's db backend gives its own directory and derived-index steps.

---

## all-procedures

Every operation below is a **tool call on this server**. The store is a local file, so nothing here needs a credential or reaches past the machine, and the project a row belongs to is the `project` argument — never a path.

---

## update-project-context

### § ensure-context-dir

No action. A store has no directories; the project and its scope are columns on the entry.

### § list-context-entries

Call `list_context_entries(project, scope?)`. Omit `scope` to list both layers. Each row carries `scope`, `theme`, `description` and `tags` — that list **is** the context index, so check the theme against it: a row whose `theme` matches is the entry to update, and no match means a new entry. The same call answers the move sub-flow's collision check.

### § read-context-entry

Call `read_context_entry(project, scope, theme)`. `found: false` means no live entry holds that identity.

### § create-context-entry

Call `create_context_entry(project, scope, theme, content, template_version, description?, tags?)`, with `content` the whole entry document built from [project-context-template.md]([path-to-agent-memory-project]/templates/project-context-template.md) — frontmatter included — and `template_version` the stamp that template carries below its title. Pass `description` and `tags` from that frontmatter so the listing can show them. **The stamp is declared, never stored**: it is a gate token, and the entry itself never carries the line. Refused when a live entry already holds the identity, and when `template_version` is missing or does not match the served template.

### § update-context-entry

Call `update_context_entry(project, scope, theme, content, template_version, description?, tags?)` with the entry's full new content and the template's current stamp. An update restates the whole document, so it carries the same gate the create does. Refused when no live entry holds the identity, so an update can never become a create, and when `template_version` is missing or stale.

### § move-context-entry

Call `move_context_entry(project, theme, from_scope, to_scope)`. One call where the markdown backend copies then deletes: the scope changes and the body is untouched, so there is no partial state and nothing to clean up (the markdown backend's partial-failure note does not apply here). **The direction is a choice, not a built-in**: a *promote* is `from_scope="private", to_scope="shared"` and a *demote* is the reverse, both one call. Refused when the source holds no live entry of that theme, and when the target scope already holds one — the collision M.2 stops on.

### § delete-context-entry

Call `delete_context_entry(project, scope, theme)`. The entry becomes a tombstone: gone from every read, and the same theme can be created again afterwards.

### § check-entry-size

Call `check_entry_size(content)` for the measurement. `create` and `update` enforce it: an entry over **1000 lines** is refused. The markdown backend splits an overgrown file into one file per sub-theme; a store row has no second file to split into, so the store refuses instead — same threshold, different remedy, and the fix is the same either way: write one entry per sub-theme.

### § update-context-index

No action. The index is not a file here: `§ list-context-entries` renders it from the rows, so there is nothing to edit and nothing to keep in step.

---

## load-project-context

### § list-context-entries

Call `list_context_entries(project)` — both scopes in one call, each row carrying its own `scope`, which is what the `[shared]` / `[private]` display reads. An empty result is the silent skip.

### § read-context-entry

Call `read_context_entry(project, scope, theme)` for each selected entry and load `content`.

---

## map-orientation

### § map-exists

Call `map_exists(project)` and read `exists`.

### § ensure-context-dir

No action. A store has no directories.

### § read-map

Call `read_map(project)`; `found: false` means the project has no map. `content` is the whole map, frontmatter included.

### § write-map

Call `write_map(project, content, template_version, description?)` with the full map text and the template's current stamp. Refused when the project has no map — writing never creates one — and when `template_version` is missing or stale.

### § create-map

Call `create_map(project, content, template_version, description?)` with the map built from [orientation-map-template.md]([path-to-agent-memory-project]/templates/orientation-map-template.md) and the stamp that template carries below its title. Declared, never stored: the map itself never carries the line. Refused when the project already has a map, and when `template_version` is missing or stale.

---

## awaken-coder

### § load-coding-reasoning

The coding-reasoning layer is memory, not project context, so the project store does not hold it: read it from the memory layer, the same way the core's shared content is read. This is a visible cost of the no-join decision (the store carries no episodes and no fleet memory). A client with no memory layer attached skips the layer, exactly as the markdown backend does when the file is missing.

### § load-context-indexes

Call `list_context_entries(project)` — the rows are the index projection for the resolved project, and they span both scopes, so this is both indexes in one call.

### § check-fleet-roster

The roster is store memory rather than project context, so the project store does not hold it: ask the memory layer whether the project has a roster, and skip the fleet pointer when there is none.

### § select-project-episode

**Delegated to the memory layer.** Episodes are Munnin's records and the project store holds none, so the two-part step resolves there: ask the memory layer for the newest episode whose `project` is in the resolved project set, and read its body there. This is the second and sharper cost of the no-join decision, and the strongest single argument for revisiting it.

---

## project-wrap-up

### § persist-store

Execute **`/push-project <mode>`** on the project repository. This store is the server's own file, written by every op above as it runs, so there is nothing left for a memory push to persist at wrap-up and that half of the op dissolves. The project push is the half that still has work — the commits Steps 2-3 produced. In the default `agent` mode it stages only this agent's own work; `all` pushes the full tree.
