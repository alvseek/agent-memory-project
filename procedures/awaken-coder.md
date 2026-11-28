+++
format_version = 2
id = "awaken-coder"
kind = "procedure"
title = "Awaken Coder — Coding-Agent Awakening Overlay"
description = "Orchestrating overlay for coding agents (working in a repo)."
argument_name = "domain"
argument_description = "the agent domain to awaken; asks if omitted"
+++
# Awaken Coder — Coding-Agent Awakening Overlay

Awaken the selected agent for work in this repository by loading its core memory together with the project context.

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

`$ARGUMENTS`

`[domain]` — the agent domain to awaken (e.g. `invintiry`, `aquazone`).

## Procedure

**Resolve the project first**: the repository this session is in, by the project identity rule, together with the related repositories that widen the recall. Then make **both awakening calls in one step**: the core's `/awaken-agent [domain]` and the store's `awaken_coder(domain, projects)` (**§ awaken-coder-payload**), which is the coding half of the same awakening. Neither needs the other's answer, so they go out together. First return both full tool responses for reading in that step, without selecting fields, summarizing, slicing, or preemptively redirecting them to files. Do not assume they will truncate before trying. For file-backed loads, likewise try one whole read per required source first.

@start component id="ref-1" ref="procedures/components/project-identity.md"
@end component

If the platform explicitly reports truncation or says the result was saved to a file, read the saved result to recover all omitted context before processing either payload or reporting completion. Try one whole read of that file first; only if that read also reports a limit, recover the missing content using a method that preserves it, including long lines. A preview, clipped JSON string, or summary is not a full load. If required context remains unavailable, name the source and failure and stop the work that depends on it. These recovery reads are only for observed output limits; a normal coding awakening still takes the two payload calls together. An episode's `next_cursor` is server-side pagination, not platform truncation: preserve the deliberate continuation rules below rather than automatically loading older sub-episodes.

1. **Run core awakening** — invoke the memory core `/awaken-agent [domain]` (Phase 1 identity + Phase 2 **central** memory + report). This loads identity, **universal** reasoning, emotional memory, shared and agent-owned knowledge indexes, and the **whole central episodic index**, every entry carrying its own `project`. On the store backend, shared knowledge is `shared.knowledge_index`: fetch only relevant bodies, never the whole directory. The file backend keeps its own loading contract. The core is **project-blind**; the coding half arrives in the other call, whose `episodes` carry one newest body per repository in the set (**§ select-project-episode**), and those are what the report carries forward. (This overlay owns coding-scoped reasoning and project-context loading, in steps 2-3.)

2. **Coding reasoning** — it arrived with the payload: read the lane from it (**§ load-coding-reasoning**); an empty lane is the silent skip. These are the reasoning patterns that only fire for a coding agent: they name repo artifacts, plan logs, foreign code, and fleet teammates, so the project-blind core does not carry them. Process them alongside the core reasoning patterns the core awakening already loaded — same lean shape, same weight.

3. **Project context** — it arrived with the payload too: the merged index for the whole set, both scopes included (**§ load-context-indexes**), so a related repository's index is in hand when the task moves into it. The HOME contract component still names the home that this session's own writes and its load-on-relevance reads use.

@start component id="ref-2" ref="procedures/components/home-contract.md"
@end component

   **Localized detection + handoff** — if `.agents/` exists at cwd, the project is localized and its home (episodic, knowledge, map) is owned by `agent-memory-local`: run **`/load-local-context`** to load it. That read supersedes the central load above. If `.agents/` is absent, the central load stands. For a project already known to be localized, skip the detection entirely by running `agent-memory-local`'s `/awaken-local`, which runs this procedure with that check replaced by the same call.

4. **Orientation map + fleet pointer** — the maps arrived with the payload: one per project in the set that has one, with its dates (**§ load-maps**) — never auto-create. (The bare `/map-orientation` load is for a project you are working in outside an awakening.) Then, when a roster appears in the payload's context index (**§ check-fleet-roster**), the overlay's whole fleet statement is one pointer: **this project has a fleet; fleet operation is available using `hermod-fleet`.** Resolve how to reach it from `[FLEET-ACCESS]` (see [Layer access](#layer-access)). The roster itself is loaded by the fleet repo's `/load-fleet`, not here.

5. **Task workflow** — load only the resolved current project's shared context entry named `task-workflow` (**§ load-task-workflow**), using the active home after any local-memory handoff. A related project's entry or an agent-private entry does not opt this project in. No entry → skip silently; never create one during awakening. Multiple matching entries → report the ambiguity and do not choose one.

   An **Awakening Hook** is the `Awakening Hook` section in that entry: project-owned, read-only instructions for checking assigned tasks and items waiting on a human. It declares the task system and required connection, the project/account scope, query filters (including what “me” means), the report format, and what to do when the connection is unavailable. Follow only this section during awakening; task creation, assignment, comments and status changes are not authorized by a hook. Report its results in the consolidated awakening report.

   If the hook declares `Readiness: Incomplete`, report its missing setup and skip task queries; do not repair or validate it during awakening. If the entry cannot be read, the section is missing, or its scope or query is unspecified, report the problem and skip the hook rather than guessing or reporting zero tasks. Other workflow sections are documentation, not awakening actions. To configure or change the entry explicitly, use `/set-project-task-workflow`.

6. **Report the coding awakening** — fold the coding results into the core report; do not produce a second report.
   - **Project**: name the current project. List related projects in one line if they widened recall.
   - **Carry-forward**: summarize open items from the **page** that arrived per repository, current project first. The episodic index and episode pages are scoped to the awakened agent: an empty result means **no episodes for this agent in this project set**, not that the repositories have no history or that nobody has worked on them. Keep that scope explicit when reporting an absence; do not automatically load other agents' episodes to fill it. A non-null `next_cursor` means the episode continues — say so and name that row's uuid and cursor rather than presenting the page as the whole record; a count below `blocks_total` with a null cursor is a complete final page. Include related-project items when they affect the current work. Present remembered status as the previous session's record, not newly verified state.
   - **Project context**: when available, say it will load on relevance. Show the full index only when asked.
   - **Attention needed**: report unresolved load problems, an absent coding-reasoning lane, and task counts or items from hooks that ran.
   - **Localization and fleet**: mention an active local-memory override or available fleet once, when present.

   Omit skipped checks, absent optional features, loaded-layer inventories and repeated setup suggestions. Do not prompt to create missing maps or context during awakening.

   Keep additions brief. If nothing needs attention, confirming the current project is enough.

*(Proactive project-context loading — standing behavior for the session: when the task shifts and the **project context** index has a relevant entry (`CONTEXT_DIR/context-index.md` shared · `KNOWLEDGE_DIR/context-index.md` agent), proactively load it — don't wait to be asked. Load silently, report briefly; never load everything. This is the coding half of Proactive Memory Loading; the general-knowledge + episodic half lives in the core knowledge foundation.)*

---

@start storage id="db-preamble" ref="procedures/memory/storage-backends/{backend}.md" target="all-procedures" applies_to="db"
@end storage
@start storage id="mechanics" ref="procedures/memory/storage-backends/{backend}.md" target="awaken-coder"
@end storage
