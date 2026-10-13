# Add Coding Reasoning Protocol

Capture an anti-pattern or decision-making approach that only fires for a **coding** agent, and write it into the fleet's **coding-reasoning lane**.

The lane is fleet memory, but it is its own record type, so a chat agent's awakening never carries it: `awaken` loads its universal layer by type, and the coding lane is not that type. Only `/awaken-coder` reads it.

*How* the lane is physically read and written is delegated to the active **storage backend** (see [Storage Mechanics](#storage-mechanics)).

## Arguments

`$ARGUMENTS`

- `/add-coding-reasoning [context]` → Document the coding reasoning pattern described in context
- `/add-coding-reasoning` → Will ask for context

If no arguments provided, ask: "What coding reasoning pattern or anti-pattern should I document?"

---

## Procedure

### Step 1: Read the Coding Lane

Read the current lane (**§ read-coding-lane**) so the new pattern fits alongside the existing ones and does not duplicate one.

### Step 2: Draft from the Template

Draft the entry using the reasoning-pattern template (**§ template**), the same lean shape a `reasoning` pattern uses. The template carries the shape; fill Title (action plus consequence, an emoji, and a PATTERN TYPE tag), Why (the pain anchor, kept sharp), Signals, and a Final Conclusion, and Rule plus the optional Do / Guardrail / Siblings where they add beyond it.

### Step 3: Generate the Pattern's UUID

Generate 8-4-4-4-12 (**§ generate-uuid**); the pattern's fingerprint for the COUNT roster and cross-references.

### Step 4: Persist

Write the completed pattern into the coding lane (**§ persist-coding-reasoning**).

---

## Storage Mechanics

The operations referenced above — **§ read-coding-lane**, **§ template**, **§ generate-uuid**, **§ persist-coding-reasoning** — are defined by the **active storage backend**:

- **Markdown (native)** — follow `storage-backends/markdown.md` → its `add-coding-reasoning` section.
- **DB (Hermod)** — the equivalents live in `storage-backends/db.md` → its `add-coding-reasoning` section.

See the seam contract at `storage-backends/README.md` for how this swap works.
