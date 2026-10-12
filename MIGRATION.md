# Migration Note — extracted from the memory core (2026-08-06)

The procedures under [`procedures/`](procedures/) were **moved out of** the memory core repo
(`agent-memory-system` / `control-files/procedures/`) into this standalone overlay repo as part of
**Phase 2** of the memory-core / coding-skill decoupling (ADR-012).

## Later move — the fleet (2026-10-08)

The **fleet** procedures (`ask-agent`, `delegate-agent`, `setup-fleet`), scripts (`fleet-scripts/`),
and templates were moved **out** of this overlay into the sibling repo
[`agent-memory-fleet`](https://github.com/alvseek/agent-memory-fleet) (`hermod-fleet`). The overlay
keeps exactly one pointer to it, in `awaken-coder`. See that repo's `MIGRATION.md`.

## Later move — the wizards (2026-10-09)

The **wizard + QA + implement-plan cluster** was moved **out** of this overlay into the sibling repo
[`agent-memory-wizards`](https://github.com/alvseek/agent-memory-wizards) (`hermod-wizards`):
the six wizard protocols, `implement-plan`, the QA pipeline, `wait-options-coding`, their components,
the plan templates, and three templates. The overlay keeps the shell (`awaken-coder`,
`project-wrap-up`, `dockerize`, push/pull) and the project / doc surface. Nothing calls the wizards
layer, so it declares no access; it reads only the core. The three doc generators now fall back to
the core `/wait-options` on their ambiguous-scope branch. See that repo's `MIGRATION.md` and the
overlay's `docs/adr/2026-10-09-hermod-wizards-extraction.md`.

## What moved

31 add-on procedures relocated from `control-files/procedures/` — wizards, doc-gen, QA, fleet,
`map-orientation`, `localize-context`, and `pull-*`/`push-*` — joined by the 3 overlay files authored
in Phase 1 (`awaken-coder.md`, `localized-memory-workflow.md`, `project-wrap-up.md`).

## History

Per-file commit history for the moved procedures **remains in the core repo** (`agent-memory-system`).
This overlay starts with a **fresh initial commit** rather than a filtered history graft (decision:
fresh repo + migration note — simpler and safe; the authoritative history is preserved in the core).

## Accepted broken links

~230 references to the old `control-files/procedures/<name>.md` paths live in **frozen** episodic
memory and completed plans across the framework. These are **append-only archival records** and are
**left as-is** (framework convention already accepts broken links in `plans/completed/`). Only
**active** cross-references (per-agent memory files, `new-agent-template`, README/ARCHITECTURE, the
orientation map) are repointed — see the core repo's Phase 3 work.

## Later move — localization, and the rename to `agent-memory-project` (2026-10-09)

The **localization lane** (`localize-context`, `localized-memory-workflow`, and the
`## Localized Home Resolution` rule) was moved **out** into the sibling repo
[`agent-memory-local`](https://github.com/alvseek/agent-memory-local) (`hermod-local`), which also
owns the new `load-local-context` reader. This overlay was renamed
**`agent-memory-coding-skill` → `agent-memory-project`** and made **central-only**: its procedures no
longer resolve `home: project` themselves; they operate on the `HOME` contract
(`components/home-contract.md`, central default), and `agent-memory-local` resolves the localized
override. `awaken-coder` hands off to `/load-local-context` when it detects a localized project
(`.agents/` at cwd). The repo had already split twice (fleet 2026-10-08, wizards 2026-10-09); it is
now **four repos**: project, local, fleet, wizards.

The rename changed the installed identity: folder prefix `agent-coding-` → `agent-project-`,
manifest `.agent-memory-coding-skill-*` → `.agent-memory-project-*`, placeholder
`[path-to-agent-memory-coding-skill]` → `[path-to-agent-memory-project]`. Run
`setup-scripts/migrate-old-name.py` once to clear the pre-rename installs, then re-run the
platform installers. See `agent-memory-local`'s `MIGRATION.md` and
`docs/adr/2026-10-09-hermod-local-project-split.md`.

## 2026-10-12 — the doc cluster and `dockerize` left

Two more concerns left this repo, so the contents list above is superseded on those points:
the five doc generators and `discovery-contract` moved to `agent-memory-doc` (`hermod-doc`), and `dockerize` moved to `agent-memory-wizards`. This overlay now holds the shell, project memory, the orientation map and push/pull. The decision is recorded in ADR-024.
