# Update Project Context Protocol

Create or update project-specific context files. Routes new entries to **shared** (`shared-memory/[project-name]/context/`, for cross-agent universal facts) or **private** (`agent-[domain]/knowledge-base/[project-name]/`, for domain-specialized facts) based on a heuristic + user confirmation. Also supports moving an existing private entry to shared.

*How* the entries are physically stored is delegated to the active **storage backend** (see [Storage Mechanics](#storage-mechanics)).

## Arguments

`$ARGUMENTS`

- `/update-project-context [context]` → Create or update project context described in context
- `/update-project-context` → Will ask for context

If no arguments provided, ask: "What project context should I capture? (e.g., environment setup, deployment procedure, feature conventions)"

---

## Procedure

*IMPORTANT: Use TodoWrite tool with FULL VERBATIM copy of each step below (including all commands, examples, and sub-points) to prevent context loss and ensure complete execution*

### Step 1: Determine Project Name

Identify the project this context belongs to:
- **From working directory**: Infer project name from the current repository/folder name
- **From user input**: Ask if unclear: "Which project is this context for?"
- **Naming convention**: Use lowercase-hyphenated format (e.g., `ocx-platform`, `my-saas-app`, `data-pipeline`)

### Step 2: Determine Scope (Shared vs Private)

Decide whether this context belongs in the **shared** layer (cross-agent universal facts) or the **private** layer (domain-specialized facts for this agent only).

**Heuristic:**
- **Shared** (default when in doubt): Universal facts that are true for every agent on this project. Examples: GitButler usage, deployment process, env vars, repo conventions, infrastructure URLs.
- **Private**: Domain-specialized facts only one agent's role cares about. Examples: backend's DB schemas, frontend's component patterns, PM's stakeholder map.

> **Why this matters**: Under-sharing causes drift (agent A learns a fact, agent B doesn't know it). Over-sharing is just slightly noisier loads. When the call is genuinely ambiguous, default to **shared**.

Present the suggestion and wait for confirmation (show the reason, the suggested scope, and the alternative so [USER-NAME] can confirm or switch):

```
**Scope determination for "[context summary]":**

- [Brief reason for the suggestion — e.g., "This describes the project's deployment workflow, which applies to every agent."]

  > A) Shared — `shared-memory/[project-name]/context/` `✓✓`
  > B) Private — `agent-[domain]/knowledge-base/[project-name]/`

  ([Reason: why this scope is suggested.])

Reply with "shared", "private", or your preferred scope.
```

Based on the confirmed scope, the subsequent steps will use the matching path:
- **Shared scope**: `[AGENT-MEMORY-PATH]/shared-memory/[project-name]/context/`
- **Private scope**: `[AGENT-MEMORY-PATH]/agent-[domain]/knowledge-base/[project-name]/`

> **Storage location**: use the [HOME contract component]([path-to-agent-memory-project]/components/home-contract.md)'s `CONTEXT_DIR` (shared) and `KNOWLEDGE_DIR` (private). Use those dirs for every scope-aware step below (folder check, create, index).

> **Move operation**: If the user has asked to **move** an existing entry between scopes — a **promote** (private → shared, e.g. "move X to shared") or a **demote** (shared → private) — skip the rest of this procedure and follow the [Move Between Scopes Sub-Flow](#move-between-scopes-sub-flow) section below.

### Step 3: Ensure the Project Folder

Ensure the scope-aware project folder exists (**§ ensure-context-dir**), creating it if missing. Proceed to Step 4.

### Step 4: Determine Theme and Check Existing Entries

Identify the theme of the context being captured (e.g., `environment-setup`, `deployment`, `auth-module`, `database-conventions`).

List the existing entries in the scope-aware folder (**§ list-context-entries**) to check whether one already covers this theme:
- **If an existing entry matches**: Proceed to Step 5B (Update)
- **If no match**: Proceed to Step 5A (Create New)

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
2. Update or append the relevant content, then write it back (**§ update-context-entry**)
3. Update the `updated:` date in YAML frontmatter to today's date
4. Update `tags:` if new tags are relevant
5. Proceed to Step 6

### Step 6: Check the Entry Size

Housekeeping after writing (**§ check-entry-size**): under the size cap, proceed to Step 7. Over it, split the entry into one file per distinct sub-theme (each with its own frontmatter and tags), remove the original, and index every new file in Step 7.

### Step 7: Update the Context Index

Update the scope-aware context index (**§ update-context-index**) with this entry.

---

## Move Between Scopes Sub-Flow

When the user explicitly asks to move an existing entry between scopes, follow this sub-flow instead of the normal procedure. A **promote** is private → shared; a **demote** is shared → private.

> **Direction**: `[from]` is the source scope and `[to]` the target scope. Everything below is direction-neutral, and the collision check is always in the **target** scope.

### M.1: Identify Source Entry

Locate the source entry to move (**§ list-context-entries**).

If unclear which theme the user means, ask: "Which entry should I move? Available entries in [from]: [list]"

### M.2: Check Collision in the Target Scope

List the target scope's entries (**§ list-context-entries**) to check whether one with the same theme already exists.

- **If no collision**: Proceed to M.3
- **If collision**: **STOP**. Present the conflict to user: "A [to] entry with this name already exists. Options: A) merge the content manually first, B) rename the source entry before moving, C) cancel." Wait for user direction.

### M.3: Move to the Target Location

Ensure the target scope exists (**§ ensure-context-dir**), then move the entry's content verbatim to the target scope (**§ move-context-entry**).

### M.4: Remove the Source Entry

Remove the entry from the source scope (**§ delete-context-entry**).

### M.5: Update Both Indexes

Remove the entry from the source index and add it to the target index (**§ update-context-index**).

---

## Storage Mechanics

The operations referenced above — **§ ensure-context-dir**, **§ list-context-entries**, **§ read-context-entry**, **§ create-context-entry**, **§ update-context-entry**, **§ move-context-entry**, **§ delete-context-entry**, **§ check-entry-size**, **§ update-context-index** — are defined by the **active storage backend**:

- **Markdown (native)** — follow `storage-backends/markdown.md` → its `update-project-context` section.
- **DB (Hermod)** — the equivalents live in `storage-backends/db.md` → its `update-project-context` section (not yet implemented).

See the seam contract at `storage-backends/README.md` for how this swap works.
