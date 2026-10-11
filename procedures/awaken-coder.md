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

**Resolve the project first.** The session's project, and the related projects that widen the recall, come from [the project identity rule]([path-to-agent-memory-project]/components/project-identity.md).

1. **Run core awakening** — invoke the memory core `/awaken-agent [domain]` (Phase 1 identity + Phase 2 **central** memory + report). This loads identity, **universal** reasoning, emotional, knowledge, and the **whole central episodic index**, every entry carrying its own `project`. The core is **project-blind**, so the project's newest episode is selected here: take the newest index entry whose `project` is in the project set (**§ select-project-episode**) and report it as the carry-forward. (This overlay owns coding-scoped reasoning and project-context loading, in steps 2-3.)

2. **Load coding reasoning** — load the coding-reasoning layer (**§ load-coding-reasoning**); silently skip if the store has none yet. These are the reasoning patterns that only fire for a coding agent: they name repo artifacts, plan logs, foreign code, and fleet teammates, so the project-blind core does not carry them. Process them alongside the core reasoning patterns the core awakening already loaded — same lean shape, same weight.

3. **Load project context** — apply the [HOME contract component]([path-to-agent-memory-project]/components/home-contract.md) with the resolved project as `[project]` to resolve the home, then load both context indexes (**§ load-context-indexes**), silently skipping whichever is missing. This is the central home by default.

   **Localized detection + handoff** — if `.agents/` exists at cwd, the project is localized and its home (episodic, knowledge, map) is owned by `agent-memory-local`: run **`/load-local-context`** to load it. That read supersedes the central load above. If `.agents/` is absent, the central load stands. For a project already known to be localized, skip the detection entirely by running `agent-memory-local`'s `/awaken-local`, which runs this procedure with that check replaced by the same call.

4. **Orientation map + fleet pointer** — Call `/map-orientation` (bare, load-only) to load the orientation map if it exists — never auto-create. Then, when the project has a fleet roster (**§ check-fleet-roster**), the overlay's whole fleet statement is one pointer: **this project has a fleet; fleet operation is available using `hermod-fleet`.** Resolve how to reach it from `[FLEET-ACCESS]` (see [Layer access](#layer-access)). The roster itself is loaded by the fleet repo's `/load-fleet`, not here.

5. **Task system check** — match the working directory to its task system and run that project's Awakening Hook: **Todoist** (`aquazone`, `invintiry`) → query `@agent-[my-domain]` + `@waiting-human`; **Jira/Linear** (`plko` / `ocx-platform`, `ocx-data`) → the Awakening Hook section in that project's context. Report counts. No matching project → skip silently.

6. **Augment the core report** — fold these additions into the core's report block:
   - **Current project + related projects + orientation map status**: name the resolved project, list any related projects that widened the recall, and if no map → *"No orientation map for [project] yet — use `/map-orientation create` to scan and create when ready."*
   - **Project context**: if either context-index was found, show a merged numbered list with `[shared]` / `[private]` prefixes; offer to load (auto-loads on relevance). If neither: *"No project context for [project] yet — use `/update-project-context` to capture some."*
   - **Task system**: report the queried counts.
   - **Coding reasoning**: if `coding-reasoning-memory.md` was missing, say so once — those patterns are simply absent this session, not silently substituted.
   - If localized: note that `agent-memory-local` superseded the central load.

*(Proactive project-context loading — standing behavior for the session: when the task shifts and the **project context** index has a relevant entry (`CONTEXT_DIR/context-index.md` shared · `KNOWLEDGE_DIR/context-index.md` private), proactively load it — don't wait to be asked. Load silently, report briefly; never load everything. This is the coding half of Proactive Memory Loading; the general-knowledge + episodic half lives in the core knowledge foundation.)*

---

## Storage Mechanics

The operations referenced above — **§ load-coding-reasoning**, **§ load-context-indexes**, **§ check-fleet-roster** — are defined by the **active storage backend**:

- **Markdown (native)** — follow `storage-backends/markdown.md` → its `awaken-coder` section.
- **DB (Hermod)** — the equivalents live in `storage-backends/db.md` → its `awaken-coder` section (not yet implemented).

See the seam contract at `storage-backends/README.md` for how this swap works.
