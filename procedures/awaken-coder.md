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

## Access

When a step calls another procedure, use the access setting for the layer that owns it: `[CORE-ACCESS]` for Munnin, `[PROJECT-ACCESS]` for Hermod, or `[FLEET-ACCESS]` for the fleet.

- **`markdown`** (or no setting): run the installed command with the specified arguments.
- **`mcp`**: fetch the named procedure from that layer’s configured server and follow its instructions, passing the same arguments. Use the server even if the command is also installed.

## Arguments

`$ARGUMENTS`

`domain` — the agent domain to awaken (for example, `software-architect`). If omitted, ask which domain to awaken.

## Procedure

### Identify the project set

Start in the current working directory. Identify the home project first, then the related projects whose memory should be loaded.

@start component id="ref-1" ref="procedures/components/project-identity.md"
@end component

Put the home project first. Outside Git, it is the only project. Otherwise, add related projects once each to widen recall; the home project is still where this session’s memory is filed.

Traverse submodules recursively. From each repository root, match Git’s recorded submodule paths (`git ls-files --stage`, mode `160000`) to their paths and URLs in `.gitmodules`. Resolve each path relative to that root, skip vendored or read-only submodules, and use the repository name from each included URL. If a child is not checked out, its recorded commit can supply its Git tree and `.gitmodules` without initialization.

Before using the set, verify that every included repository was checked for nested submodules. If a recorded submodule has no mapping, or a child cannot be inspected, name the path and report that discovery is incomplete. A repository with no recorded submodules needs no `.gitmodules` file.

### Load the awakening data

Run Munnin’s `awaken-agent` procedure for the selected domain, using Munnin’s access setting. Load Hermod’s coding context for the project set as described below.

@start storage id="load-awakening" ref="procedures/memory/storage-backends/{backend}.md" target="load-awakening"
@end storage

Read each tool response in full in the step that requests it. Do not select fields, summarize, slice, or redirect the response to a file in advance. For a required file, start with one whole read.

If the platform reports truncation or saves a result to a file, read the saved result in full before using the awakening data. If that read is also clipped, recover all missing content, including long lines. If required context remains unavailable, name the source and failure and stop the work that depends on it. An episode’s `next_cursor` is pagination, not truncation; follow the episode instructions before requesting older entries.

1. **Use the core awakening** — Munnin loads identity, **universal** reasoning, emotional memory, shared and agent-owned knowledge indexes, and the **whole central episodic index**, every entry carrying its own `project`. On the store backend, shared knowledge is `shared.knowledge_index`: fetch only relevant bodies, never the whole directory. The file backend keeps its own loading contract. The core is **project-blind**; for carry-forward, use the newest episode selected for each repository (**§ select-project-episode**).

2. **Coding reasoning** — it arrived with the payload: read the lane from it (**§ load-coding-reasoning**); an empty lane is the silent skip. These are the reasoning patterns that only fire for a coding agent: they name repo artifacts, plan logs, foreign code, and fleet teammates, so the project-blind core does not carry them. Process them alongside the core reasoning patterns the core awakening already loaded — same lean shape, same weight.

3. **Project context** — it arrived with the payload too: the merged index for the whole set, both scopes included (**§ load-context-indexes**), so a related repository's index is in hand when the task moves into it. The HOME contract component still names the home that this session's own writes and its load-on-relevance reads use.

@start component id="ref-2" ref="procedures/components/home-contract.md"
@end component

   **Localized detection + handoff** — if `.agents/` exists at cwd, the project is localized and its home (episodic, knowledge, map) is owned by `agent-memory-local`: run **`/load-local-context`** to load it. That read supersedes the central load above. If `.agents/` is absent, the central load stands. For a project already known to be localized, skip the detection entirely by running `agent-memory-local`'s `/awaken-local`, which runs this procedure with that check replaced by the same call.

4. **Orientation map + fleet pointer** — the maps arrived with the payload: one per project in the set that has one, with its dates (**§ load-maps**) — never auto-create. (The bare `/map-orientation` load is for a project you are working in outside an awakening.) Then, when a roster appears in the payload's context index (**§ check-fleet-roster**), the overlay's whole fleet statement is one pointer: **this project has a fleet; fleet operation is available using `hermod-fleet`.** Resolve how to reach it from `[FLEET-ACCESS]` (see [Access](#access)). The roster itself is loaded by the fleet repo's `/load-fleet`, not here.

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
