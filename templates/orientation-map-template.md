---
project: "[project-name]"
description: "Orientation map for [project] — index of READMEs, architecture docs, flow diagrams, ADRs, and sub-project maps with staleness + role tracking."
created: "YYYY-MM-DD"
last_full_scan: "YYYY-MM-DD"
---

# Orientation Map — [project-name]

template_version: 2026-10-12-16-48

Index of orientation artifacts in this project. Used by agents at awakening (load into session context) and wrap-up (refresh entries the session touched) via the `/map-orientation` skill.

## Status Legend

- **useful** — current, accurate, future tasks will rely on it. Update when scope changes.
- **stale-but-valuable** — could be useful if updated. Repair on demand when next task hits its scope.
- **obsolete** — neither current nor valuable. Ignore. Optional: archive or delete.
- **unverified** — mtime changed since `last_verified`, or never verified. Next task touching its scope verifies and updates status.

## Scope Legend

- **shared** — relevant to every role on this project. Always loaded.
- **role-private** — relevant only to roles listed in `roles`. Other roles skip.
- **cross-readable** — relevant to roles listed in `roles`, PLUS Architect and QA always (cross-cutting roles read everything).

## Type Legend

- **7q-readme** — 7 Questions Framework README (any scope: root, module, sub-component)
- **architecture-map** — project-wide architecture navigation doc (ARCH-map.md style)
- **architecture-overview** — single-section architecture deep-dive (ARCH-overview, ARCH-domain-*, etc.)
- **flow-diagram** — Mermaid or similar diagram showing data/control flow (`.mmd`, `.mermaid`); the flow *deep-dive* altitude (`doc_type: flow`)
- **flow-journey-map** — the flow *map* altitude: how flows chain into journeys (`doc_type: flow-journey-map`, `docs/flows/journey-map.md`)
- **domain-model** — data-model / ERD doc: entities + relationships + cardinality (Mermaid `erDiagram` / `classDiagram`) (`doc_type: domain`, under `docs/domain/`)
- **domain-context-map** — the domain *map* altitude: how bounded contexts relate (DDD context map; `doc_type: domain-context-map`, `docs/domain/context-map.md`)
- **adr** — Architecture Decision Record (single decision document)
- **orientation-map-link** — pointer to a child orientation map for a sub-project (fractal scaling). The `child_map` field names the sub-map file.
- **other** — orientation artifact that doesn't fit above categories (CONTRIBUTING.md, GLOSSARY.md, etc.)

## Note on Creation

The agent who runs `/map-orientation create` for the first time scans ALL orientation docs in the project regardless of its own role. Creation is role-blind by necessity — the map must be complete for future agents of every role to filter against it. Role filtering applies at CONSUMPTION (which target docs each role actually reads), not creation.

---

## Entries

### `README.md`

- **type**: 7q-readme
- **scope**: shared
- **roles**: []
- **status**: useful
- **tags**: [overview, entry-point]
- **last_verified**: YYYY-MM-DD
- **verified_by**: [agent-role] / [context, e.g., "2026-06-03 session" or "awakening scan"]
- **update_trigger**: "when project tech stack, setup steps, or commands change"
- **notes**: "Project root README. First read for new contributors and agents."

### `docs/architecture/ARCH-map.md`

- **type**: architecture-map
- **scope**: shared
- **roles**: []
- **status**: useful
- **tags**: [navigation, architecture, all-modules]
- **last_verified**: YYYY-MM-DD
- **verified_by**: [agent-role] / [context]
- **update_trigger**: "when ARCH-* sub-docs change OR new architecture decisions logged"
- **notes**: "Single source of truth for project-wide structure. Navigate from here."

### `apps/api/` (sub-project)

- **type**: orientation-map-link
- **scope**: role-private
- **roles**: [backend]
- **status**: useful
- **child_map**: orientation-map-api.md
- **last_verified**: YYYY-MM-DD
- **verified_by**: [agent-role] / [context]
- **update_trigger**: "when sub-project structure changes OR new docs added under apps/api/"
- **notes**: "Backend API sub-project. Has its own orientation map covering apps/api/**. Load when working on backend tasks."

