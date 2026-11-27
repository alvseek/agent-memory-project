+++
format_version = 2
id = "push-all"
kind = "procedure"
title = "Push All (Project + Agent Memory)"
description = "Commit and push both the current working project and the agent-memory repository — either the **full tree** of each (`all`) or **only the agent's own work** (`agent`). A thin composition of the two leaf pushers in whichever mode you name; it adds no git logic of its own."
+++
# Push All (Project + Agent Memory)

Commit and push both the current working project and the agent-memory repository — either the **full tree** of each (`all`) or **only the agent's own work** (`agent`). A thin composition of the two leaf pushers in whichever mode you name; it adds no git logic of its own.

## Arguments

`$ARGUMENTS` = `[all|agent] [message]`

- **Mode** (first token, optional): `all` (default) stages the whole working tree in both repos; `agent` stages only the agent's own work — agent-produced project paths, plus this agent's own memory — leaving the user's unrelated changes and other agents' in-flight memory untouched. Use `agent` from an automatic flow, `all` when you deliberately mean everything.
- **Message** (remainder, optional): commit message for every repo committed. If omitted, auto-generate from the staged changes.
- If the first token is not literally `all` or `agent`, mode defaults to `all` and the **entire** `$ARGUMENTS` is treated as the message (backward-compatible).

Examples: `/push-all` (all, auto-msg) · `/push-all agent` · `/push-all "fix: …"` (all) · `/push-all agent "chore: session work"`.

---

## Procedure

*(Push-exclude policy, submodule ordering, and the `[ahead N]` push-state gate are all honored inside the delegated leaf pushers — this command adds no git logic of its own and holds no copy of those rules.)*

### Step 1: Resolve Mode

Parse `$ARGUMENTS`: if the first whitespace-delimited token is `all` or `agent`, that is the **mode** and the remainder is the **message**; otherwise mode = `all` and all of `$ARGUMENTS` is the message.

### Step 2: Push Project Files

Follow the [Push Project](/push-project) procedure in the resolved mode — `/push-project <mode> [message]` — for the current working directory.

### Step 3: Push Agent Memory

Follow the [Push Memory](/push-memory) procedure in the resolved mode — `/push-memory <mode> [message]` — for the agent-memory repo (the core owns its store location).

### Step 4: Summary

Aggregate the two leaf-push reports:

```
Push (mode: [all|agent]):
- [project/submodule]: [pushed — commit-hash / no changes] [— N user file(s) left for user (agent mode)]
- agent-memory: [pushed — commit-hash / no changes] [— other agents' files left untouched (agent mode)]
- [excluded repo]: skipped (excluded)
```

---
