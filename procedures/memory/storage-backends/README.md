# Project storage backends

Project-memory procedures keep their shared judgment in the procedure and refer to named backend regions for concrete storage mechanics. The Markdown backend gives file operations; the DB backend gives Hermod tool-call instructions. Repository operations such as git push are separate from project-memory storage.

The two canonical documents are [markdown.md](markdown.md) and [db.md](db.md). Their region IDs identify the procedure or shared preamble. Each procedure's Format 2 storage reference selects the same region ID from the chosen backend. The DB-only `all-procedures` region supplies the shared tool-call preamble; it includes the separator before the procedure region. Operations use the `§ op-name` notation and each selected backend must define the operations the body references.

For example, `procedures/awaken-coder.md` references the shared project-identity and HOME components and its `awaken-coder` backend region. The compiler renders Markdown with `procedure-composer`; Hermod renders DB. Reference interiors stay empty: change the owning component or region, not a cached rendering. Template-copy references are ordinary links and remain in the output.

The vendored `seam.py` remains for legacy compiler callers that still supply heading-based input; converted procedures use the shared composer instead.
