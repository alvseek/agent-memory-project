# High Wizard Plan

## **PROJECT INFO**
- **Project**: agent-memory-project (hermod-project)
- **Date**: 2026-10-12
- **Agent**: Claude Meta
- **Theme**: Scaffold `hermod-server` — the coding overlay's MCP server, serving `agent-memory-project`'s procedures and templates, spec mirrored from the Munnin server
- **Source Protocol**: `/high-wizard` — /high-wizard

*CRITICAL INSTRUCTION: To continue this plan: load the source protocol above, then inspect which sections below are filled vs unfilled to infer your current step.*

---

## **INHERITED CONTEXT**
*Filled at investigation step 0 with whatever was settled before this plan existed. The two sources are recorded separately and never merged — write "None" under a part that does not apply.*
*These decisions are **not yours to reopen**. If one looks wrong, STOP and surface it to [USER-NAME] — do not silently re-decide it here or in Confirmed Decisions below.*

### From the Parent Plan
- **Parent plan**: None — not a sub-plan.
- **Assigned scope**: N/A.
- **Integration contracts**: None.
- **Pushed-down open items**: None.

### From Pre-Planning Discussion
- **Discussion**: Pre-planning discussion with [USER-NAME], 2026-10-12 (this session).
- **Agreed scope**: Stand up `hermod-server`, the coding overlay's MCP server, scoped for now to `agent-memory-project` alone, built from a spec similar to the Munnin server (`agent-memory-server`).

| # | Settled decision | Chosen | His reason | Status |
|---|------------------|--------|------------|--------|
| 1 | Umbrella name | **Asgard** | "ok let's go with asgard" | Settled |
| 2 | Asgard's direct children | the deploy repos: `munnin-deploy` and the hermod deploy repo | "asgard will have munnin-deploy and hermod-project obviously" | Settled |
| 3 | The layer chain | deploy → server → content, one chain per capability. Munnin: `munnin-deploy` → `agent-memory-server` → `agent-memory-system` | "correct?" — verified true (deploy pins server, server pins control-files) | Settled |
| 4 | The coding server's name | **`hermod-server`** | "ok then hermod-server it is" | Settled |
| 5 | Bundling unit | one server per overlay, not per repo: the four hermod repos are content sources of one server | "instead of logging in / setup multiple hermod mcp. I don't see the benefit of it being separated mcp" | Settled |
| 6 | Future domains | a new overlay name per domain (Balder for 3D, Bragi for music), not a repo per capability | "we can use another overlay name (Balder for example)" | Settled |
| 7 | Munnin and Hermod stay separate servers | a chat client connects Munnin alone; a coding client connects Munnin + Hermod | "there's a reason why I separated munnin and hermod: modular … for chat agent (like claude desktop / chatgpt) I still can connect it using pure munnin" | Settled |
| 8 | This plan's content scope | `agent-memory-project` only, for now | "for now, let's purely setup for agent-memory-project for the hermod server" | Settled |
| 9 | The spec to mirror | the Munnin server (`agent-memory-server`) | "we can use similar spec to the munnin server" | Settled |
| 10 | Server boundary rule | a boundary is earned by a store, auth or blast radius; capability repos are content | proposed by me, moved past with no objection | My call |

- **Considered and rejected**:
  - **Four separate hermod MCP servers**, one per hermod repo → lost: "I don't see the benefit of it being separated mcp".
  - **A domain server now** (Balder as its own server immediately) → deferred, not rejected: it is the pattern for when a domain earns a server.
  - **`hermod-project-server` as the middle layer's name** → dropped: it puts a codename on a public repo, which no existing public repo does; `hermod-server` sidesteps the question.
  - **Bundling the core into hermod-server** (pinning `agent-memory-system` as a second content submodule) → lost: the client already connects Munnin, so it would duplicate content and breach the core's invariant guard.
  - **Extracting the shared tooling (a shared `seam.py` package) inside this plan** → deferred to the Asgard monorepo work; this plan mirrors the Munnin spec, which vendors what it needs.

- **Left open**:
  - The hermod deploy repo's name (`hermod-project-deploy` and `hermod-project` were both written).
  - Whether hermod-server is local-only (my argument: the overlay reads the working repo, so it is per-machine) or hosted like Munnin.
  - Whether the Asgard move renames the public family to the codenames, or keeps the functional names with the codename only on private deploy repos.
  - The overlay's project store timing (ADR-023 defers the `db` backend).

---

## **OBJECTIVES**
Two deliverables, in this order:

1. **Trim the overlay.** Extract the artifact-generation family out of `agent-memory-project` into a new repo, so the surface the overlay owns is the shell, project memory and push/pull.
2. **Build `hermod-server`.** A second MCP server that serves that trimmed overlay to a client, on the Munnin spec: same composition pipeline, same local-mode shape, no store of its own outside the project store it is given.

### **Related Documents**
- [Munnin server README](C:/Work/IM/munnin-deploy/agent-memory-server/README.md) - the spec this mirrors (five-minute run, local mode, hosting)
- [Munnin architecture](C:/Work/IM/munnin-deploy/agent-memory-server/docs/README.md) - the tool and endpoint surface, the data model, known debts
- [Munnin loader](C:/Work/IM/munnin-deploy/agent-memory-server/src/munnin/content/loader.py) - the composition pipeline hermod reimplements over a different content root
- [Munnin seam bridge](C:/Work/IM/munnin-deploy/agent-memory-server/src/munnin/content/seam_bridge.py) - how a server imports the framework's own compile modules by path
- [storage-backends README](C:/Work/IM/agent-memory-project/storage-backends/README.md) - the overlay's seam, markdown live and db declared
- [db.md](C:/Work/IM/agent-memory-project/storage-backends/db.md) - the per-op checklist the project store implements
- ADR-016 (wrap-up persistence and `§ persist-store`), ADR-023 (the overlay storage seam), ADR-020/021/022 (the three family splits this extraction follows), ADR-004 (docs placement, which the extracted family owns)

### **SUCCESS CRITERIA**
- [ ] `agent-memory-project` holds 9 procedures; `agent-memory-doc` holds the 6 extracted procedures with `compute-doc-placement`, `present-doc-for-review` and 6 templates; `dockerize` lives in `agent-memory-wizards`
- [ ] Every installer, manifest, README, MIGRATION and test across the three repos is consistent, and the overlay's installed command set is rebuilt and verified
- [ ] `map-orientation`'s 4 producer clauses and `orientation-map-template`'s 3 are gone, and the map still discovers and classifies the same artifacts
- [ ] `hermod-server` runs locally: a client connects over `/mcp`, `read_procedure("awaken-coder")` returns the composed procedure, both remaining templates read as resources, and `/health` answers
- [ ] `push-all`, `pull-all`, `dockerize` and the 6 doc procedures are absent from the served prompt list
- [ ] `project-wrap-up` Step 4 resolves to `/push-all` on markdown and `/push-project` on the db
- [ ] A project context entry round-trips through `hermod-server`'s tools against the project store
- [ ] Fidelity: for a sample of served prompts, hermod's composition matches the overlay compiler by mechanic accounting (ops referenced and backend section substituted), not by byte-identity
- [ ] The registry is source-list-shaped, so adding a Munnin proxy later is one provider plus config
- [ ] Records updated: the three repos' README/MIGRATION/NOTICE; the core's README and ARCHITECTURE prose; the store's orientation map and a new context entry; one ADR for the extraction and the server boundary

---

## **SCOPE**

### In Scope
- Extract `generate-readme`, `generate-docs`, `generate-architecture-docs`, `generate-domain-docs`, `generate-flow-docs` and `discovery-contract`, together with `components/compute-doc-placement.md`, `components/present-doc-for-review.md` and 6 templates, into a new repo `agent-memory-doc` (`hermod-doc`): its own copy-and-adapted compile and install tooling, placeholder, manifest, README, MIGRATION, NOTICE, tests and CI
- Move `dockerize` into `agent-memory-wizards`, with a note recording the boundary it crosses against ADR-021
- Drop the 4 producer clauses in `map-orientation.md` (L95-97, L285) and the 3 in `orientation-map-template.md` (L31-33)
- Update `agent-memory-project`: README, MIGRATION, installer, tests
- New repo `hermod-server`: Munnin's shape minus its HTTP face. FastMCP mounted at `/mcp` on a Starlette app carrying one `/health` route; local mode only; the content root pinned as a submodule with an env override; a loader reading the overlay live; the seam imported by path; hermod's own inliner and discovery; a registry shaped as a source list
- The project store: implement `storage-backends/db.md`'s ops for the 4 seamed procedures, with its schema, migrations and repository, and compose served prompts onto `db.md` rather than `markdown.md`
- Give `project-wrap-up` a `## Storage Mechanics` section with `§ persist-store`, defined in both backends
- The served-procedure exclusion list, defined and visible: `push-all`, `pull-all`, `dockerize`, the 6 doc procedures
- Records: the core's README and ARCHITECTURE prose; the store's orientation map and a new context entry; one ADR

