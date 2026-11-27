+++
format_version = 2
id = "push-exclude-policy"
kind = "component"
title = "push-exclude-policy"
description = "Procedure content: push-exclude-policy."
+++

**Before pushing, consult the project's push-exclude list** — `push-policy.md` in the shared context dir (`CONTEXT_DIR`, per the HOME contract).

Repos and submodules listed there are **vendored / third-party / read-only**: never commit or push them, and do not count their state against completion. Report each as `skipped (excluded)` so the skip is visible rather than silent. An absent file means no exclusions — push everything in scope as normal.

**How one comes to exist**: `/update-project-context` writes it. Describe what must not be pushed and why, and it creates or updates `push-policy.md` under the resolved home and registers the entry in that project's context index. Nothing creates the file automatically during a push — an exclusion is a deliberate statement about ownership, not something a push flow should infer from a repo looking untouched.
