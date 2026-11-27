"""Format 2 sources use the shared composer and retain backend-specific mechanics."""

import re
from pathlib import Path

import pytest
from procedure_composer import CompositionError, FileSource, MemorySource, compose, validate_catalog

ROOT = Path(__file__).resolve().parents[1]


def test_real_catalog_renders_both_backends_and_tool_instructions() -> None:
    source = FileSource(ROOT)
    catalog = validate_catalog(source)
    assert set(catalog.procedures) == {p.stem for p in (ROOT / "procedures").glob("*.md")}
    for name in catalog.procedures:
        for backend in ("markdown", "db"):
            result = catalog.compose(name, backend)
            assert result.text
    db = catalog.compose("update-project-context", "db").text
    markdown = catalog.compose("update-project-context", "markdown").text
    assert "create_shared_context_entry(project" in db
    assert "create_agent_context_entry(project" in db
    assert "create_shared_context_entry(project" not in markdown
    assert "[path-to-agent-memory-project]/templates/project-context-template.md" in db


def test_awakening_db_links_to_a_public_pinned_adr() -> None:
    result = compose("awaken-coder", "db", FileSource(ROOT))
    assert re.search(
        r"\[ADR-029\]\(https://github\.com/alvseek/agent-memory-project/blob/"
        r"[0-9a-f]{40}/docs/adr/2026-10-14-hermod-reads-memory-rows-for-the-coding-awakening\.md\)",
        result.text,
    )


def test_unknown_component_and_storage_region_fail() -> None:
    source = FileSource(ROOT)
    files = {path: source.read(path) for path in source.paths("procedures")}
    path = "procedures/awaken-coder.md"
    for old, new in (
        (b"procedures/components/project-identity.md", b"procedures/components/missing.md"),
        (b'target="awaken-coder"', b'target="missing-region"'),
    ):
        altered = dict(files)
        assert old in altered[path]
        altered[path] = altered[path].replace(old, new, 1)
        with pytest.raises(CompositionError, match="missing"):
            compose("awaken-coder", "db", MemorySource(altered))
