# Awaken Coder — Coding-Agent Awakening Overlay

Orchestrating overlay for **coding agents** (working in a repo). It composes the memory-core awakening with repo/environment context: the core loads central memory; this overlay adds coding-scoped reasoning, localization, orientation map, fleet, and task-system.

**Delivery**: as a local skill/command (Claude Code CLI) or an MCP prompt (`agent-memory-project` server). Either way, the composition is agent-side — this overlay *invokes* the core; it never reaches into the core repo/server directly.

## Core access

Every handoff to the core in these instructions exists in two forms, and `[CORE-ACCESS]` fixes which one this machine uses:

- **`markdown`** — invoke the installed command, exactly as written.
- **`mcp`** — do not invoke the installed command. Fetch the procedure by name from the served core and follow what it returns, passing the argument the command would have taken (a domain, a mode). The installed commands are the file form, and they would write files where the store keeps records.

`[CORE-ACCESS]` decides even when the installed commands are also present, which under `mcp` they are.

Applies to every core procedure these instructions name: `awaken-agent`, `update-memory`, `wrap-up`, `push-memory`, `pull-memory`, `wait-options`.

## Layer access

A handoff to another layer resolves through that layer's **access declaration**, which the caller reads:

- `[CORE-ACCESS]` / `[CORE-MCP-URL]`: how the memory core (`munnin`) is reached.
- `[PROJECT-ACCESS]` / `[PROJECT-MCP-URL]`: how this coding overlay (`hermod-project`) is reached.
- `[FLEET-ACCESS]` / `[FLEET-MCP-URL]`: how the fleet (`hermod-fleet`) is reached.

Each value is `markdown` (the layer is installed as local commands/skills) or `mcp` (the layer is served as procedures over a connected server). An **absent** declaration means `markdown`. Name the target layer's capability, then resolve the invocation form from its declaration: invoke the installed command under `markdown`, or fetch the served procedure under `mcp`.

The `## Core access` rule above is this same rule applied to the core, kept separate because the core is the layer every handoff falls back to.

## Arguments

`[domain]` — the agent domain to awaken (e.g. `invintiry`, `aquazone`).

## Procedure

**Resolve the project first**: the repository this session is in, by [the project identity rule]([path-to-agent-memory-project]/components/project-identity.md), together with the related repositories that widen the recall. Then make **both awakening calls in one step**: the core's `/awaken-agent [domain]` and the store's `awaken_coder(domain, projects)` (**§ awaken-coder-payload**), which is the coding half of the same awakening. Neither needs the other's answer, so they go out together, and that one step is what keeps a coding awakening down to two calls.

1. **Run core awakening** — invoke the memory core `/awaken-agent [domain]` (Phase 1 identity + Phase 2 **central** memory + report). This loads identity, **universal** reasoning, emotional, knowledge, and the **whole central episodic index**, every entry carrying its own `project`. The core is **project-blind**; the coding half arrives in the other call, whose `episodes` carry one newest body per repository in the set (**§ select-project-episode**), and those are what the report carries forward. (This overlay owns coding-scoped reasoning and project-context loading, in steps 2-3.)

2. **Coding reasoning** — it arrived with the payload: read the lane from it (**§ load-coding-reasoning**); an empty lane is the silent skip. These are the reasoning patterns that only fire for a coding agent: they name repo artifacts, plan logs, foreign code, and fleet teammates, so the project-blind core does not carry them. Process them alongside the core reasoning patterns the core awakening already loaded — same lean shape, same weight.

3. **Project context** — it arrived with the payload too: the merged index for the whole set, both scopes included (**§ load-context-indexes**), so a related repository's index is in hand when the task moves into it. The [HOME contract component]([path-to-agent-memory-project]/components/home-contract.md) still names the home that this session's own writes and its load-on-relevance reads use.

   **Localized detection + handoff** — if `.agents/` exists at cwd, the project is localized and its home (episodic, knowledge, map) is owned by `agent-memory-local`: run **`/load-local-context`** to load it. That read supersedes the central load above. If `.agents/` is absent, the central load stands. For a project already known to be localized, skip the detection entirely by running `agent-memory-local`'s `/awaken-local`, which runs this procedure with that check replaced by the same call.

4. **Orientation map + fleet pointer** — the maps arrived with the payload: one per project in the set that has one, with its dates (**§ load-maps**) — never auto-create. (The bare `/map-orientation` load is for a project you are working in outside an awakening.) Then, when a roster appears in the payload's context index (**§ check-fleet-roster**), the overlay's whole fleet statement is one pointer: **this project has a fleet; fleet operation is available using `hermod-fleet`.** Resolve how to reach it from `[FLEET-ACCESS]` (see [Layer access](#layer-access)). The roster itself is loaded by the fleet repo's `/load-fleet`, not here.

5. **Task system check** — match the working directory to its task system and run that project's Awakening Hook: **Todoist** (`aquazone`, `invintiry`) → query `@agent-[my-domain]` + `@waiting-human`; **Jira/Linear** (`plko` / `ocx-platform`, `ocx-data`) → the Awakening Hook section in that project's context. Report counts. No matching project → skip silently.

6. **Augment the core report** — fold these additions into the core's report block:
   - **Carry-forward, one per repository**: the session's own repository first, then each related repository that has an episode, each with the open items its body carries. A repository with no episode is left out rather than filled with the newest overall's.
   - **Current project + related projects + orientation map status**: name the resolved project, list the related projects that widened the recall, and say which of them have a map — for one without it: *"No orientation map for [project] yet — use `/map-orientation create` to scan and create when ready."*
   - **Project context**: if the payload's context index has rows, show a merged numbered list with `[shared]` / `[agent]` prefixes, grouped by repository; offer to load (auto-loads on relevance). If it is empty: *"No project context for [project] yet — use `/update-project-context` to capture some."*
   - **Task system**: report the queried counts.
   - **Coding reasoning**: if the lane came back empty, say so once — those patterns are simply absent this session, not silently substituted.
   - If localized: note that `agent-memory-local` superseded the central load.

*(Proactive project-context loading — standing behavior for the session: when the task shifts and the **project context** index has a relevant entry (`CONTEXT_DIR/context-index.md` shared · `KNOWLEDGE_DIR/context-index.md` agent), proactively load it — don't wait to be asked. Load silently, report briefly; never load everything. This is the coding half of Proactive Memory Loading; the general-knowledge + episodic half lives in the core knowledge foundation.)*

---

## Storage Mechanics

The operations referenced above — **§ awaken-coder-payload**, **§ load-coding-reasoning**, **§ load-context-indexes**, **§ check-fleet-roster**, **§ select-project-episode**, **§ load-maps** — are defined by the **active storage backend**:

- **Markdown (native)** — follow `storage-backends/markdown.md` → its `awaken-coder` section.
- **DB (Hermod)** — `storage-backends/db.md` → its `awaken-coder` section, where every one of those ops reads from the single payload `awaken_coder(domain, projects)` returns.

See the seam contract at `storage-backends/README.md` for how this swap works.