### Out of Scope
- **No join to Munnin** (decision 4). No httpx client, no `ProxyProvider`, no Munnin credential. The registry is shaped so the migration is one provider plus config, and that migration is recorded rather than built
- **No deployment.** No deploy repo, no hosting, no TLS, no token mode. Local mode only
- **No Asgard folder yet** (decision 3)
- **No serving of the sibling repos.** `hermod-server` serves `agent-memory-project` alone, not `hermod-doc`, `hermod-local`, `hermod-fleet` or `hermod-wizards`
- **No FastAPI, no `/api`, no anonymous pages** (decision 5)
- **No bundling of the core** as a second content source: the client connects Munnin for that
- **No change to the store's markdown twins** beyond the recorded one-way import (decision 15)
- **No content change to the moved procedures** beyond what the move itself requires

---

## **CONFIRMED DECISIONS**
*Decisions made **by this plan** — both **asked-and-confirmed** by [USER-NAME] AND **written-through** (Zone A and B decisions made by the agent, recorded with their reasoning). The reasons serve as the analysis record.*
*Decisions settled before this plan existed — by a parent, or in a pre-planning discussion — belong in [INHERITED CONTEXT](#inherited-context) above, not here. Keeping them separate is what shows which decisions this plan actually owns.*

| # | Decision | Chosen | Reason |
|---|----------|--------|--------|
| 1 | This plan's deliverables | Two: the artifact-generation extraction, then `hermod-server` | "for now, let's purely setup for agent-memory-project for the hermod server"; decision 12 folded the extraction into the same plan |
| 2 | The project store | In scope: implement `db.md` and give hermod-server the project store | "2. B, in fact maybe we should do this first" |
| 3 | Asgard's folder | Created after this plan | "3. A" |
| 4 | The join to Munnin | None in this plan; the registry is built source-list-shaped so a proxy is a later addition | FastMCP 3.4.6 ships `ProxyProvider` and `create_proxy`, so migrating A to C is one `add_provider` plus config, which means starting simple spends no option |
| 5 | hermod's inbound HTTP face | MCP face on FastMCP's Starlette app plus one `/health` route. No FastAPI, no `/api`, no pages | "I haven't found any extending usage for hermod. C should be fine, except that we still need /health" |
| 6 | Build order | Content first, then the store | working-product-first; the store's shape is already pinned by `db.md`'s op list, so it does not need to land first to be safe |
| 7 | The compile logic hermod consumes | Split: import the overlay's `seam.py` by path, carry hermod's own inliner and discovery, guard the copy with a fidelity test | the two `seam.py` files are byte-identical but for the overlay's own header, which asks for one home; the inliner is `inline_components()` inside a CLI script, not a module; the fidelity test turns a copy into a caught divergence instead of a silent drift |
| 8 | Served-procedure exclusions | `push-all`, `pull-all`, `dockerize`, and the 6 doc procedures | "we don't need pull-all and push-all for hermod-server. only push project and pull-project"; the other 7 leave the repo entirely |
| 9 | `project-wrap-up` Step 4 | Becomes a `§ persist-store` seam op: markdown resolves to `/push-all`, db resolves to `/push-project` | `push-all` is unserved, so the composite reaches it through an op; under the db the resolution is a real project push for a localized project, so the completion gate stays honest |
| 10 | `dockerize`'s destination | `agent-memory-wizards` | "dockerize -> move to wizard" |
| 11 | The doc family's destination | New repo `agent-memory-doc`, codename `hermod-doc` | "create new repo called agent-memory-documentation (or agent-memory-doc?)", then "let's just use -doc, it's easier" |
| 12 | Where the extraction is planned | Folded into this plan, phased extraction-first (decision 3 → B) | "3. B" |
| 13 | `map-orientation` | Stays in `hermod-project`; its 4 producer clauses and the template's 3 are dropped | "keep as is in hermod-project", then "let's remove the references to that generator docs then"; the mechanism, the recognizer, the `HOME` wiring and the seam ops are untouched, and only the provenance is dropped |
| 14 | The content root | Pinned as a submodule, with an env override | mirrors Munnin, whose five-minute clone and deploy story depend on it |
| 15 | Backend composition | Served prompts compose onto `db.md`, not `markdown.md` | a served client has no local store, and Munnin likewise always composes onto its own db backend |
| 16 | The store's import model | One-way from the markdown files; DB authoritative, markdown frozen as history | mirrors Munnin's importer and the 2026-10-08 decision to keep the DB authoritative rather than importing |
| 17 | `hermod-doc`'s read of the orientation map | **No read at all.** The generators list documented-vs-not from disk, and the map indexes docs on its own scan | "the map is the one who should be actively list docs, not the other way around" — supersedes this row's original "by file, with no access declaration", which was written before the ownership split was known |

---

## **SOLUTION**

### Architecture Overview

**Part 1, the extraction.** `agent-memory-doc` is created as a sibling overlay holding the artifact-generation family: 6 procedures, 2 components and 6 templates. Its tooling is a copy-and-adapted compiler with **no seam stage**, which is the shape the wizards, fleet and local copies already have and the reason none of them carries a `seam.py`. `dockerize` moves to `agent-memory-wizards`. `agent-memory-project` keeps 9 procedures, 3 components and 2 templates, and gains a `map-orientation` whose producer clauses are gone.

**Part 2, the server.** `hermod-server` is Munnin's composition root minus its HTTP face and minus the memory store. One ASGI app carries FastMCP mounted at `/mcp` plus a single `/health` route. A `ContentLoader` reads the `agent-memory-project` submodule live and composes each served procedure the way the overlay's own compiler does: component references inlined, then the `## Storage Mechanics` section swapped for the `db` backend's ops. Two definitions are imported rather than copied (the seam, loaded by path) and two are carried (the inliner and the glob discovery), with a fidelity test holding the carried pair honest. The registry is a **source list**, so a Munnin proxy is one `add_provider` later. Beside it sits the project store the overlay's `db` backend has been declaring since ADR-023.

### Component 1: hermod-doc (new repo)
- **Purpose**: give the artifact-generation family its own home, so the overlay's surface is the shell, project memory and push/pull
- **Key Files**: `procedures/{discovery-contract,generate-readme,generate-docs,generate-architecture-docs,generate-domain-docs,generate-flow-docs}.md`; `components/{compute-doc-placement,present-doc-for-review}.md`; `templates/{readme,architecture-doc,domain-doc,flow-doc,domain-context-map,flow-journey-map}-template.md`; `setup-scripts/{compile-procedures,install-skills}.py`; `README.md`; `MIGRATION.md`; `NOTICE`; `tests/`; `.github/`; `docs/adr/`

### Component 2: hermod-wizards (gaining dockerize)
- **Purpose**: take `dockerize`, so the overlay holds no artifact emitter
- **Key Files**: `procedures/dockerize.md`, `README.md`, `MIGRATION.md`, `setup-scripts/install-skills.py`, `tests/`, `docs/adr/`

### Component 3: agent-memory-project (trimmed)
- **Purpose**: lose the family, keep the shell plus project memory plus push/pull
- **Key Files**: `procedures/map-orientation.md` (L95-97 and L285 trimmed), `templates/orientation-map-template.md` (L31-33 trimmed), `procedures/project-wrap-up.md` (gains a `## Storage Mechanics` section), `storage-backends/{markdown,db}.md` (gain `§ persist-store`), `README.md`, `MIGRATION.md`, `setup-scripts/install-skills.py`, `tests/`

### Component 4: hermod-server, the content pipeline
- **Purpose**: turn a procedure source into a self-contained served Prompt, identically to the overlay's compiler
- **Key Files**: `src/hermod/content/{loader.py,seam_bridge.py,inline.py}`, `tests/test_loader.py`, `tests/test_fidelity.py`

### Component 5: hermod-server, the app and its faces
- **Purpose**: one ASGI app carrying the MCP face and `/health`
- **Key Files**: `src/hermod/{app.py,__main__.py}`, `src/hermod/api_mcp/server.py`, `src/hermod/configuration/config.py`, `tests/test_app.py`, `tests/test_twin_parity.py`

### Component 6: hermod-server, the project store
- **Purpose**: own the project-keyed memory the overlay's `db` backend has been deferring since ADR-023
- **Key Files**: `src/hermod/data_entities/{project_context.py,migrations/}`, `src/hermod/data_repositories/project_repository.py`, `src/hermod/business_services/context_service.py`, `tests/test_store.py`

<!-- OPTIONAL SECTION A: Include when multi-system changes, multiple components interacting -->
### Integration Architecture

| Component | Integrates With | Data Flow | Dependencies |
|-----------|----------------|-----------|--------------|
| `hermod-doc` | `hermod-project` at extraction time only | 14 files move out; afterwards the two repos do not reference each other | both keep a one-way dependency on the core; no runtime link |
| `hermod-wizards` | `hermod-project` at extraction time only | `dockerize.md` moves in, and the wizards manifest and tests gain it | a note against ADR-021, whose boundary shifts |
| `hermod-project` | the core (one-way), the project store | 7 procedures leave; `map-orientation`'s provenance is trimmed; `project-wrap-up` gains a store op | the core invariant guard stays green |
| `hermod-server` content pipeline | the `agent-memory-project` submodule, read live | procedure source + components + `db.md` → composed Prompt; templates → Resources | the seam is imported by path; the inliner and discovery are carried |
| `hermod-server` faces | the client | client → `/mcp` (prompts, resources, tools), and `/health` | FastMCP plus Starlette; no FastAPI |
| `hermod-server` project store | `db.md`'s ops, and `hermod-doc`'s discovery read | context entries and the orientation map in, records out | markdown imports one-way; the map stays a file `hermod-doc` can read |
| the client | `hermod-server` and Munnin | prompts and resources from hermod, memory from Munnin | two connectors until decision 4 is revisited |

### Cross-System Contract Impact (Blast-Radius Check)

*The change that crosses a boundary is the project store: project-keyed memory moves from markdown files under `[AGENT-MEMORY-PATH]` to store records. The markdown backend stays the default for installed users, so the new shape is additive until a project opts into the served form.*

**Change classification** (check all that apply): ☑ string/ID format (entry scope) ☑ enum value added/changed (the `doc_type` vocabulary loses its producer clauses) ☑ new/removed field (store records)

| # | Consumer (system + path) | How it couples (deserialize / string-parse / DB-read / migrate / display) | Breaks how on this change? | Verified / mitigated |
|---|---|---|---|---|
| 1 | `agent-memory-project` → `map-orientation.md` | string-parse: reads `MAP_PATH` and per-entry `status` | none: the path, format and recognizer are untouched, only the producer clauses leave | a fixture test asserts discovery and classification are unchanged |
| 2 | `agent-memory-doc` → `discovery-contract.md` | file-read: reads the map for per-entry status | none: it reads by path, and decision 17 keeps that a file read | the same fixture exercises it |
| 3 | `agent-memory-project` → `update`/`load-project-context.md` | file read/write on the markdown backend | none: markdown stays live | the existing suite covers it |
| 4 | `hermod-server` → `db.md` | seam op resolution | nothing consumes it today | the ops are written in this plan and tested against the store |
| 5 | installed commands, all three repos | string-parse: the installer's enumerated procedure names | **breaks** if an installer still claims a moved procedure | each repo's installer set is recompiled and asserted against its `procedures/` directory |

- **Deploy ordering**: the extraction lands first (Phase 1), then the server reads the trimmed tree, so no producer ships ahead of its consumer
- **Existing data**: nothing is mixed-format; the store is new, and the markdown files import one-way (decision 16)
- **Project registry**: none exists for this project

### Technical Considerations

- **The seam is a file, not a package.** `storage-backends/seam.py` has no importable module path, so hermod loads it by path with `importlib.util.spec_from_file_location` and caches it, exactly as Munnin's `seam_bridge` does. Its own header asks that a change land in both copies, and the core's verification depends on that.
- **The inliner is carried, and only a test holds it.** `inline_components()` and `component_body()` live inside `setup-scripts/compile-procedures.py`. Two of their rules are load-bearing: a component body is everything after the component's first standalone `---` rule, and only component links are de-linked, so an in-document anchor survives. The fidelity test is what makes the copy safe rather than a drift.
- **Discovery differs between the two servers.** Munnin reads `procedures/command_set.py`; the overlay's rule is a bare `sorted(procedures/*.md)` glob. So hermod's discovery is its own three lines and there is nothing to import.
- **`db.md` is a checklist, not mechanics.** It names each op and what it must do, and deliberately carries no schema, so the store's schema is this plan's work rather than a transcription.
- **One op cannot be answered by the project store.** `§ select-project-episode` returns the newest episode whose project is in the resolved set, and episodes are Munnin's records. Under decision 4 its db mechanic is a delegation: the memory layer answers it and the agent reads it there. This is the visible cost of no-join, and the strongest single argument for revisiting it.
- **The exclusion list is the server's only say over the framework.** `push-all` and `pull-all` are excluded because the memory write is durable on every insert; `dockerize` and the 6 doc procedures are absent because they left the repo. The list stays a named constant so a future exclusion is a visible one-liner.
- **Local mode only.** There is no issuer and no token path at all, so the app carries no auth middleware and the config has no issuer fields. Adding hosted mode later means porting Munnin's `build_auth` and its loopback guards rather than inventing them.
- **`project-wrap-up` gains a seam section it does not have today.** Its Step 4 was the only remaining call to an unserved procedure, so it becomes an op resolving to `/push-all` on markdown and `/push-project` on the db, which keeps the installed form's memory push and keeps the served form's reference resolvable.

### Solution Options & Evaluation

#### Solution Options

The plan's forks, with the losing option recorded beside the winner.

| # | Option | Fork | Description |
|---|--------|------|-------------|
| 1 | No join, registry source-list-shaped | Hermod ↔ Munnin | each server serves its own layer and the client connects both |
| 2 | Static fetch from Munnin | " | hermod pulls Munnin's prompts and resources over `/api` and re-serves them |
| 3 | Full proxy now | " | hermod mirrors Munnin's whole surface through `ProxyProvider` |
| 4 | Import the seam, carry the inliner | the compile logic | one definition imported, two carried, guarded by a fidelity test |
| 5 | Import the CLI script wholesale | " | hermod calls `inline_components()` out of `compile-procedures.py` |
| 6 | Copy everything | " | a third copy of the byte-identical seam |
| 7 | Content first | build order | a client can read a procedure before any store exists |
| 8 | Store first | " | the store lands while attention is fresh |

#### Evaluation

| Solution | Pros | Cons |
|----------|------|------|
| No join (#1) | no credential, no availability coupling, boots without Munnin, and the move to #3 is one `add_provider` | the coding client keeps two connectors |
| Static fetch (#2) | one source of truth for shared content | needs a Munnin token and degrades whenever Munnin is down, and today it would fetch exactly one thing, which Munnin does not hold |
| Full proxy (#3) | one connector for coding | puts a memory credential inside a repo-touching process, and the arguments the agent must supply stay the agent's either way |
| Import the seam, carry the inliner (#4) | one home for the byte-identical file, no third copy, and the carried pair is covered by a test | the inliner exists in two places, and only the test holds them together |
| Content first (#7) | a working product early, and the store's shape is already pinned by `db.md`'s op list | the store then lands against a surface already in place |

#### Selected Approach
- **Chosen**: options 1, 4 and 7 together, which are decisions 4, 7 and 6
- **Rationale**: the join is the only fork with a real product consequence, one connector against two, and FastMCP makes the migration cheap enough that deferring it spends nothing, so the credential and the coupling are not paid until a client needs them. The compile logic splits on evidence rather than taste: the two `seam.py` files differ by a header whose own text asks for one home, so the seam is imported, while the inliner is a function inside a CLI script and is therefore carried, with a fidelity test rather than a promise holding it. Content first follows the project's working-product principle, and it is safe because `db.md` already fixes the store's op list.

### ADR Output

- **ADR File**: [agent-memory-project/docs/adr/2026-10-12-hermod-doc-extraction-and-hermod-server.md](C:/Work/IM/agent-memory-project/docs/adr/2026-10-12-hermod-doc-extraction-and-hermod-server.md)
- **Decision Summary**: The artifact-generation family leaves the coding overlay for its own repo, and the remaining overlay gains a served form through `hermod-server`, which mirrors the Munnin server's composition without its HTTP face and owns the project store ADR-023 deferred.

---

## **IMPLEMENTATION PHASES**

### Phase 1: Extract the artifact-generation family

- [ ] **Step 1.1**: Create `agent-memory-doc` and move the 14 assets in
  - **Action**: create the repo, move 6 procedures, 2 components and 6 templates, and rewrite their references
  - **Implementation**: `git mv` the 14 files; inside the moved procedures replace `[path-to-agent-memory-project]` with `[path-to-agent-memory-doc]` and repoint every component and template reference; in `discovery-contract.md` reword the two map references (L53, L54) to name the resolved map path rather than `/map-orientation`'s Prelude, so `hermod-doc` names no procedure living in another repo; leave the rest of each file's text unchanged
  - **Testing**: `grep -r "path-to-agent-memory-project"` over the new repo returns nothing, and the adapted compiler reports 6 procedures clean under `--strict`
  - **Success Criteria**: the 14 files live in `agent-memory-doc`, compile clean, and no longer exist in `agent-memory-project`

- [ ] **Step 1.2**: Give `agent-memory-doc` its own tooling
  - **Action**: copy-and-adapt the compile and install tooling, with **no seam stage**
  - **Implementation**: copy `compile-procedures.py` and drop the seam import, the module-level `_load_seam()` call and the seam stage, exactly as the wizards, fleet and local copies have none; ship no `seam.py`; set the prefix `agent-doc-`, the placeholder `[path-to-agent-memory-doc]` and the manifest name; add `README.md`, `MIGRATION.md`, `NOTICE`, `LICENSE`, `pyproject.toml`, `tests/` and CI
  - **Testing**: the compiler's output matches a spot-checked sample; the installer installs 6 procedures and uninstalls cleanly leaving sibling manifests intact; the suite is green
  - **Success Criteria**: `agent-memory-doc` installs and uninstalls itself, compiles clean under `--strict`, and carries no `seam.py`

- [ ] **Step 1.3**: Move `dockerize` into `agent-memory-wizards`
  - **Action**: move the procedure and update the wizards' bookkeeping
  - **Implementation**: `git mv dockerize.md` into the wizards; update its `README.md`, `MIGRATION.md`, installer and tests; add an ADR note recording that the boundary ADR-021 drew has shifted
  - **Testing**: the wizards compile and install with the extra procedure; a reference check finds no `dockerize` mention left in `agent-memory-project` outside history
  - **Success Criteria**: `dockerize` installs from the wizards and is gone from the overlay

- [ ] **Step 1.4**: Trim `map-orientation` and the overlay's own files
  - **Action**: drop the 7 producer clauses and update the overlay's bookkeeping
  - **Implementation**: in `map-orientation.md` remove the producer parentheticals at L95-97 and the `/discovery-contract` entry at L285; in `orientation-map-template.md` remove the "from `/generate-…`" clauses at L31-33; update `README.md`, `MIGRATION.md`, the installer's enumerated names and `tests/` to the 9 remaining procedures
  - **Testing**: a fixture test asserts the map still discovers the same artifacts and classifies them to the same types; `--strict` compiles 9 procedures clean; the installer's installed set equals `procedures/*.md`
  - **Success Criteria**: the mechanism, the recognizer, the `MAP_PATH` wiring and the 5 seam ops are untouched; no dangling `/generate-…` or `/discovery-contract` reference remains in the overlay, and no `/map-orientation` reference remains in `hermod-doc`; the installer set matches

- [ ] **Step 1.5**: Verify the three repos together
  - **Action**: run every suite, the invariant guard, and a cross-reference sweep
  - **Implementation**: run each repo's suite and `--strict` compile; run the core's `check-core-invariant.sh`; grep all three repos for references to the moved procedures
  - **Testing**: three green suites and a green guard; the sweep returns nothing outside `docs/adr/` and `MIGRATION.md`
  - **Success Criteria**: nothing live references a procedure that moved

### Phase 2: hermod-server, the content pipeline

- [ ] **Step 2.1**: Scaffold the repo
  - **Action**: create `hermod-server` with its config, submodule pin and CI
  - **Implementation**: `pyproject.toml` (fastmcp, uvicorn, starlette; dev pytest, ruff, httpx); add `agent-memory-project` as a submodule; `src/hermod/configuration/config.py` with `HERMOD_*` env vars and **no issuer fields**; `README.md`, `NOTICE`, `LICENSE`, `.env.example`, `.gitignore`, CI
  - **Testing**: `uv sync` succeeds; `git clone --recurse-submodules` populates the content root
  - **Success Criteria**: the repo installs and a placeholder module imports

- [ ] **Step 2.2**: The seam bridge and the inliner
  - **Action**: import the seam by path; carry the inliner
  - **Implementation**: `content/seam_bridge.py` loads `storage-backends/seam.py` from the content root by `spec_from_file_location`, cached by path; `content/inline.py` carries `inline_components()`, `component_body()`, `_lines()` and `_emit()` from the overlay's compiler with a header recording the copy and naming the fidelity test as its guarantee
  - **Testing**: unit tests cover the first-`---` body rule and the de-link rule; a test asserts the bridge raises `FileNotFoundError` when the submodule is absent
  - **Success Criteria**: both modules import, and the two load-bearing inliner rules are covered

- [ ] **Step 2.3**: The loader
  - **Action**: discover, compose and list
  - **Implementation**: `content/loader.py` with discovery by `sorted(procedures/*.md)` minus an exclusion constant holding `push-all` and `pull-all` (the 7 that left need no entry, being absent from the tree); the registry expressed as a **source list** holding one source; the backend document taken as configuration, defaulting to `markdown.md` until Phase 4.3 flips it to `db.md`; `get_prompt` inlines then substitutes the `## Storage Mechanics` section from that backend; `list_resources`/`get_resource` over `templates/`; titles from each document's own `#` heading and descriptions from its lead sentence, as Munnin derives them
  - **Testing**: `list_prompts()` equals the 9 minus the exclusions; `get_prompt("awaken-coder")` carries no unresolved component reference; `list_resources()` returns 2
  - **Success Criteria**: the loader serves the trimmed overlay, and an unknown prompt name raises rather than returning nothing

- [ ] **Step 2.4**: The fidelity test
  - **Action**: hold the carried inliner honest against the overlay's compiler
  - **Implementation**: a test that runs the overlay's own `compile_one()` over a sample of procedures and hermod's composition over the same ones, then compares **mechanic accounting**: the components inlined, the ops referenced, and the backend section substituted. Not byte-identity, because the two compose different backends
  - **Testing**: the test fails when a component reference is deliberately broken, proving it can fail in the direction that matters
  - **Success Criteria**: a change to the overlay's inlining that hermod does not follow turns the test red

### Phase 3: hermod-server, the app and its faces

- [ ] **Step 3.1**: Register the served surface
  - **Action**: prompts, resources and the read tools
  - **Implementation**: `api_mcp/server.py` registering each served procedure as a FastMCP Prompt with a derived title, a derived description and its optional argument slot; each template as a Resource; and the tools an agent may invoke itself, being `read_procedure`, `read_resource`, `list_procedures`, `list_resources`, `ping` and `help`
  - **Testing**: a client lists 9 prompts and 2 resources with titles and descriptions that differ from each other; `read_procedure` round-trips
  - **Success Criteria**: nothing unserved appears in the handshake, and the exclusion list is the only filter

- [ ] **Step 3.2**: Compose the app
  - **Action**: one ASGI app carrying the MCP face and `/health`
  - **Implementation**: `app.py` builds FastMCP with the loader injected, calls `http_app()`, mounts it at `/mcp` on a Starlette app that takes the MCP app's lifespan and adds a `/health` route returning the service name and version
  - **Testing**: `/health` answers 200; `/mcp` answers an MCP handshake; the app starts with no issuer configured
  - **Success Criteria**: one process serves both, and the MCP session manager starts (the lifespan is wired)

- [ ] **Step 3.3**: Boot and connect
  - **Action**: run the server locally and drive it from a real client
  - **Implementation**: start the process; connect with `claude mcp add --transport http hermod http://127.0.0.1:<port>/mcp` or a `.mcp.json` entry; exercise `ping`, `list_procedures`, `read_procedure("awaken-coder")` and a `read_resource`
  - **Testing**: a twin-parity test asserts a served prompt's mechanics equal the compiled command's, allowing for the backend difference; a smoke test exercises both faces
  - **Success Criteria**: a real client answers `pong`, lists 9 procedures and reads a composed prompt

### Phase 4: the project store

- [ ] **Step 4.1**: Schema, migrations and repository
  - **Action**: create the store the `db` backend's ops need
  - **Implementation**: a `project_context` table keyed by project with a scope column for shared and private, an `orientation_map` table keyed by project, and a migration runner; a `ProjectRepository` behind a Protocol, as Munnin's `MemoryRepository` is, so a second backend is a later addition rather than a rewrite
  - **Testing**: migrations apply to a fresh database and are idempotent on re-run; the repository round-trips an entry and a map
  - **Success Criteria**: a fresh database reaches the schema in one call, and a re-run changes nothing

- [ ] **Step 4.2**: The context service and the store's tools
  - **Action**: expose the store through the service layer and its tools
  - **Implementation**: a `ContextService` covering the op set `db.md` names (list, read, create, update, move, delete, check-size) and the map ops (exists, read, write, create); register the tools the served procedures call
  - **Testing**: each op has a test; `§ move-context-entry` changes a scope without touching the body; an oversized entry is refused by `check-entry-size`
  - **Success Criteria**: every op `db.md` lists outside the seam has an implementation and a test

- [ ] **Step 4.3**: Write `db.md`'s mechanics and compose onto it
  - **Action**: turn the checklist into mechanics, and serve from it
  - **Implementation**: fill each op in `storage-backends/db.md`; give `project-wrap-up` a `## Storage Mechanics` section whose `§ persist-store` resolves to `/push-all` in `markdown.md` and `/push-project` in `db.md`; add `§ select-project-episode`'s db mechanic as a delegation to the memory layer, since episodes are Munnin's records; switch the loader's backend from `markdown.md` to `db.md`
  - **Testing**: every op a served procedure references resolves, asserted by the loader's own unresolved-op check; the served `project-wrap-up` names `/push-project`; the served `awaken-coder` delegates the episode step
  - **Success Criteria**: no served prompt carries an unresolved op, and the three consequence lines above hold in the composed text

- [ ] **Step 4.4**: Round-trip and fidelity re-run
  - **Action**: prove the store and re-prove the copy
  - **Implementation**: exercise `update-project-context` and `load-project-context` end to end against the store; re-run the fidelity test with the db backend composed
  - **Testing**: an entry written through one procedure reads back through the other, with its scope intact; the fidelity test stays green under the new backend
  - **Success Criteria**: a project context entry round-trips through the server's tools

### Phase 5: Records

- [ ] **Step 5.1**: Finalize the ADR
  - **Action**: reconcile the ADR authored alongside this plan with what actually shipped
  - **Implementation**: read `docs/adr/2026-10-12-hermod-doc-extraction-and-hermod-server.md`; correct any requirement, success criterion or rejected alternative that implementation changed; keep its link to this plan resolving
  - **Testing**: every rejected alternative in the ADR still matches section F, and the ADR's link resolves
  - **Success Criteria**: the ADR describes the system as built rather than as planned, and matches the decisions recorded here

- [ ] **Step 5.2**: The cross-repo prose and the store's entries
  - **Action**: bring every description of the boundary up to date
  - **Implementation**: update the core's `README.md` and `ARCHITECTURE.md`; update the three repos' `README.md`/`MIGRATION.md`/`NOTICE`; refresh the store's orientation map and add a project context entry recording the new family member and the served form
  - **Testing**: the store's map lists the new sibling repo; a grep for the old family description returns nothing outside history
  - **Success Criteria**: no document still describes the overlay as owning the doc family


---

## **EXECUTION LOG**
**Execution Protocol for AI**:
I have to use this document as my **ONLY** source of truth to execute and track the plan steps iteratively. I should **NOT** use additional tools like ToDos because it lacks the context of what should I do. Everytime I want to implement a step I have to check the reference to the original step plan above. Everytime a step has been finished I need to go back to this document to log what was done.
*In other words*:
- I have to make this document as the source of truth for the implementation phase on what I have worked on and what I will be working
- The original plan must be fully in my context, therefore, I have to make sure I loaded the **Plan File** before executing any task and read carefully the reference to the original step
- I have to do the implementation by doing it in order per step THEN, I ALWAYS have to fill the step log rightly after

**Definition of Done (applies to ALL steps)**:
- ✅ **Code Quality**: Code compiles/runs without errors
- ✅ **Testing**: Tests written and passing
- ✅ **Logged**: Implementation and testing logged below
- 🚫 **Blocked**: Get input from [USER-NAME] before assuming

### Phase 1:
- [x] **Step 1.1**: Create `agent-memory-doc` and move the 14 assets in
  - **Implementation Log**: Created `C:\Work\IM\agent-memory-doc` with `procedures/`, `components/` and `templates/`, and moved the 14 files out of the overlay with `Move-Item` (a cross-repo move cannot use `git mv`, whose destination must sit inside the same repo). Swapped 12 occurrences of `[path-to-agent-memory-project]` for `[path-to-agent-memory-doc]`. Then, per decision 17 as revised, removed **every** orientation-map reference from the repo: `discovery-contract`'s status-join section plus its header line, inventory example, stale-flag bullet and integration entry; the 5 generators' status-join items, integration bullets, two-altitude clauses and anti-patterns; `generate-docs`' `MAP_PATH` preflight, Step 4 heading, report line and anti-pattern; and 6 lines across 4 templates. Every numbered list punched by a deletion was renumbered.
  - **Testing Log**: Reference check: 6 procedures, 2 components, 6 templates, **0 unresolved** component or template references. Repo-wide greps: `path-to-agent-memory-project` = 0, and `/map-orientation|MAP_PATH|orientation map` = **0**. Numbering-gap scan across every `.md`: **0 gaps**. The compiler carries no `--strict` run yet (Step 1.2 brings it). A first pass of the removal over-deleted four clarifications (both "two altitudes" notes, one frontmatter instruction, one anti-pattern); all four were recovered from the overlay's `HEAD` and re-inserted, reworded to name the altitude rather than the map.
  - **Success Criteria**: PASS on the file and reference halves; the `--strict` compile half is deferred to Step 1.2, which is what brings the compiler.
  - **Tech Debts**: None.
  - **Result**: PASS. Note the plan's step text said "reword the two map references (L53, L54)"; the repo carried 24 references in total, so Step 1.4's repo-wide criterion is the one that was applied, and decision 17 now records the change from *reword* to *remove*.

- [x] **Step 1.2**: Give `agent-memory-doc` its own tooling
  - **Implementation Log**: Copied the 6 tooling files into `setup-scripts/` (`compile-procedures.py`, `install-skills.py`, `setup-all-opencode.py` + `.bat`, `uninstall-opencode.py` + `.bat`). Base = the **wizards'** copy, chosen on evidence: a line diff against the overlay's compiler shows every non-seam difference is a docstring line or the unwrapped `Report.clean`, so the wizards' copy *is* the overlay's minus the seam stage. Re-identified it: prefix `agent-doc-`, manifest `.agent-memory-doc-opencode-manifest`, placeholder `[path-to-agent-memory-doc]`, prose, and its **own** marker UUIDs (`3fa71dac-…` path, `682b2148-…` environment) because the copies carried the wizards'. Packaging added: `.gitattributes`, `.gitignore` and `LICENSE` verbatim, plus `pyproject.toml` (`package = false`), `NOTICE`, `README.md`, `MIGRATION.md`, `uv.lock` (root name adapted), `tests/` (4 files, re-identified) and `.github/workflows/ci.yml`. Registered `.agent-memory-doc-opencode-manifest` in the four sibling layers' installers, uninstallers and the project's migration script, and updated the wizards' sibling assertion. `git init -b main`, initial commit `d465a3d`.
  - **Testing Log**: `pytest -q` → **34 passed**; `ruff check` → clean; `compile-procedures.py --strict` → 6 procedures, exit 0 (this also discharges Step 1.1's deferred check); `uv lock --check` → resolves; no `seam.py` present. Installer cycle against a scratch skills dir: install → 6 skills, re-install idempotent, removal leaves a sibling-claimed folder intact. Sibling suites: wizards **34 passed**, fleet **41 passed**, local **39 passed**. Project shows 1 failure, which belongs to Step 1.4: its skill-set test still expects the 7 procedures that moved.
  - **Success Criteria**: PASS. Installs and uninstalls itself, compiles clean under `--strict`, and carries no `seam.py`.
  - **Tech Debts**: (1) `AGENT_MEMORY_TARGET_DIR` redirects the skills directory but **not** the instructions file, so a scratch-target install still edits the live `AGENTS.md`; the registration made while testing was **reverted**. (2) The uninstaller's `_OWN_MARKERS` lists only the path UUID, mirroring the wizards'. (3) Pre-existing and **not** fixed: the fleet installer's sibling list omits the wizards, the project installer's omits local, and the wizards' own `setup-all-opencode.bat` sits LF on disk despite the `eol=crlf` rule. (4) No GitHub remote exists; creating and pushing it is [USER-NAME]'s call at the push step.
  - **Result**: PASS.

- [x] **Step 1.3**: Move `dockerize` into `agent-memory-wizards`
  - **Implementation Log**: Moved `procedures/dockerize.md` (343 lines) from the overlay into the wizards. It carried no placeholder, component or template reference, so its text needed no rewrite. Added it to the wizards' `README.md` in both the cluster sentence and the contents bullet; appended a dated `MIGRATION.md` section recording the arrival and explicitly superseding the 2026-10-09 "what did not move" clause on that one point; and added `dockerize` to the wizards' `test_install_skills.py` known-procedure set. Gave ADR-024 the explicit note that this move crosses the boundary ADR-021 drew. The overlay's `MIGRATION.md` line stays as the record it is; Step 1.4 adds a dated supersession note beside it rather than rewriting the 2026-10-09 entry.
  - **Testing Log**: wizards `pytest -q` → **34 passed**; `compile-procedures.py --strict` → **18 procedures**, exit 0. Reference sweep over the overlay: no `dockerize` mention outside `MIGRATION.md`, which is history. The overlay now holds **9 procedures**, its target count.
  - **Success Criteria**: PASS.
  - **Tech Debts**: None.
  - **Result**: PASS.

- [x] **Step 1.4**: Trim `map-orientation` and the overlay's own files
  - **Implementation Log**: Trimmed the three producer parentheticals in `map-orientation.md` and removed the now-false `/discovery-contract` handoff bullet (the generators no longer read the map, so the entry had become untrue). Trimmed the three "from `/generate-…`" clauses in `orientation-map-template.md`. Updated the overlay's `README.md` on both the contents line and the Doc-gen bullet, which now records the move rather than describing the family. Appended a dated note to `MIGRATION.md` beside the 2026-08-06 record instead of rewriting it. Repointed the `_KNOWN` spot-check in `tests/test_install_skills.py` from `generate-readme` to `load-project-context`. Added `tests/test_map_orientation_vocabulary.py`: a document assertion that pins the discovery kinds and the type vocabulary and asserts the producer references are gone.
  - **Testing Log**: `compile-procedures.py --strict` → **9 procedures**, exit 0. Overlay suite → **52 passed** (from 47 passed and 1 failed), ruff clean. Direct checks: the map and its template now carry **0** references to `/generate-` or `/discovery-contract`, while every discovery kind and every type name is still present. The installer's installed set matches `output/`'s 9, covered by the suite's prefix, manifest and `_KNOWN` assertions.
  - **Success Criteria**: PASS. The mechanism, the recognizer, the `MAP_PATH` wiring and the 5 seam ops are untouched; no dangling generator reference remains in the overlay, and `hermod-doc` carries no `/map-orientation` reference.
  - **Tech Debts**: None.
  - **Result**: PASS.

- [x] **Step 1.5**: Verify the three repos together
  - **Implementation Log**: Ran every suite and every strict compile across the five repos touched by Phase 1; ran the core's invariant guard; and swept all five for references to the seven moved procedure names. The guard was invoked through Git-Bash by absolute path, because `where bash` resolves to the WSL launcher first and WSL has no distro installed here, so a bare `bash` fails with `execvpe(/bin/bash)`.
  - **Testing Log**: agent-memory-project **52 passed** / 9 procedures compiled; agent-memory-doc **34 passed** / 6; agent-memory-wizards **34 passed** / 18; agent-memory-fleet **41 passed** / 4; agent-memory-local **39 passed** / 4. Every compile exited 0. The core invariant guard printed *"Core invariant holds — the memory core references no add-on procedure by name"*, exit 0. The sweep finds **no live dependency** on a moved procedure: the hits are the repos that now own them, the deliberate move-notes in README/MIGRATION, and this plan.
  - **Success Criteria**: PASS, with one residue named rather than hidden: six docstring examples across the family's five `install-skills.py` / `test_install_skills.py` files cite `generate-readme` as the model of a good opening sentence. They are prose, the name is still a real procedure, and three of those four repos are outside this plan, so they were left alone.
  - **Tech Debts**: the docstring residue above; it is cosmetic and family-wide.
  - **Result**: PASS. **Phase 1 complete**: the overlay holds 9 procedures, `hermod-doc` exists and installs, `dockerize` lives in the wizards, and every suite and the invariant guard are green.

### Phase 2:
- [x] **Step 2.1**: Scaffold the repo
  - **Implementation Log**: Committed the overlay's Phase-1 work first (`ed07920`), because a submodule pin can only cite a commit that exists. Created `hermod-server`: `pyproject.toml` (fastmcp, starlette, uvicorn; dev pytest, ruff, httpx; `uv_build`), `src/hermod/__init__.py`, `src/hermod/configuration/{__init__.py,config.py}`, `tests/test_config.py`, `README.md`, `NOTICE`, `.env.example`, `.gitignore`, `.github/workflows/ci.yml` (checkout with `submodules: recursive`), with `LICENSE` and `.gitattributes` copied from the overlay. Pinned `agent-memory-project` as a submodule with a **relative** URL (`../agent-memory-project`), which git resolves against this repo's own remote: it points at the overlay on GitHub for any clone and at the sibling checkout during development, with no absolute path to rewrite. Two my-call details recorded: port **8210** rather than Munnin's 8200, since a coding client connects both and they run side by side; and the console-script entry left out of `pyproject.toml` because its module (`__main__.py`) arrives in Step 3.2, so nothing here references a module that does not exist.
  - **Testing Log**: `uv sync` succeeds and builds the package; `ruff check` clean; `pytest -q` → **4 passed**, including `test_no_issuer_or_auth_surface`, which asserts the config carries none of Munnin's seven auth fields (decision 5). `git clone --recurse-submodules` into a scratch directory: **9 procedures** materialized, submodule at `ed07920`, and the config imports from the clone. **Caveat, recorded rather than glossed**: that commit is not on GitHub yet, so a clone from the remote cannot fetch the submodule until the overlay is pushed.
  - **Success Criteria**: PASS. The repo installs and its modules import.
  - **Tech Debts**: (1) the submodule pin cites a local-only commit until the overlay is pushed, so a remote clone fails until then; (2) the README's run steps name `python -m hermod`, which Step 3.2 lands — the README's Status section says scaffold.
  - **Result**: PASS.

- [x] **Step 2.2**: The seam bridge and the inliner
  - **Implementation Log**: `content/seam_bridge.py` imports the overlay's `storage-backends/seam.py` by file path (`spec_from_file_location`), cached per content root, and raises `FileNotFoundError` naming the expected path when the checkout or the file is absent. `content/inline.py` carries `_COMPONENT_LINK`, `_lines`, `_emit`, `component_body` and `inline_components` byte-for-byte from the overlay's compiler, with a header recording that it is a copy and naming the fidelity test as what holds it honest. `content/__init__.py` stays a docstring until Step 2.3 adds the loader, so no module here imports one that does not exist.
  - **Testing Log**: `tests/test_inline.py` (6 tests) covers the first-`---` body rule, the label substitution, a surviving non-component link on the same line, a component with no rule contributing nothing, a missing component reported rather than dropped, and a bare `components/…` mention not counting as a reference. `tests/test_seam_bridge.py` (3 tests) asserts the missing-checkout `FileNotFoundError` names the path, that the loaded module really is the overlay's own (its `__file__` sits under `storage-backends`), and that it is cached per root. `pytest -q` → **13 passed**; `ruff check` clean.
  - **Success Criteria**: PASS. Both modules import and the two load-bearing inliner rules are covered.
  - **Tech Debts**: None. One process slip worth recording: the first commit for this step went in before the ruff check had passed; the outstanding line-length error was fixed and the commit amended, so the committed state is green.
  - **Result**: PASS.

- [x] **Step 2.3**: The loader
  - **Implementation Log**: `content/loader.py` with discovery by `sorted(procedures/*.md)` per source minus `EXCLUDED_PROCEDURES` (a constant holding `push-all` and `pull-all`), a registry expressed as a **source list** (`ContentSource`, one entry today) so a Munnin proxy joins beside it rather than replacing it, the backend document taken from configuration (`HERMOD_BACKEND_DOC`, defaulting to `markdown.md`), `get_prompt` inlining then substituting the `## Storage Mechanics` section, `list_resources`/`get_resource` over each source's `templates/`, and titles from each document's own `#` heading with descriptions from its lead sentence (the derivation carried from Munnin's loader, including the parenthesis-aware first-sentence rule). Added `unresolved_ops()`, which the seam module cannot answer — it extracts and substitutes sections and says nothing about which ops a body asked for — so the two `§ op` patterns and the mechanics-stripping helper are carried from the overlay's compiler with a comment saying so.
  - **Testing Log**: probed the real output before writing assertions, then pinned them: `list_prompts()` is exactly the 7 (the 9 minus the 2 exclusions, named literally), `list_resources()` is exactly the 2, `available()` is True, the composed `awaken-coder` grew from 7,126 to 9,029 characters with **no** `/components/` link left, `map-orientation` keeps its template path (templates are copied, never inlined), `$ARGUMENTS` survives a no-argument call and is substituted when one is given, titles and descriptions are derived and all-distinct, `unresolved_ops` is empty for every served prompt, a resource is byte-identical to its file, and an absent checkout serves nothing rather than failing. `pytest -q` → **24 passed**; `ruff check` clean.
  - **Success Criteria**: PASS. The loader serves the trimmed overlay, and an unknown prompt name raises rather than returning nothing.
  - **Tech Debts**: None.
  - **Result**: PASS.

- [x] **Step 2.4**: The fidelity test
  - **Implementation Log**: Added `components_used(name)` to the loader — the one accessor the check needs, because the inlined-component list is the half of composition this server carries rather than imports. Wrote `tests/test_fidelity.py`, which loads the overlay's own `compile-procedures.py` by file path (the same way the server loads the seam), runs `compile_one()` over every served procedure, and compares three **backend-independent** mechanics: the components inlined; the ops each body references, read out of each side's composed text with the mechanics section stripped so the backend's own additions cannot mask a changed body; and that a marker-bearing procedure had its section swapped at all. Composed text is deliberately *not* compared, because the two sides compose different backend documents once the project store exists.
  - **Testing Log**: 5 fidelity tests, full suite **29 passed**, `ruff check` clean. The comparison is guarded against passing vacuously: one assertion requires that at least one procedure actually inlined a component (four of the seven do), and `test_the_check_can_fail` silences the inliner through `monkeypatch` and requires the accounting to diverge from the compiler's, so a green run cannot mean merely that both sides executed.
  - **Success Criteria**: PASS. A change to the overlay's inlining that the carried copy does not follow turns the test red.
  - **Tech Debts**: None.
  - **Result**: PASS. **Phase 2 complete** — the content pipeline serves the trimmed overlay and is held honest against the compiler.

### Phase 3:
- [x] **Step 3.1**: Register the served surface
  - **Implementation Log**: `api_mcp/server.py` registers each served procedure as a FastMCP Prompt with its derived title, derived description and its optional argument slot, each template as a static Resource (`resource://templates/<name>`, `text/markdown`, assistant audience, priority 0.1), and the four read tools plus `ping` and `help`. The prompt's parameter is built dynamically because each procedure names its argument differently, and **both** `__signature__` and `__annotations__` are set — pydantic reads the second and raises on the first alone. Added `PROMPT_ARGUMENTS` and `argument_prompt()` to the loader: the map is **authored rather than parsed**, because the overlay's `## Arguments` sections are prose bullets in varying shapes (a bare `[domain]` line, a `$ARGUMENTS` token plus mode bullets, two positional tokens, and one with no argument at all), and every declared slot is optional since each procedure has an ask-if-missing branch. `INSTRUCTIONS` carries what a client injects at `initialize`; `help` returns the same text for clients that show none.
  - **Testing Log**: 9 tests drive the surface through an **in-memory MCP client**, not a description of one, because the registration path has edges that constants would not touch (a prompt's arguments come from a function signature; a resource must register static rather than as a URI template). Verified: the handshake lists exactly the 7 with all-distinct titles and descriptions; the exclusions never reach it; 2 resources; `read_procedure("awaken-coder")` round-trips with no `/components/` left; `read_resource` is byte-identical to the file; an unserved name returns `served=false` with the listing to call; `ping` is `pong` and `help` carries `INSTRUCTIONS` plus 7 rows; and a prompt argument actually fills the `$ARGUMENTS` slot. Full suite **38 passed**, `ruff check` clean.
  - **Success Criteria**: PASS. Nothing unserved appears in the handshake, and the exclusion list is the only filter. Note the plan's testing line says "9 prompts"; the served set is **7** by decision 8 and Step 2.3, and that is what is asserted.
  - **Tech Debts**: None.
  - **Result**: PASS.

- [x] **Step 3.2**: Compose the app
  - **Implementation Log**: `app.py` builds the loader from configuration (source name `overlay`), builds the MCP face over it, calls `http_app(path="/")`, and mounts it at `/mcp` on a Starlette app that takes the sub-app's **lifespan** — without it the MCP session manager never starts and the face answers nothing, which is the one wiring detail this file exists for. `/health` returns the service name and version and reads nothing. `__main__.py` runs it under uvicorn on the configured host and port, and the `[project.scripts]` entry is back in `pyproject.toml` now that its module exists. **Measured, not assumed**: I probed both `/mcp` and `/mcp/` before deciding whether to carry Munnin's path normaliser, and with this Starlette and this MCP app neither form redirects, so no normaliser is carried.
  - **Testing Log**: `tests/test_app.py` (4 tests) asserts `/health` returns exactly the service identity, that a real `initialize` POST to `/mcp` comes back 200 with the protocol version and the server name in it — which is what proves the session manager started — that **both** slash forms reach the face with no redirect, and that the app builds with no issuer configured. Full suite **42 passed**, `ruff check` clean. Verified separately that the console script resolves: `uv run hermod` booted uvicorn and completed application startup, and the process was then stopped and the port confirmed free.
  - **Success Criteria**: PASS. One process serves both surfaces and the MCP session manager starts.
  - **Tech Debts**: `main()` ignores argv, so `hermod --help` starts the server instead of printing help. Harmless (the README documents the run command) and not worth a parser until a second flag exists.
  - **Result**: PASS.

- [x] **Step 3.3**: Boot and connect
  - **Implementation Log**: Wrote `tests/test_end_to_end.py`, which starts a **real uvicorn** on a free loopback port in a thread and connects FastMCP's HTTP client to it. That is the automated form of this step's "start the process and connect a client": running `claude mcp add` would edit the client's config, which is not something a test should do. Four checks: a real client answers `pong` and lists 7 prompts over HTTP; `read_procedure("awaken-coder")` comes back composed with no dangling component reference; **transport parity** — every served prompt arrives byte-identical to what the loader composes; and `/health` answers on the same live process.
  - **Testing Log**: 4 end-to-end tests; full suite **46 passed**, `ruff check` clean. One interpretation recorded: the plan's twin-parity line reads as "served prompt against the compiled command", which Step 2.4 already covers by mechanic accounting. The parity this step adds is the one nobody looks at — the transport against the source — since a session manager that never started, an SSE frame that mangles a line, or a mount answering the wrong path are all invisible to an in-memory client.
  - **Success Criteria**: PASS. A real client answers `pong`, lists the 7 served procedures, and reads a composed prompt.
  - **Tech Debts**: None.
  - **Result**: PASS. **Phase 3 complete** — the server boots, serves both faces, and a real client drives it.

### Phase 4:
- [x] **Step 4.1**: Schema, migrations and repository
  - **Implementation Log**: Created `src/hermod/data_entities/`: `project_context.py` (the two entities — `ContextEntry` addressed by `(project, scope, theme)` with a `ContextScope` enum of `shared`/`private`, and `OrientationMap` keyed by `project` alone), `schema_migrations.py` (the runner carried from Munnin's: ordered `migrations/*.sql`, a `migration_history` table, one transaction per migration, checksum refusal), and `migrations/0001_init.sql` (the two tables, a **partial** unique index on `(project, scope, theme) WHERE deleted_date IS NULL`, a browse index, no FKs and no FTS). Created `src/hermod/data_repositories/`: `project_repository.py` (the Protocol — entries: list/get/create/update/move/delete; map: exists/get/create/write) and `sqlite_project_repository.py` (the impl — connection-per-op with WAL, migrations applied lazily on the first op, `deleted_date` tombstones). Three calls recorded: **create and update are distinct strict ops, not one upsert**, mirroring Munnin's `create_agent`/`upsert_agent` split, so creating over a theme is refused rather than silently absorbed; **the unique index is partial on `deleted_date IS NULL`**, so a tombstone frees the theme and delete-then-recreate is a new entry, exactly as removing and recreating the file is on markdown; **move is one UPDATE of the `scope` column alone**, the DB's single-step form of the markdown backend's copy-then-delete, so the body cannot drift.
  - **Testing Log**: `ruff check` clean. `pytest -q` → **57 passed** (46 before this step; 11 new in `tests/test_store.py`). `test_migrations_apply_to_a_fresh_database` asserts every migration is `pending`, then `applied` after one call and the three tables exist; `test_migrations_are_idempotent_on_re_run` asserts the second call returns `[]`; a third asserts an already-applied file edited afterwards raises `RuntimeError` rather than being skipped. The repository tests round-trip an entry and a map and pin the behaviours the ops need: create refuses a duplicate theme and writes nothing, update replaces the body and raises on a missing entry, move changes only the scope (body asserted untouched) and refuses an occupied target, delete hides the entry from every read and frees the theme for re-creation, and a map's `created_date` survives a write while `write_map` on an absent map raises.
  - **Success Criteria**: PASS. A fresh database reaches the schema in one call (the repository's first operation applies it — asserted with no explicit migration step), and a re-run changes nothing.
  - **Tech Debts**: none.
  - **Result**: PASS.

- [x] **Step 4.2**: The context service and the store's tools
  - **Implementation Log**: Created `src/hermod/business_services/context_service.py` (`ContextService` over the repository: `list_context_entries`, `read_context_entry`, `create_context_entry`, `update_context_entry`, `move_context_entry`, `delete_context_entry`, `check_entry_size`, `map_exists`, `read_map`, `create_map`, `write_map`) plus the package `__init__`. Registered one MCP tool per method in `api_mcp/server.py` (`_register_store`), on the **same** face as the content, so a served db mechanic naming `§ create-context-entry` resolves to something the agent can call; `build_mcp` now takes the service, and `app.py` builds `SqliteProjectRepository(config.db_path)` → `ContextService` → `build_mcp`. Two calls recorded. **The size cap is carried, not invented**: 1000 lines is the markdown backend's split point, and the store **refuses** the write instead of splitting, because a row has no second file to split into — same threshold, different remedy, because the medium differs. **`§ ensure-context-dir` and `§ update-context-index` get no code and no tool**: there is no directory, and the index *is* the SELECT `list_context_entries` performs, so `db.md` declares them no-ops exactly as the memory core's db backend no-ops its derived index and directory steps. `check_entry_size` is a pure measurement and `create`/`update` are where it is enforced, so a caller can read the verdict before writing.
  - **Testing Log**: `ruff check` clean. `pytest -q` → **65 passed** (57 before this step; 8 new). Service tests cover each op: create/list/read including the scope narrowing, update and move (the body asserted untouched across the move), delete, `check_entry_size` returning `SizeVerdict(lines, max_lines, oversized)` with `create` and `update` refusing an over-cap body, the four map ops, and the bad-scope refusal. `test_every_store_tool_round_trips_without_an_overlay` drives **all eleven tools** through a real in-memory MCP client against a loader whose checkout does not exist, which proves the store is served independently of `content` and that each op is genuinely registered rather than merely named. `test_the_store_tools_share_the_face` in `test_mcp_surface.py` pins the registered set; that file's fixture and `build_mcp`'s signature moved with the store.
  - **Success Criteria**: PASS. Every op `db.md` names outside the two declared no-ops has an implementation and a test; the two no-ops carry their declaration in `db.md` (Step 4.3 rewrites it) and are guarded by the loader's unresolved-op check.
  - **Tech Debts**: `db.md`'s `§ check-entry-size` line currently reads "no length cap expected", which this step supersedes — the plan's own testing line requires the refusal. Step 4.3 rewrites the checklist into mechanics and must record the cap.
  - **Result**: PASS.

- [x] **Step 4.3**: Write `db.md`'s mechanics and compose onto it
  - **Implementation Log**: Rewrote `storage-backends/db.md` from a declared checklist into concrete mechanics: every op a served procedure references now names the tool it calls (`create_context_entry(project, scope, theme, content, description?, tags?)`, and so on), with an `## all-procedures` preamble stating that every op is a tool call on this server and that the project is an argument rather than a path. `§ ensure-context-dir` and `§ update-context-index` are declared **no-ops with their reason**, mirroring the memory core's db backend. Added the `## project-wrap-up` section to `markdown.md` (`§ persist-store` → `/push-all`) and to `db.md` (→ `/push-project`: the store is the server's own file, written as every op runs, so only the project's commits are left to push); gave `project-wrap-up.md` a `## Storage Mechanics` marker section, changed Step 4 from executing `/push-all` to executing `§ persist-store`, and reworded the body's one other `/push-all` mention so the body no longer hardcodes a backend's command (`/push-all` is unserved, so the served text must not name it). `§ select-project-episode` resolves to a **delegation to the memory layer** — episodes are Munnin's records and the store holds none — and `§ load-coding-reasoning` and `§ check-fleet-roster` delegate the same way, which is where the no-join decision becomes visible. Updated `storage-backends/README.md` (the backend is implemented; `project-wrap-up` carries exactly one op). Flipped `hermod`'s `DEFAULT_BACKEND_DOC` to `storage-backends/db.md` and pinned the overlay at `6d5db11` in the `agent-memory-project` submodule.
  - **Testing Log**: Overlay: `pytest` → **52 passed**; `compile-procedures.py --strict` → 9 procedures, exit 0; the compiled `output/project-wrap-up.md` carries the substituted `### § persist-store` → `/push-all` with no `## Storage Mechanics` marker left. hermod: `ruff check` clean, `pytest -q` → **68 passed** (65 before this step; 3 new in `test_loader.py` — the served ops are the store's tool calls, the served `project-wrap-up` names `/push-project` and not `/push-all`, and the served `awaken-coder` delegates the episode step). One **real defect the fidelity test caught**: the `## all-procedures` preamble's literal `` `§ op` `` registered as a phantom op named `op` in the served text, so the carried-op accounting parted company with the compiler's (`+op`); the preamble was reworded, and all seven served prompts were then validated against the overlay working tree via `HERMOD_CONTENT_ROOT` (unresolved `[]`, ops and components matching the compiler, marker gone) **before** re-pinning.
  - **Success Criteria**: PASS. No served prompt carries an unresolved op; `project-wrap-up` resolves to `/push-all` on markdown and `/push-project` on the db, and the served form names the latter; `awaken-coder` delegates the episode step.
  - **Tech Debts**: the submodule pin (`6d5db11`) is a local-only overlay commit until the overlay is pushed, so a remote clone still cannot fetch it (the Step 2.1 debt, carried). The two delegations are the recorded costs of decision 4 (no join).
  - **Result**: PASS.

- [x] **Step 4.4**: Round-trip and fidelity re-run
  - **Implementation Log**: Added a real-HTTP round-trip to `tests/test_end_to_end.py` — an entry created through `create_context_entry` (the op `update-project-context` resolves to) is listed and read back through `list_context_entries` / `read_context_entry` (the ops `load-project-context` resolves to), over a live uvicorn. The `live_server` fixture now points the store at a temp file rather than the repo's runtime `data/hermod.db`, so a test that writes project context leaves no rows in the store an agent is using. **No fidelity change was needed**: `test_fidelity.py` composes through the loader's configuration, and Step 4.3 flipped that configuration to `db.md`, so the carried inliner is re-proved against the store backend by the same run.
  - **Testing Log**: `ruff check` clean; `pytest -q` → **69 passed** (68 before this step; 1 new). The round trip asserts the written scope is the scope read, the content arrives whole, and the same theme in the **other** scope stays absent — the entry is addressed rather than searched for. The fidelity suite (5 tests) stays green with `db.md` composed.
  - **Success Criteria**: PASS. A project context entry round-trips through the server's tools, and the fidelity check is green under the store backend.
  - **Tech Debts**: none.
  - **Result**: PASS. **Phase 4 complete** — the store exists, is served, and its ops are what a served procedure resolves to.

### Phase 5:
- [x] **Step 5.1**: Write the ADR
  - **Implementation Log**: Read `docs/adr/2026-10-12-hermod-doc-extraction-and-hermod-server.md` against what shipped and reconciled the two facts implementation settled that the plan's requirements did not yet carry. **The store's concrete shape**: two tables (`project_context` addressed by `(project, scope, theme)`, `orientation_map` keyed by `project`), a migration runner, a `ProjectRepository` Protocol, one MCP tool per op, `§ ensure-context-dir` and `§ update-context-index` as **declared no-ops**, and an entry over 1000 lines **refused** rather than split. **The no-join cost**, now visible in three ops: `§ select-project-episode`, `§ load-coding-reasoning` and `§ check-fleet-roster` all resolve to a delegation to the memory layer, recorded against the rejected-join alternative rather than hidden. No decision changed, so the ADR is finalized in place rather than superseded.
  - **Testing Log**: The overlay suite is green (**52 passed**) after the edits; the ADR's link `../../plans/2026-10-12-agent-memory-project-hermod-server.md` resolves; every rejected alternative still matches the plan's section F, which the ADR's six-alternative list is a curated subset of with no contradiction.
  - **Success Criteria**: PASS. The ADR describes the system as built rather than as planned, and matches the decisions recorded here.
  - **Tech Debts**: none.
  - **Result**: PASS.

- [ ] **Step 5.2**: The cross-repo prose and the store's entries
  - **Implementation Log**: [What was done]
  - **Testing Log**: [What was tested and results]
  - **Success Criteria**: [Pass/Fail against step's success criteria]
  - **Tech Debts**: [Optional - any shortcuts, TODOs, or future improvements noted]
  - **Result**: [Outcome compared to success criteria]

---

## **QUALITY REVIEW**
*Filled by procedure Step 16 (delegated to `/analyze-code-quality` in embedded mode) after all execution phases are complete. **Static** review — answers "is the code clean?".*

- **Scope**: [Files reviewed — from Execution Log, reconciled against `git diff --name-only`]
- **Quality Standard**: [quality-standard.md found / not found — dimensions applied]
- **Findings**: [Issues found, or "No findings — implementation meets quality dimensions"]
- **Fixed**: [What was fixed from approved findings, or "N/A"]

---

## **QA HANDOFF**
*Filled by procedure Step 17 after Quality Review is resolved. This plan is **not** runtime-verified — this section records the plan for that verification, which happens in a QA session with the stack up.*

- **Scope**: [Modules touched — mapped from Execution Log scope]
- **QA instrument**: [Set up (map + bench) / NOT SET UP — auto-skipped]
- **Integration coverage**: **NONE** — the bench check failed: `agent-memory-project` has no `qa/qa-map.md`, so no bench exists to probe and the stack state is unknown (probe: none available). Phases 2, 3 and 4 cross real boundaries (a served composition over a submodule, an HTTP face, a store) and would carry integration tests if the instrument existed. Fix: `/map-qa-instrument create` then `/build-qa-bench`. Confirmed with [USER-NAME] before implementation: confirmed 2026-10-12 ("proceed").
- **Checklist**: [`qa/checklists/{feature}.md`, or "none — skipped, reason"]
- **Coverage split**: [N automated (named tests) / N manual — of which N are UI-bound]
- **Runtime verification**: **NOT DONE.** Next action: [`/run-qa-test --checklist qa/checklists/{feature}.md` once the stack is up | set up the instrument first: `/map-qa-instrument create` → `/build-qa-bench`]

> Do not read a filled checklist as a passed one. This section says a verification *plan* exists, nothing more.

---

## **POST-COMPLETION**
After all phases are executed, logged, and both **Quality Review** + **QA Handoff** are filled, move this plan to `plans/completed/`:
`mkdir -p ./plans/completed && mv ./plans/[this-file].md ./plans/completed/[this-file].md`
