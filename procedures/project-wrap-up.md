+++
format_version = 2
id = "project-wrap-up"
kind = "procedure"
title = "Project Wrap Up Session"
description = "End-of-session full orchestrator (coding/environment add-on): push the project's work → update memory → refresh the orientation map → push everything those steps wrote → final summary with a push-completion gate."
argument_name = "mode"
argument_description = "Push mode: `agent` (default) or `all`"
+++
# Project Wrap Up Session

Close the coding session: push the project work, save what the session learned, and report what remains open.

Run without progress messages or routine confirmation. If a memory write needs a decision the session did not settle, defer that write, continue the remaining steps, and list it under **Needs review** in the final summary.

## Arguments

`$ARGUMENTS` = `[agent|all]`

- `agent` (default) — push only this agent’s work.
- `all` — push the full in-scope working trees, including unrelated changes.

---

## Procedure

Invoking `/project-wrap-up` authorizes the commits and pushes below in the selected mode.

### Step 1: Push the project work

Before updating memory, run `/push-project <mode>`. For the final summary, record each repository’s push result, any commit hashes, and how many files were left for the user.

### Step 2: Select the project and save memory

**Select the project.** Use the repository this session changed. If several changed, use the one the work was mainly about and tag the others. If no single repository was primary, file the episode without a project and tag all of them. If nothing changed, use the current repository.

@start component id="ref-1" ref="procedures/components/project-identity.md"
@end component

**Save project context first.** Pass each reusable project fact, its repository, and its scope to `/update-project-context`. Honor an explicit scope; otherwise use `shared` for project-wide facts and `agent` for role-specific facts. Default to `shared` when in doubt. Save access instructions, not credential values. If the repository for a fact is unclear, defer just that entry to **Needs review**.

**Save session memory.** Run `/update-memory` with the resolved project and tags, explicitly stating when there is no project. Let it choose the review window. Keep its results, **Tech Debts**, and **Next Steps** for the final summary.

### Step 3: Refresh the orientation map

Skip this step if no orientation documents changed. Otherwise, pass the changed paths (such as READMEs, architecture docs, flow diagrams, or ADRs) to `/map-orientation --session-touched [paths]`. Update mode checks whether the project already has a map and skips if none exists; do not create one. For the final summary, record the refresh count or the reason for skipping. If the procedure is unavailable, report that and continue.

### Step 4: Save and verify the remaining work

@start storage id="mechanics" ref="procedures/memory/storage-backends/{backend}.md" target="project-wrap-up"
@end storage

Verify that required writes succeeded and all in-scope Git changes were committed and pushed. Excluded repositories and unrelated files left in `agent` mode do not block completion.

### Step 5: Final summary

Use the report below for either outcome. Start with **Wrap-up complete** only if Step 4 passed. Otherwise start with **WRAP-UP INCOMPLETE** and name each unsaved path or record, its repository or store, and why it remains unsaved. Report only the pushes that applied to this backend.

```
Wrap-up complete (memory update: [mode reported by /update-memory]):

Memory update:
- Phase 1 — Promoted artifacts: project context: [updated/created — file / skipped] / reasoning: [added — pattern name / skipped] / knowledge: [added — entry name / skipped]
- Phase 2 — Session captured: [appended to / created] [episode] ([entry timestamp]) — [brief theme]; carry-forward: [N items / N/A]; promotions: [N markers / none]
- Phase 3 — Feeling captured: emotional [captured — polarity + clearest criterion / skipped — brief reason]

Orientation map: [refreshed N entries / no-op: reason]

Push — [agent / all]:
- [repository]: [✅ pushed at commit / no changes / ⚠️ incomplete: path and reason] — [user files left, if any]
- [excluded repo]: ⏭️ skipped (excluded)   ← only if applicable

📋 Open items going forward:

Tech debts:
- [item 1]
- [item 2]
(or "None declared")

Next steps:
- [item 1]
- [item 2]
(or "None declared")
```

Use the episode’s Tech Debts and Next Steps. If both lists are empty, write “No open items declared from this session.” Add **Needs review** only for deferred writes: name the proposed change and the decision needed. Do not count it as saved.
