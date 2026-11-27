+++
format_version = 2
id = "pull-all"
kind = "procedure"
title = "Pull All (Project + Agent Memory)"
description = "Pull the latest changes for both the current working project and the agent-memory repository."
+++
# Pull All (Project + Agent Memory)

Pull the latest changes for both the current working project and the agent-memory repository.

## Arguments

`$ARGUMENTS`

- `/pull-all` → Pull both repos

---

## Procedure

### Step 1: Pull Project Files

Follow the [Pull Project](/pull-project) procedure for the current working directory.

### Step 2: Pull Agent Memory

Follow the [Pull Memory](/pull-memory) procedure for the agent-memory repo (the core owns its store location).

### Step 3: Summary

Report results for both:
```
Pull summary:
  - Project: [pulled/already up to date/error] — [details]
  - Memory: [pulled/already up to date/error] — [details]
```

---
