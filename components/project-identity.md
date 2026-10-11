# Project Identity (project component)

The rule that decides a session's project, and the related projects that widen its recall. **This is a component, not a standalone skill** — a procedure that reads or writes project memory invokes it.

*Owned by `agent-memory-project`. The value it resolves is the `[project]` the project home is keyed by.*

---

**The project is the repository the session works in**, so a submodule is the project rather than its parent. `git rev-parse --show-toplevel` gives the enclosing root (it stops at the submodule boundary, so it never returns the parent), and `git remote get-url origin` gives the name. A repository with no remote uses the folder name of its root, and with no repository at all the project is the working folder's name.

**Related projects** are the repositories beneath that root: read each `.gitmodules` on the way down, take the remote basename of every entry that is not vendored or read-only, and the resolved project plus those form the **project set**. Reading `.gitmodules` needs no initialization.

**The resolved repository is the session's project.** It names the project-context home and it is the value the session's memory is filed under; the set widens the episodic recall only.
