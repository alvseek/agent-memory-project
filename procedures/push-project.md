+++
format_version = 2
id = "push-project"
kind = "procedure"
title = "Push Project Files"
description = "Commit and push changes in the current working project repository — either the full tree (all) or only the agent's own work (agent)."
argument_name = "mode"
argument_description = "`all` or `agent`, optionally followed by a commit message"
+++
# Push Project Files

Commit and push changes in the current working project repository — either the **full tree** (`all`) or **only the agent's own work** (`agent`).

## Arguments

`$ARGUMENTS` = `[all|agent] [message]`

- **Mode** (first token, optional): `all` (default) stages the whole working tree; `agent` stages **only the agent's own work** and leaves the user's unrelated changes untouched (safe for automatic flows like `/wrap-up`).
- **Message** (remainder, optional): commit message for every repo committed. If omitted, auto-generate from the staged changes.
- If the first token is not literally `all` or `agent`, mode defaults to `all` and the **entire** `$ARGUMENTS` is treated as the message (backward-compatible).

Examples: `/push-project` (all, auto-msg) · `/push-project agent` · `/push-project "fix: …"` (all) · `/push-project agent "chore: wrap-up session work"`.

---

## Procedure

> **Push-exclude list (check first).** Read and follow the Push Exclude Policy component — excluded repos/submodules are never committed or pushed and never counted against completion (`skipped (excluded)`).

@start component id="ref-1" ref="procedures/components/push-exclude-policy.md"
@end component

> **In-scope repos.** The working project repo and its **owned git submodules** (recurse). A superproject's `git status` shows a dirty submodule only as a one-line gitlink — it does NOT reveal uncommitted files *inside* the submodule, and `git add` on the gitlink records only the pointer. So you MUST enter each owned submodule and commit/push **inside it first**, then commit the updated pointer in its superproject. Always process submodules **before** their superproject.

### Step 1: Resolve Mode

Parse `$ARGUMENTS`: if the first whitespace-delimited token is `all` or `agent`, that is the **mode** and the remainder is the **message**; otherwise mode = `all` and all of `$ARGUMENTS` is the message.

### Step 2: Stage per Mode

**Mode `all`** — full tree: in each in-scope repo, `git add -A`.

**Mode `agent`** — the agent's own work only. In each in-scope project repo / owned submodule, stage **ONLY**:
- files the agent created/edited **this session** — cross-check the newest episode's `Deliverables` / `Outcomes` plus your own Write/Edit history.
- agent-produced files from **earlier sessions still uncommitted** — identify from prior episode deliverables.
- 🚨 **NEVER `git add -A` in `agent` mode.** Stage the agent-work paths explicitly. Every other dirty file is the **user's** — leave it untouched, report it as `left for user`, never commit it.
- ⚠️ **When the set is uncertain** (long or context-compacted session — recalled edit history may be incomplete, and the episode may miss late edits): do NOT silently drop a dirty file you can't confidently classify. Surface the ambiguous paths (whatever in `git status` you're not sure is the user's) and confirm before finishing. The completion gate can catch an agent path left *unpushed*, but it CANNOT detect an *under-inclusive* set — a missed agent file would be silently abandoned, so resolve the doubt here.

### Step 3: Commit & Push (submodules before superprojects)

For each in-scope repo, **innermost submodule first**:

1. **Stage** per Step 2 (`all` → `git add -A`; `agent` → `git add <agent-work paths>`, never `-A`).
2. Run `git diff --cached --stat` to confirm what's staged. **If nothing is staged AND the branch is not ahead of its remote** (`git status -sb` shows no `[ahead N]`), this repo is already done → skip it silently. Do **NOT** halt — continue to the next repo.
3. Otherwise **commit** the staged changes (provided message, or auto-generate), then **`git push`**. **Message style — self-contained**: describe *what changed + why* in plain prose; never reference plan-internal or process artifacts — decision letters (`A1`, `OQ2`), ADR numbers (`ADR-10`), or plan step/phase numbers. See the *Durable Artifacts Don't Point At Plans* coding reasoning pattern, which covers code comments and test names too.
4. After pushing a **submodule**, stage + commit its **updated pointer** in the superproject.
5. Treat a **non-zero `git push` exit** as a failure for that repo — do not retry elaborately; carry it to Step 4.

### Step 4: Verify & Report

In every in-scope repo run **`git status -sb`** — the `-sb` branch header surfaces `[ahead N]`, i.e. locally-committed-but-**unpushed** work that plain `git status --short` hides. A repo is **done** only when **both**: (a) nothing in scope is dirty, AND (b) its branch is **not ahead of its remote**. In `agent` mode, any files still dirty must be the user's — expected, reported as `left for user`, never a failure. Excluded repos → `skipped (excluded)`.

```
Push (mode: [all|agent]):
- [project/submodule]: [pushed — commit-hash — N user file(s) left for user (agent mode) / no changes]
- [excluded repo]: skipped (excluded — vendored/read-only)
```

---
