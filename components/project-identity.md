# Project Identity (project component)

The rule that gives a project its identity, and the related repositories that widen a recall. **This is a component, not a standalone skill** — a procedure that reads or writes project memory invokes it.

*Owned by `agent-memory-project`. The value it resolves is the `[project]` the project home is keyed by.*

---

**A project is a git repository.** `git rev-parse --show-toplevel` finds the enclosing root, and because a submodule is its own repository that root stops at the submodule boundary rather than returning the parent. Its identity is the basename of `git remote get-url origin`, so a folder name cannot lie. A repository with no remote uses the folder name of its root, and outside any repository the identity is the working folder's name.

**Related projects** are the repositories beneath that one: read each `.gitmodules` on the way down, take the remote basename of every entry that is not vendored or read-only, and the resolved project plus those form the **project set**. Reading `.gitmodules` needs no initialization.

**The resolved repository names the project-context home and is the value a session's memory is filed under.** Which repository that is, the caller decides for itself: the awakening takes the one the session is standing in, and the wrap-up takes the one the work landed in, asking when those are not the same. The set widens the episodic recall only.
