"""The orientation map's vocabulary survived the doc cluster's extraction.

``map-orientation`` is prose, so this is a document assertion rather than an executing test.
It pins the two halves the 2026-10-12 trim had to leave alone - what the map discovers, and
what it classifies an artifact as - and asserts that the one thing the trim did remove, the
names of the procedures that produce those artifacts, is gone.

Why the trim was safe: the map indexes docs, and docs carry their `doc_type` frontmatter
wherever they came from. Naming their producer was provenance the index never needed, and
`hermod-doc` no longer reads the map back, so nothing consumes the relationship either way.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = (ROOT / "procedures" / "map-orientation.md").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "templates" / "orientation-map-template.md").read_text(encoding="utf-8")

# What the map discovers: the artifact kinds, not their producers.
DISCOVERED = [
    "README*.md",
    "ARCH*.md",
    "ADR-*.md",
    "*.mmd",
    "docs/flows/",
    "docs/domain/",
    "docs/architecture/",
    "CONTRIBUTING.md",
]

# What it classifies them as: the type vocabulary the legend publishes.
TYPES = [
    "7q-readme",
    "architecture-map",
    "architecture-overview",
    "flow-diagram",
    "flow-journey-map",
    "domain-model",
    "domain-context-map",
    "adr",
    "orientation-map-link",
]


def test_discovery_list_is_intact() -> None:
    for kind in DISCOVERED:
        assert kind in MAP, f"the map no longer discovers {kind}"


def test_type_vocabulary_is_intact() -> None:
    for name in TYPES:
        assert name in MAP, f"the map no longer classifies {name}"
        assert name in TEMPLATE, f"the legend no longer publishes {name}"


def test_the_recognizer_survived() -> None:
    """A README with no `doc_type` is still recognised by its own structure."""
    assert "doc_type: 7q-readme" in MAP
    assert "7Q structure" in MAP


def test_no_producer_is_named() -> None:
    """The trim removed provenance: the map indexes artifacts, not the procedures making them."""
    for text, what in ((MAP, "map-orientation"), (TEMPLATE, "orientation-map-template")):
        assert "/generate-" not in text, f"{what} still names a doc generator"
        assert "/discovery-contract" not in text, f"{what} still names the discovery contract"
