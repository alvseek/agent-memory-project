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

Use the selected push mode for every push below.

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

Save the changes made by Steps 2–3 using the selected push mode. Invoking `/project-wrap-up` authorizes these commits and pushes.

@start storage id="mechanics" ref="procedures/memory/storage-backends/{backend}.md" target="project-wrap-up"
@end storage

Use the push results from Steps 1 and 4 to verify that every in-scope agent change was committed and pushed. Record any failed push or remaining agent work for the final summary. Excluded repositories and unrelated files left in `agent` mode do not block completion.

### Step 5: Final Summary (only visible output)

In either outcome, add **Needs review** only for deferred writes. Name the proposed change and the decision needed; do not count it as saved.

**Completion gate (per NO TODOS LEFT BEHIND, UUID a1b2c3d4)**: using the Step 4 verification (covering both the Step 1 project push and the Step 4 memory push), the wrap-up is **complete ONLY if every agent-work path is committed AND pushed** in every in-scope repo. A project repo that still holds the **user's own** uncommitted changes is still complete — leftover user files are expected and exempt (so are push-excluded repos). The wrap-up is **NOT complete** only if an **agent-work** path is uncommitted, a branch carrying agent commits is ahead of its remote, or an agent-work push failed → print the *WRAP-UP INCOMPLETE* block (at the bottom of this step) instead, and never claim completion.

**On success (every agent-work path committed + pushed)**, print this block:

```
Wrap-up complete (memory update: [mode reported by /update-memory]):

Memory update:
- Phase 1 — Promoted artifacts: project context: [updated/created — file / skipped] / reasoning: [added — pattern name / skipped] / knowledge: [added — entry name / skipped]
- Phase 2 — Session captured: [appended to / created] [filename] ([H3 timestamp]) — [brief theme]; carry-forward: [N items / N/A]; promotions: [N markers / none]
- Phase 3 — Feeling captured: emotional [captured — polarity + clearest criterion / skipped — brief reason]

Orientation map: [refreshed N entries / no-op: reason]

Push — agent work only (every agent-work path must be ✅):
- [project/submodule]: ✅ [commit-hash] pushed (project work) — [N user file(s) left for user / no user files left]
- agent-memory: ✅ [commit-hash] pushed (memory) / no changes
- [project memory files]: ✅ pushed with memory   ← only if Steps 2–3 wrote project files
- [excluded repo]: ⏭️ skipped (excluded — vendored/read-only)   ← only if the project has exclusions

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

If both Tech Debts and Next Steps are empty → replace both lists with *"No open items declared from this session."*

---

**On failure (ANY agent-work path not committed + pushed)** — do NOT print "Wrap-up complete". Print this block instead:

```
🚨 WRAP-UP INCOMPLETE — UNPUSHED AGENT WORK. NEED CONFIRMATION.

[Memory update / Orientation map / Open items sections — same as above]

Push — FAILED / INCOMPLETE (agent work not fully saved):
- [repo]: ⚠️ agent-work [uncommitted N files / branch ahead by N / push error: <reason>]
- [repo]: ✅ [commit-hash] pushed

⚠️ The agent's work is NOT fully saved to the remote. What remains, and where:
- [repo → which agent-work path is uncommitted/unpushed]
(User's own uncommitted files are expected and NOT listed here — only agent work blocks completion.)

Retry the push (or resolve the blocker) before leaving — the wrap-up is only complete when every agent-work path is committed AND pushed.
```
