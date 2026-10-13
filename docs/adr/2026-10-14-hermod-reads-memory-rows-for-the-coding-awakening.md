# ADR-029: Hermod Reads Memory Rows for the Coding Awakening

**Date**: 2026-10-14

**Status**: Accepted

---

## Problem

A coding awakening costs five tool calls across two faces: Munnin's `awaken`, a conditional `get` for the project's episode body, `coding_reasoning`, `list_context_entries`, and `map_exists` plus `read_map`. Measured on 2026-10-13 that assembly was 14 model steps and 157 seconds, while the core's single call, carrying the same payload, is fast. The cost is step count, and the steps exist because the client has to visit two servers to start one session.

---

## Decision

**We decided to**: give the coding awakening one composite call on Hermod, `awaken_coder(domain, projects)`, and leave Munnin's `awaken` untouched.

The tool returns the coding half of an awakening in one read-only call: the reasoning lane, the episode index for the project set, one episode body per project in the set, the context index for the set, and every map for the set. To do that, Hermod reads two record types it does not own, `episode` and `coding_reasoning`, from the same database it already reads for project context. It filters and returns; it does not re-implement what an awakening contains.

**Why we chose this:**
- It removes three of five calls without crossing the join that ADR-024 deferred.
- The memory assembly stays in one place, so nothing has to be kept in step across two servers.
- It makes the one-call future smaller, because the service this creates is exactly where a Munnin client would later be added.

---

## What to Build (Requirements)

**Core Requirements:**
- `awaken_coder(domain, projects)` on Hermod's MCP face, read-only, returning the lane, the set-scoped episode index, one episode body per project, the context index for the set, and every map for the set with its dates
- Two new repository reads for `episode` and `coding_reasoning` rows, applying the same hot-read filters Munnin applies (`deleted_date IS NULL`, `archived_date IS NULL`)
- The overlay's `awaken-coder` body and its DB backend ops rewritten to read from that payload, with `storage-backends/markdown.md` untouched
- The set's first element is the session's repository, stated in the tool's docstring because the resolved project is implicit in the order

**Success Criteria:**
- A coding awakening completes in two calls issued in one step
- A parity test proves Hermod's filters exclude soft-deleted and archived rows exactly as Munnin's do
- The served procedure names the new call, and no step calls what the payload already answered
- The measured step count falls from 14 to roughly three

---

## Alternatives Rejected

- **Batching the existing five calls**: leaves the count intact and keeps the ordering in prose, which is what produced a 14-step awakening.
- **A narrowing knob on Munnin's `awaken`**: re-opens a project-shaped hole on a tool that was made project-blind the day before.
- **Hermod calling Munnin internally**: pays the join ADR-024 deferred, with a credential and an availability dependency, before it is needed.
- **Munnin returning the complete set**: makes the core project-aware again, which the same day's work had just undone.
- **Hermod re-implementing the assembly**: buys one hop with a second implementation of an awakening that must then be kept in step forever.

---

**Full context**: [2026-10-13-agent-memory-project-awaken-coder-single-call.md](../../plans/2026-10-13-agent-memory-project-awaken-coder-single-call.md)
