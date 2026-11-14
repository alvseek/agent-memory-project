# Project Identity (project component)

The rule that gives a project its identity, and the related repositories that widen a recall. **This is a component, not a standalone skill** — a procedure that reads or writes project memory invokes it.

*Owned by `agent-memory-project`. The value it resolves is the `[project]` the project home is keyed by.*

---

**A project is a git repository.** `git rev-parse --show-toplevel` finds the enclosing root, and because a submodule is its own repository that root stops at the submodule boundary rather than returning the parent. Its identity is the basename of `git remote get-url origin`, so a folder name cannot lie. A repository with no remote uses the folder name of its root, and outside any repository the identity is the working folder's name.

**Related projects** are the repositories beneath that one. Traverse submodules recursively, not just the current repository's immediate children: read its `.gitmodules`, resolve each entry's path relative to the repository containing that file, then read the child's `.gitmodules` and repeat until every included repository has been checked. Take the remote basename of every entry that is not vendored or read-only; the resolved project first, followed by these related repositories without duplicates, forms the **project set**. Before using the set, verify that every included repository was checked for nested submodules. A missing `.gitmodules` ends that branch; an unreadable or unavailable child does not prove it has no descendants. Reading an available `.gitmodules` needs no initialization; if a required nested file cannot be obtained, report that discovery is incomplete rather than silently treating the immediate children as the full set.

**The resolved repository names the project-context home and is the value a session's memory is filed under.** Which repository that is, the caller decides for itself: the awakening takes the one the session is standing in, and the wrap-up takes the one the work landed in, asking only when its candidate repositories do not settle that question. The set widens the recall: the episodes, the project-context index and the orientation maps all span it, while the resolved repository stays the home the session's memory is filed under.
