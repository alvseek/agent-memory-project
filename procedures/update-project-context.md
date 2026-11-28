+++
format_version = 2
id = "update-project-context"
kind = "procedure"
title = "Update Project Context Protocol"
description = "Create or update project-specific context entries."
argument_name = "project"
argument_description = "The project to update. If not supplied, resolve it from Git or ask."
+++
# Update Project Context Protocol

Save project-specific knowledge for future sessions. Create or update an entry shared by the project’s agents or private to one agent. Move an existing entry between those scopes only when explicitly requested.

## Arguments

`$ARGUMENTS`

**`project`** — the project to update. Use the name supplied by the user or caller; otherwise resolve it in Step 1. Record the fact identified by the caller or in the conversation. If a direct request doesn’t identify a fact, ask what to save.

---

## Procedure

### Step 1: Determine Project Name

If the project was supplied, use it. Otherwise, run `git rev-parse --show-toplevel` to find the current repository. Use the repository name from `git remote get-url origin`, dropping a trailing `.git`. If there is no `origin`, use the repository root’s folder name.

If no project was supplied and the current directory is outside Git, ask “Which project should I update?” before writing.

### Step 2: Determine Scope (Shared vs Agent)

Use the scope supplied by the user or caller without asking again. If none was supplied, suggest `shared` for project-wide facts or `agent` for role-specific facts, give a brief reason, and ask the user to confirm. When in doubt, suggest `shared`.

Based on the confirmed scope, the markdown backend reads and writes the matching path:
- **Shared scope**: `[AGENT-MEMORY-PATH]/shared-memory/[project-name]/context/`
- **Agent scope**: `[AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]/`

A store keeps no path: its mechanics say which layer a row lands in.

> **Storage location**: use the HOME contract component's `CONTEXT_DIR` (shared) and `KNOWLEDGE_DIR` (agent). Use those dirs for every scope-aware step below (folder check, create, index).

@start component id="ref-1" ref="procedures/components/home-contract.md"
@end component

> **Move operation**: If the user has asked to **move** an existing entry between scopes — a **promote** (agent → shared, e.g. "move X to shared") or a **demote** (shared → agent) — skip the rest of this procedure and follow the [Move Between Scopes Sub-Flow](#move-between-scopes-sub-flow) section below.

### Step 3: Ensure the Project Folder

Ensure the scope-aware project folder exists (**§ ensure-context-dir**), creating it if missing. Proceed to Step 4.

### Step 4: Determine Theme and Check Existing Entries

Identify the theme of the context being captured (e.g., `environment-setup`, `deployment`, `auth-module`, `database-conventions`).

List the layer's existing entries (**§ list-context-entries**) to check whether one already covers this theme:
- **If an existing entry matches**: Proceed to Step 5B (Update)
- **If no match**: Proceed to Step 5A (Create New)

> **A theme is a name, not an address.** This comparison is the only thing the theme decides, and it decides exactly one question: create, or update. How an entry is then read, changed or retired is the storage backend's business, and a store's answer may be more than one call.

### Step 5A: Create New Context Entry

1. Create the new entry from the [Project Context Template]([path-to-agent-memory-project]/templates/project-context-template.md) (**§ create-context-entry**).
2. Fill the YAML frontmatter:
   - `project`: the project name from Step 1
   - `tags`: relevant feature/module tags for selective loading (e.g., `[environment, setup, vm, gcloud]`)
   - `description`: one-line summary
   - `created`: today's date
   - `updated`: today's date
3. Fill the markdown sections (Purpose, Quick Reference, Details, Sources)
4. Proceed to Step 6

### Step 5B: Update Existing Context Entry

1. Read the existing entry (**§ read-context-entry**)
2. Change its body (**§ update-context-entry**): edit the part that changed, append the new content, or rewrite the document, whichever the backend supports
3. Update the `updated:` date in YAML frontmatter to today's date
4. Update `description:` and `tags:` where they changed, in the frontmatter **and** wherever the backend's index keeps them (a store keeps the first as the row's `content_summary`)
5. Proceed to Step 6

### Step 6: Check the Entry Size

Housekeeping after writing (**§ check-entry-size**): under the size cap, proceed to Step 7. Over it, split the entry into one file per distinct sub-theme (each with its own frontmatter and tags), remove the original, and index every new file in Step 7.

### Step 7: Update the Context Index

Update the scope-aware context index (**§ update-context-index**) with this entry.

---

## Move Between Scopes Sub-Flow

When the user explicitly asks to move an existing entry between scopes, follow this sub-flow instead of the normal procedure. A **promote** is agent → shared; a **demote** is shared → agent.

> **Direction**: `[from]` is the source scope and `[to]` the target scope. Everything below is direction-neutral, and the collision check is always in the **target** scope.

### M.1: Identify Source Entry

Locate the source entry to move (**§ list-context-entries**).

If unclear which theme the user means, ask: "Which entry should I move? Available entries in [from]: [list]"

### M.2: Check Collision in the Target Scope

List the target scope's entries (**§ list-context-entries**) to check whether one with the same theme already exists.

- **If no collision**: Proceed to M.3
- **If collision**: **STOP**. Present the conflict to user: "A [to] entry with this name already exists. Options: A) merge the content manually first, B) give the source entry a different theme first, C) cancel." Wait for user direction.

### M.3: Move to the Target Location

Ensure the target scope exists (**§ ensure-context-dir**), then move the entry's content verbatim to the target scope (**§ move-context-entry**).

### M.4: Ensure the Source Entry Is Gone

Check the source layer for the entry (**§ list-context-entries**) and remove it if it is still there (**§ delete-context-entry**). A backend whose move already removes the source leaves nothing to do here, and its own mechanics say so.

### M.5: Update Both Indexes

Remove the entry from the source index and add it to the target index (**§ update-context-index**).

---

@start storage id="db-preamble" ref="procedures/memory/storage-backends/{backend}.md" target="all-procedures" applies_to="db"
@end storage
@start storage id="mechanics" ref="procedures/memory/storage-backends/{backend}.md" target="update-project-context"
@end storage