### `apps/web/components/Button/README.md`

- **type**: 7q-readme
- **scope**: role-private
- **roles**: [frontend]
- **status**: useful
- **tags**: [component, ui]
- **last_verified**: YYYY-MM-DD
- **verified_by**: [agent-role] / [context]
- **update_trigger**: "when Button component API changes"
- **notes**: "Button component docs. Frontend-only — backend doesn't need this."

### `docs/integration-contracts.md`

- **type**: other
- **scope**: cross-readable
- **roles**: [backend, frontend, mobile]
- **status**: useful
- **tags**: [contracts, integration, api]
- **last_verified**: YYYY-MM-DD
- **verified_by**: [agent-role] / [context]
- **update_trigger**: "when API contracts change between FE/BE/mobile"
- **notes**: "API contract specs. Anyone touching cross-boundary work needs this. Architect/QA always load."

### `docs/flows/order-flow.mmd`

- **type**: flow-diagram
- **scope**: cross-readable
- **roles**: [backend, frontend]
- **status**: stale-but-valuable
- **tags**: [order, fulfillment, multi-system]
- **last_verified**: YYYY-MM-DD
- **verified_by**: [agent-role] / [context]
- **update_trigger**: "when order processing flow changes across submodules"
- **notes**: "End-to-end order flow. Last refresh predates 2026-04 cancellation-path fix — verify on next order-related task."

### `docs/decisions/ADR-001-database-choice.md`

- **type**: adr
- **scope**: shared
- **roles**: []
- **status**: useful
- **tags**: [decision, database]
- **last_verified**: YYYY-MM-DD
- **verified_by**: [agent-role] / [context]
- **update_trigger**: "supersede only — ADRs are append-only history"
- **notes**: "Original Postgres-over-Mongo decision. Reference for future data-store decisions."

### `docs/legacy/old-architecture.md`

- **type**: other
- **scope**: shared
- **roles**: []
- **status**: obsolete
- **tags**: [legacy]
- **last_verified**: YYYY-MM-DD
- **verified_by**: [agent-role] / [context]
- **update_trigger**: "none — superseded by docs/architecture/ARCH-map.md (2026-04)"
- **notes**: "Pre-restructure architecture doc. Kept for historical context only. Do not consult for current state."

---

## How to Use This File

**Agents at awakening**: Loaded into session context automatically by `/map-orientation` (bare call). Reference entries by `path` when consulting orientation docs for a task. The role-filter rules:

- Architect / QA → load + consult ALL entries (cross-cutting roles)
- Other roles → load + consult `scope: shared` + `scope: role-private/cross-readable` where your role is in the `roles` array

For `type: orientation-map-link` entries: if the entry passes the role filter, ALSO load the child map.

**Agents at wrap-up**: If your session updated any orientation doc, `/map-orientation --session-touched [paths]` updates its `last_verified` date and status. If your session DISCOVERED that an entry's status is wrong (useful doc is actually stale, obsolete doc is actually still valuable), update the entry directly via `/update-project-context`.

**Humans reviewing**: Spot-check `verified_by` and `update_trigger` fields. Spot-check `scope` and `roles` assignments — auto-guess from path heuristic may need correction.

---

## Customization Notes (delete after first fill)

- Example entries above demonstrate the schema with all scope/role/type combinations. Replace with this project's actual orientation artifacts.
- Add new entries as new orientation docs are created (via `/map-orientation --session-touched [new-path]`).
- Remove example entries that don't apply to this project.
- For monorepos with sub-projects: parent map references sub-maps via `type: orientation-map-link` entries. Sub-maps live in the same `context/` folder with suffix naming (`orientation-map-[subproject].md`).
- For projects with no role split (single-role projects like undanganaku, agent-memory framework): all entries get `scope: shared`, `roles: []`. Role filtering becomes a no-op.
