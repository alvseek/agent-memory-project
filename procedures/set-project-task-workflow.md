+++
format_version = 2
id = "set-project-task-workflow"
kind = "procedure"
title = "Set Project Task Workflow"
description = "Configure the current project's task tracker and read-only Awakening Hook in its shared task-workflow context entry."
argument_name = "argument"
argument_description = "Input text in the format described by this procedure's Arguments section"
+++
# Set Project Task Workflow

Configure the current project's task tracker and read-only Awakening Hook in its shared `task-workflow` context entry. Inspect existing setup, ask only for missing details, and confirm the proposed changes before saving. This procedure configures instructions; it does not create a tracker integration or change tasks.

## Arguments

`$ARGUMENTS`

- `/set-project-task-workflow [details]` → Create or update this project's workflow using the supplied details.
- `/set-project-task-workflow` → Inspect existing configuration, then ask what needs setting up or changing.

Details are free text, not a required vendor-specific syntax. Tracker names are inputs, never a hardcoded project-to-vendor mapping.

## Procedure

### 1. Resolve the project and active home

Resolve the current repository using the project identity rule. Only the current project is a write target; related repositories do not inherit its tracker configuration. If the user names a different project, clarify the target before proceeding rather than writing under the current repository's identity.

@start component id="ref-1" ref="procedures/components/project-identity.md"
@end component

Use the active HOME contract. Preserve an existing local-memory override. If `.agents/` exists and local context has not been loaded, run `/load-local-context` before reading or writing project context; its active shared home supersedes central context. Do not create local memory or fall back to a central entry when local context is unavailable.

@start component id="ref-2" ref="procedures/components/home-contract.md"
@end component

The target is fixed: **shared scope**, theme **`task-workflow`**. Do not ask the user to choose shared versus agent scope.

### 2. Inspect before asking

Load the `/update-project-context` instructions and their active storage mechanics. Resolve this handoff through `[PROJECT-ACCESS]` (absent means `markdown`): under `mcp`, call the project layer's `read_procedure("update-project-context")`; under `markdown`, read the installed command. Fetching instructions does not perform a write.

Use that writer's list and read operations for the current project's **shared** layer, with the active HOME. Select only entries whose theme is exactly `task-workflow`:

- No match: prepare a new entry.
- One match: read its complete body and retain its address for updating.
- Multiple matches: report the ambiguity and stop before writing; ask which entry is authoritative. Do not merge, delete or pick one automatically.
- A listed entry that cannot be read is a load failure, not permission to create a duplicate.

Inspect relevant existing integration context and the user's supplied details. Reuse confirmed setup and do not ask settled questions again. Ignore agent-private and related-project workflow entries as configuration sources for this project. Read only non-secret integration configuration; never inspect credential stores or put tokens into the entry.

### 3. Collect the workflow

Ask for only the missing or conflicting details needed to describe:

| Detail | What must be specified |
|---|---|
| Tracker and connection | The task system and the existing tool, MCP connection or API used to read it |
| Project scope | Workspace, project, board or list identifiers and boundaries that limit the query |
| Account and assignment | Which account is used, what “me” means, and how agent-assigned work is identified |
| Queries | Active-task filters, human-handoff filters, relevant statuses and pagination |
| Report | Counts or items to show, what each count means, and behavior for an empty result |
| Unavailable connection | What awakening reports when tools, authorization or project scope cannot be established |

Use the tracker's actual capabilities rather than imposing another vendor's labels or states. A query can select one collection or a confirmed set of collections, but never broaden to the whole account merely because a project identifier is missing. Distinguish a confirmed absence of a handoff convention from an unknown one.

### 4. Validate without changing the tracker

When an existing connection is available, perform the smallest read-only check that verifies the selected account, project scope and query. A successful connection alone does not prove that the project or filters are correct. Cover pagination when reporting a total; label a partial result rather than presenting it as the total. Empty results can be valid when account, scope and filters are verified.

Never create, assign, comment on, complete or transition tasks as a probe. Do not install integrations, initiate login or OAuth setup, retrieve secrets, or change credentials. If human authentication is needed, explain that separately; configuring this workflow does not authorize connecting an account.

If any required detail or validation is unavailable, allow an **Incomplete** draft. Record exactly what is missing and what read-only check would establish it; do not invent identifiers, filters or a successful validation.

### 5. Draft and confirm

Build the entry using the Project Context Template for the active backend. Within Details, write a section named exactly **Awakening Hook** containing the tracker/connection, account/project scope, queries, reporting and failure behavior.

The hook itself must include:

- **Readiness**: `Ready` only after the necessary details and read-only validation are established; otherwise `Incomplete`.
- **Validation**: what was checked, when, and its result; or explicitly `Not validated`, with the missing details and next check. Do not store task bodies, credentials or a task-result snapshot as configuration.
- **Execution rule**: if readiness is `Incomplete`, report the missing setup and skip task queries. Do not try to repair or validate an incomplete setup automatically during awakening. If `Ready`, run only the declared read-only queries, and skip with an explanation if the connection or scope can no longer be established.

Show the target project and shared home (or store scope), whether this is a create or update, the proposed hook, readiness, validation evidence and remaining gaps. For an update, identify what changes and preserve unrelated workflow content. Changing trackers does not authorize deleting the old integration or its documentation.

**Wait for explicit approval before saving.** Approval to save an incomplete draft is not a claim that the tracker works. If the user changes the account, scope or query, revisit the affected validation before presenting the revised draft.

### 6. Save through the existing context writer

Start at Step 3 of `/update-project-context` with these already-confirmed inputs: the resolved project, active HOME, shared scope, exact theme `task-workflow`, and approved content. Do not restart its project/scope selection or reopen those decisions. Re-list before creating to catch a newly appeared entry; an unexpected collision returns to inspection and confirmation rather than overwriting.

Use its existing template, create/update operations, size checks and index maintenance; do not introduce a new record type, CRUD tool or workflow-specific store. Preserve unrelated body content and use the context writer’s backend instructions for description and tags. Stored entries do not contain template-version stamps.

Read back the saved entry and its shared index row. Verify the project, exact theme, hook, readiness and approved changes. If a write or read-back fails, report the partial result; do not claim the workflow is configured or retry a create blindly.

### 7. Report

Report the project, shared entry address, tracker and saved readiness. Distinguish **saved and validated** from **saved incomplete — awakening will skip**, naming the missing setup. State what was actually checked; saving configuration is not an end-to-end awakening test.

The hook is consumed by `/awaken-coder` for this project only. Do not run awakening or modify actual tasks as a side effect of saving.
