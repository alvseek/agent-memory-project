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

@start component id="ref-1" ref="procedures/components/home-contract.md" applies_to="markdown"
@end component

### If the user asks to move an entry

A move changes an existing entry from `agent` to `shared`, or from `shared` to `agent`, without changing its content. For a create or update, skip to Step 2.

1. Identify the entry in the source scope. If the request could refer to several entries, ask which one to move.
2. Check the target scope for the same theme (**§ list-context-entries**). If it already exists there, stop and ask whether to merge, use a different theme, or cancel. Do not overwrite it.

@start storage id="prepare-move-directory" ref="procedures/memory/storage-backends/{backend}.md" target="ensure-project-context-directory" applies_to="markdown"
@end storage

3. Move the entry verbatim (**§ move-context-entry**). Verify the source entry is gone; remove it only if the move left it there (**§ delete-context-entry**).
4. Ensure the source and target indexes reflect the move (**§ update-context-index**), then finish. Do not run the create/update steps.

### Step 2: Determine Scope (Shared vs Agent)

Use the scope supplied by the user or caller without asking again. If none was supplied, suggest `shared` for project-wide facts or `agent` for role-specific facts, give a brief reason, and ask the user to confirm. When in doubt, suggest `shared`.

### Step 3: Find the entry

Use names and summaries to find likely matches in the selected project and scope. If the caller requires a particular entry or exact theme, stay within that target. Read the candidates to see whether they answer the same question as the fact being saved.

@start storage id="find-project-context-entry" ref="procedures/memory/storage-backends/{backend}.md" target="find-project-context-entry"
@end storage

- **Skip** if an entry already covers the fact accurately. Name it and finish without writing.
- **Update** if one entry answers the question but needs a correction or addition. Use that entry in Step 4B.
- **Create** if no entry answers the question. Choose a descriptive theme and continue to Step 4A.

If several entries still fit, use an explicitly identified target. Otherwise ask which to update on a direct request, or defer just that fact to **Needs review** during wrap-up. An unreadable candidate is not evidence that no entry exists.

### Step 4A: Create the entry

Fill the [Project Context Template]([path-to-agent-memory-project]/templates/project-context-template.md) with the resolved project, the fact, and its sources. Give the entry a one-line description that helps another agent decide when to read it. Use today’s date for both dates. Save it in the selected scope.

@start storage id="prepare-write-directory" ref="procedures/memory/storage-backends/{backend}.md" target="ensure-project-context-directory" applies_to="markdown"
@end storage

@start storage id="create-context-entry" ref="procedures/memory/storage-backends/{backend}.md" target="create-context-entry"
@end storage

Continue to Step 5.

### Step 4B: Update Existing Context Entry

1. Use the entry read in Step 3.
2. Change its body (**§ update-context-entry**): edit the part that changed, append the new content, or rewrite the document, whichever the backend supports
3. Update the `updated:` date in YAML frontmatter to today's date
4. Update `description:` and `tags:` where they changed, in the frontmatter **and** wherever the backend's index keeps them (a store keeps the first as the row's `content_summary`)
5. Proceed to Step 5

### Step 5: Check the Entry Size

Housekeeping after writing (**§ check-entry-size**): under the size cap, proceed to Step 6. Over it, split the entry into one file per distinct sub-theme (each with its own frontmatter and tags), remove the original, and index every new file in Step 6.

### Step 6: Update the Context Index

Update the scope-aware context index (**§ update-context-index**) with this entry.

---

@start storage id="db-preamble" ref="procedures/memory/storage-backends/{backend}.md" target="all-procedures" applies_to="db"
@end storage
@start storage id="mechanics" ref="procedures/memory/storage-backends/{backend}.md" target="update-project-context"
@end storage
