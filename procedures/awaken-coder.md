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

If `.agents/` exists in the current working directory, suggest `/awaken-coder-local` instead.

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

1. **Coding reasoning** — apply the coding reasoning patterns alongside the core reasoning patterns.
@start storage id="load-coding-reasoning" ref="procedures/memory/storage-backends/{backend}.md" target="load-coding-reasoning"
@end storage

2. **Project context** — load the shared and agent context indexes. When the task changes, read any entry relevant to the new work without waiting to be asked. Don’t load every entry.
@start component id="ref-2" ref="procedures/components/home-contract.md" applies_to="markdown"
@end component
@start storage id="load-context-indexes" ref="procedures/memory/storage-backends/{backend}.md" target="load-context-indexes"
@end storage

3. **Orientation maps.** Load the existing map for each project in the set. Skip missing maps; don’t create them during awakening.
@start storage id="load-maps" ref="procedures/memory/storage-backends/{backend}.md" target="load-maps"
@end storage

4. **Fleet.** If a project has a `fleet-agents` roster, name that project in the report and mention `/load-fleet`. Don’t load the roster during awakening.
@start storage id="check-fleet-roster" ref="procedures/memory/storage-backends/{backend}.md" target="check-fleet-roster"
@end storage

5. **Task workflow** — load only the resolved current project's shared context entry named `task-workflow`. A related project's entry or an agent-private entry does not opt this project in. No entry → skip silently; never create one during awakening. Multiple matching entries → report the ambiguity and do not choose one.

@start storage id="load-task-workflow" ref="procedures/memory/storage-backends/{backend}.md" target="load-task-workflow"
@end storage

   An **Awakening Hook** is the `Awakening Hook` section in that entry: project-owned, read-only instructions for checking assigned tasks and items waiting on a human. It declares the task system and required connection, the project/account scope, query filters (including what “me” means), the report format, and what to do when the connection is unavailable. Follow only this section during awakening; task creation, assignment, comments and status changes are not authorized by a hook. Report its results in the consolidated awakening report.

   If the hook declares `Readiness: Incomplete`, report its missing setup and skip task queries; do not repair or validate it during awakening. If the entry cannot be read, the section is missing, or its scope or query is unspecified, report the problem and skip the hook rather than guessing or reporting zero tasks. Other workflow sections are documentation, not awakening actions. To configure or change the entry explicitly, use `/set-project-task-workflow`.

6. **Report the coding awakening** — fold the coding results into the core report; do not produce a second report.
   - **Project**: name the current project. List related projects in one line if they widened recall.
   - **Carry-forward**: summarize open items from the newest episode available for each project, home project first. If a project has no episode for this agent, say so; do not substitute another project's episode. An empty set of results means **no episodes for this agent in this project set**; do not automatically load other agents' episodes. Include related-project items when they affect the current work. Present remembered status as the previous session's record, not newly verified state.

@start storage id="select-project-episode" ref="procedures/memory/storage-backends/{backend}.md" target="select-project-episode"
@end storage

   - **Project context**: when available, say it will load on relevance. Show the full index only when asked.
   - **Attention needed**: report unresolved load problems, an absent coding-reasoning lane, and task counts or items from hooks that ran.

   Omit skipped checks, absent optional features, loaded-layer inventories and repeated setup suggestions. Do not prompt to create missing maps or context during awakening.

   Keep additions brief. If nothing needs attention, confirming the current project is enough.
