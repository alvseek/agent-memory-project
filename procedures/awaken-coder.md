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

5. **Task workflow.** Look for `task-workflow` in the home project’s shared context. If there’s no entry, skip silently. If more than one matches, report the ambiguity and skip.

@start storage id="load-task-workflow" ref="procedures/memory/storage-backends/{backend}.md" target="load-task-workflow"
@end storage

   Follow only the entry’s **Awakening Hook**. Use its connection, scope, and filters to check assigned tasks and items waiting on a human. Report the results as the hook specifies. This is read-only: don’t create or change tasks or the workflow.

   If `Readiness: Incomplete`, report the missing setup without querying tasks. If the entry can’t be read, the hook is missing, or its scope or query is unclear, report why the check was skipped. A skipped check is not a zero-task result.

6. **Report the coding awakening.** Add the following to Munnin’s report:
   - **Project:** Name the home project first. List related projects on one line if they widened recall.
   - **Carry-forward:** Summarize the previous session’s open items, home project first. Include related-project items only when they affect this work. If this agent has no episode for a project, say so; don’t substitute another project’s or agent’s episode.

@start storage id="select-project-episode" ref="procedures/memory/storage-backends/{backend}.md" target="select-project-episode"
@end storage

   - **Project context:** If available, say entries will load when relevant. Show the index only on request.
   - **Attention needed:** Report unresolved load problems, missing coding reasoning, and task-hook results. Include the fleet notice if applicable.

   Omit empty sections and setup suggestions.
