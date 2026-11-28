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

### Step 2: Project Context Gate + Memory Update (silent)

**Resolve the project from the work, then state it.** The candidates are the repositories this session changed: the ones the pushes covered, plus any working tree that moved, with the repository at the working directory as the fallback when nothing changed. Then:

- **One candidate** → that repository is the session's project.
- **Several, one carrying the subject** (the majority of the session's changed paths, or the repository the session's own project-context or map writes name) → that repository is the session's project, and the others go into the record's `tags`, which `search` reads.
- **Several, none carrying the subject** → no project at all, and every repository goes into the `tags`.

Pass the resolved project (or explicitly no project and the repository tags) to the memory update so it does not infer a different one from the working directory. If a project-specific fact cannot be attributed to one repository, defer that entry for review rather than guessing or waiting for an answer.

@start component id="ref-1" ref="procedures/components/project-identity.md"
@end component

**Save project context first.** For each reusable project fact, pass its project, content, and scope to `/update-project-context`. Use the user’s explicit scope when given; otherwise use `shared` for project-wide facts and `agent` for role-specific facts. Default to `shared` when in doubt. Save access instructions, not credential values. Skip this step if there is nothing to save. Saving before `/update-memory` lets it record completed writes as promotions.

**Then — the memory update**: Run `/update-memory` and let it determine how much of the session to review. Capture its results (mode, gate decisions, episodic entry, carry-forward count, promotions, emotional status) as data for Step 5, together with the **`Tech Debts` + `Next Steps`** it hands up from the sub-episode just written (the return contract `/update-episodic` declares). Print nothing here — it all folds into Step 5.

> **Why this borrows one step rather than running the core `/wrap-up` whole.** That procedure also *persists* the memory store immediately after updating it, which here would fire too early: Step 3 refreshes the orientation map and Step 4 has to capture those writes too. So take the memory update and its returned open items, and leave the persistence to Step 4, where one call covers both repos at once.

### Step 3: Refresh Orientation Map (silent)

If this session touched orientation docs (READMEs, architecture, flow diagrams, ADRs):

`/map-orientation --session-touched [path1,path2,...]`

Silent no-op if no map exists or no orientation docs touched. Capture refresh count / no-op reason for Step 5.

### Step 4: Persist Everything Steps 2–3 Wrote (silent) — MANDATORY

Execute **§ persist-store** — the active storage backend's persistence op, covering the agent-memory store and the working project together. Invoking `/project-wrap-up` IS the authorization to commit + push. Its memory half captures the episodic / emotional / reasoning / knowledge writes that the Step 1 project push ran too early to include; its project half captures the project memory, orientation, and context files Steps 2–3 just wrote. In the default `agent` mode both leaves stage only this agent's own work (never a blanket `git add -A`), leaving other agents' in-flight memory and the user's project changes untouched; `all` mode pushes both full trees.

> **Why the project is pushed twice, and why that is not redundant.** Step 1 exists so a merge request can open without waiting for the memory update. Step 4 exists because Steps 2–3 write more files after that. Collapsing them into a single push at either end breaks the completion gate: push only at the start and the memory written afterwards is never saved, so the gate reports INCOMPLETE every run; push only at the end and the early merge request Step 1 exists for never happens.

Tool calls visible (git commands); capture per-repo commit hashes + agent-work-pushed status for Step 5.

**Then verify (drives the Step 5 completion gate)**: from the leaf pushers' `git status -sb [ahead N]` verification (Step 4 of `/push-project` + `/push-memory`, reached directly in Step 1 and through the persistence op in Step 4) across both pushes, record per repo whether **every agent-work path is committed AND pushed** (branch not ahead of remote) + a count of user files left. **Excluded repos are exempt** (report as `skipped (excluded)`). Do NOT attempt elaborate recovery — if an *agent-work* push fails or any agent-work path remains, that is carried to Step 5, where the wrap-up fails loudly.

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

---

@start storage id="db-preamble" ref="procedures/memory/storage-backends/{backend}.md" target="all-procedures" applies_to="db"
@end storage
@start storage id="mechanics" ref="procedures/memory/storage-backends/{backend}.md" target="project-wrap-up"
@end storage
