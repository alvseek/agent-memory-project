# agent-memory-project

The **coding/repo add-on overlay** for the [agent-memory](https://github.com/alvseek/agent-memory-system) framework.

This repo holds the coding- and repository-oriented procedures that sit **on top of** the memory core: the coding shell (awaken/wrap-up), project memory, and push/pull. The wizards + QA moved to [`agent-memory-wizards`](https://github.com/alvseek/agent-memory-wizards) (2026-10-09), the fleet to [`agent-memory-fleet`](https://github.com/alvseek/agent-memory-fleet) (2026-10-08), and the localization lane to [`agent-memory-local`](https://github.com/alvseek/agent-memory-local) (2026-10-09) — on that last day this repo was renamed **agent-memory-project** and made central-only. A coding agent installs the memory core **plus** this overlay; a plain chat agent installs the core alone.

## Relationship to the memory core

- **Standalone, independent repo** — a *peer* of the core ([`agent-memory-system`](https://github.com/alvseek/agent-memory-system) / `control-files`). It is **not** a git submodule of the core or of the parent aggregator.
- **One-way dependency**: this overlay references the core; the **core never references this overlay by name** (enforced by the core's `check-core-invariant.sh` guard).
- **Additive composition, not override**: the consuming agent is the composition point. `procedures/awaken-coder.md` simply orchestrates *"run the core `/awaken-agent`, then coding reasoning + localized-home + orientation map + fleet."* Nothing here overrides a core procedure.

## Contents (`procedures/`)

- **Awakening overlay**: `awaken-coder.md` (composes the core awaken, then hands off to `agent-memory-local` when a project is localized)
- **Lifecycle**: `project-wrap-up.md` (composes the core `/wrap-up`, then push + map-orientation)
- **Wizards** (moved out 2026-10-09): the wizard protocols + `implement-plan` now live in the sibling repo [`agent-memory-wizards`](https://github.com/alvseek/agent-memory-wizards) (`hermod-wizards`).
- **Doc-gen** (moved out 2026-10-12): the doc generators and `discovery-contract` now live in [`agent-memory-doc`](https://github.com/alvseek/agent-memory-doc) (`hermod-doc`); `dockerize` moved to [`agent-memory-wizards`](https://github.com/alvseek/agent-memory-wizards)
- **QA** (moved out 2026-10-09): the QA pipeline (`analyze-code-quality`, `generate-standard`, `pixel-wizard`, `setup-qa-visual-instrument`, `map-qa-instrument`, `build-qa-bench`, `integration-test`, `run-qa-test`, `qa-status`, `generate-qa-checklist`) now lives in [`agent-memory-wizards`](https://github.com/alvseek/agent-memory-wizards) (`hermod-wizards`).
- **Repo / integration**: `map-orientation`, `update-project-context`, `load-project-context`, `pull-all`/`pull-project`, `push-all`/`push-project`
- **Storage backends** (`storage-backends/`): the seam the project-memory procedures delegate their mechanics to — `markdown` live, `db` declared and deferred (ADR-023).
- **Localization** (moved out 2026-10-09): `localize-context`, `localized-memory-workflow`, and the `HOME`-resolution rule now live in [`agent-memory-local`](https://github.com/alvseek/agent-memory-local) (`hermod-local`). This repo carries only `components/home-contract.md` (the central default) and hands off to `/load-local-context`.
- **Fleet** (moved out 2026-10-08): lives in the sibling repo [`agent-memory-fleet`](https://github.com/alvseek/agent-memory-fleet) (`hermod-fleet`). `awaken-coder` surfaces a one-line pointer to it — the commands, scripts, and templates are no longer here.

> **`push-memory`/`pull-memory`** live in the memory **core** (moved 2026-08-07) — persisting the memory store is the memory server's own job; the overlay's `push-all`/`pull-all` compose `/push-project` (overlay) + the core's `/push-memory`.

## Setup

This overlay ships its **own** installers (`setup-scripts/`) — it does not depend on the core's installer, and the core's installer does not reach into this repo. Install the **memory core first**, then this overlay:

```bash
# 1. Memory core (agent-memory-system / control-files):
python /path/to/control-files/procedures/setup-scripts/setup-all-claude-code.py

# 2. This overlay:
python setup-scripts/setup-all-claude-code.py
```

On Windows, double-click (or run) `setup-scripts\setup-all-claude-code.bat` — a thin wrapper that finds Python and runs the same installer. Requires Python 3; no other dependencies.

Both target `~/.claude/commands/` but keep **separate manifests** (core = `.agent-memory-manifest`, overlay = `.agent-memory-project-manifest`), so re-running either one cleans up only its own commands.

Codex and Antigravity consume the same procedures as **Agent Skills**, which they both read as a folder holding a `SKILL.md` with `name` and `description` frontmatter:

```bash
python setup-scripts/setup-all-codex.py         # -> ~/.agents/skills/
python setup-scripts/setup-all-antigravity.py   # -> ~/.gemini/config/skills/
```

Each honours `AGENT_MEMORY_TARGET_DIR`, keeps its own manifest, and registers `[path-to-agent-memory-project]` in that platform's global instructions file (`~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`) so the script and template paths inside an installed procedure resolve.

A skill is **model-invoked** rather than typed: the agent sees only each skill's name and description until a request looks like a match, then reads the body. So ask for a procedure in your own words — *"use the quick-wizard skill"* — rather than typing a slash command as you would in Claude Code.

## Status

Extracted from the memory core on **2026-08-06** (Phase 2 of the memory-core / coding-skill decoupling — see [ADR-012](https://github.com/alvseek/agent-memory-system) in the core repo). Wrapping this overlay as a 2nd-layer **MCP server** is the target delivery model but a **separate future project** — this repo is currently the procedure content that such a server will serve.

See [MIGRATION.md](MIGRATION.md) for the move details.

## License

Licensed under the [Apache License 2.0](LICENSE) — the same license the memory core carries, so a coding agent's two halves are under one set of terms. Attribution and the license notice travel with the work; see [NOTICE](NOTICE).

The procedures here are markdown that an agent *executes*, so the license covers them as source: copying a procedure into your own fleet, adapting it, or shipping it inside a commercial product is all permitted, provided you keep the notice.
