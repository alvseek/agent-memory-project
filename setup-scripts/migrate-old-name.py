"""One-time migration: clean the pre-rename `agent-coding-*` / `*.md` installs.

The overlay was renamed `agent-memory-coding-skill` -> `agent-memory-project` (folder prefix
`agent-coding-` -> `agent-project-`, manifest `.agent-memory-coding-skill-*` ->
`.agent-memory-project-*`). An installer's cleanup reads **its own** manifest, so the renamed
installer cannot see the old installs and would leave them orphaned.

Run this once after pulling the rename, then re-run the platform installers. It removes every
entry the **old** manifest claims that no current sibling manifest also claims, then deletes the
old manifest; the reinstall writes the new one.
"""

from __future__ import annotations

from pathlib import Path

_HOME = Path.home()

# (target dir, old manifest name, sibling manifest names that must be protected)
_TARGETS = [
    (
        _HOME / ".claude" / "commands",
        ".agent-memory-coding-skill-manifest",
        [
            ".agent-memory-manifest",
            ".agent-memory-fleet-manifest",
            ".agent-memory-wizards-manifest",
        ],
    ),
    (
        _HOME / ".config" / "opencode" / "skills",
        ".agent-memory-coding-skill-opencode-manifest",
        [
            ".agent-memory-opencode-manifest",
            ".agent-memory-fleet-opencode-manifest",
            ".agent-memory-wizards-opencode-manifest",
    ".agent-memory-doc-opencode-manifest",
        ],
    ),
    (
        _HOME / ".agents" / "skills",
        ".agent-memory-coding-skill-codex-manifest",
        [
            ".agent-memory-codex-manifest",
            ".agent-memory-fleet-codex-manifest",
            ".agent-memory-wizards-codex-manifest",
        ],
    ),
    (
        _HOME / ".gemini" / "config" / "skills",
        ".agent-memory-coding-skill-antigravity-manifest",
        [
            ".agent-memory-antigravity-manifest",
            ".agent-memory-fleet-antigravity-manifest",
            ".agent-memory-wizards-antigravity-manifest",
        ],
    ),
]


def _claims(target: Path, names: list[str]) -> set[str]:
    out: set[str] = set()
    for name in names:
        p = target / name
        if p.is_file():
            out |= {ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()}
    return out


def migrate(target: Path, old_manifest: str, siblings: list[str]) -> None:
    manifest = target / old_manifest
    if not manifest.is_file():
        print(f"  {target}: no old manifest ({old_manifest}) - skip")
        return
    protected = _claims(target, siblings)
    removed = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry in protected:
            continue
        path = target / entry
        if path.is_dir():
            import shutil

            shutil.rmtree(path)
            removed += 1
        elif path.is_file():
            path.unlink()
            removed += 1
    manifest.unlink()
    print(f"  {target}: removed {removed} stale entr(ies), deleted {old_manifest}")


def main() -> int:
    print("Migrating pre-rename agent-memory-coding-skill installs:")
    for target, old_manifest, siblings in _TARGETS:
        if target.is_dir():
            migrate(target, old_manifest, siblings)
        else:
            print(f"  {target}: absent - skip")
    print("Done. Re-run the platform installers to install agent-memory-project.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
