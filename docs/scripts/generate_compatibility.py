"""Render the core<->SDK compatibility tables into the docs page from the manifest.

This script is the one-way bridge between ``compatibility.toml`` (the human-edited
source of truth) and ``docs/src/compatibility.md`` (the rendered page). It reads the
manifest with the standard-library ``tomllib`` (no third-party dependency), renders a
compact release matrix table, a Markdown-footnote ("Notes") definition list, and a per-SDK
requirements table, and splices each into the Markdown page between its dedicated
``BEGIN GENERATED`` / ``END GENERATED`` markers so the hand-written prose and the live
badge strip are preserved.

The matrix table is intentionally compact: every cell holds only a version, a range,
or the sentinel ``—``. The footnote marker is appended to the END of each row's
``Core release`` cell as a real Markdown footnote reference (``[^cnN]``); the "Notes"
section renders the matching footnote definitions (``[^cnN]: text``), so mdBook renders
each marker as a clickable superscript link (hanging off the core-release identifier)
that jumps to its note. The long provenance and caveat prose lives in those footnote
definitions below the table, so the table columns stay uniform and no single row
balloons. There is no dedicated ``Ref`` column — the superscript rides the core cell.

Run it with no arguments to regenerate the page in place. Run it with ``--check`` to
verify the committed page already matches the manifest (used by CI to fail on drift).
The rendering is deterministic and idempotent: running it twice produces byte-identical
output.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Final

# Repo layout: this file lives at docs/scripts/, the manifest at the repo root,
# and the rendered page at docs/src/compatibility.md.
SCRIPT_DIR: Final[Path] = Path(__file__).resolve().parent
REPO_ROOT: Final[Path] = SCRIPT_DIR.parent.parent
MANIFEST_PATH: Final[Path] = REPO_ROOT / "compatibility.toml"
PAGE_PATH: Final[Path] = REPO_ROOT / "docs" / "src" / "compatibility.md"

MATRIX_BEGIN: Final[str] = "<!-- BEGIN GENERATED:matrix -->"
MATRIX_END: Final[str] = "<!-- END GENERATED:matrix -->"
NOTES_BEGIN: Final[str] = "<!-- BEGIN GENERATED:notes -->"
NOTES_END: Final[str] = "<!-- END GENERATED:notes -->"
REQUIREMENTS_BEGIN: Final[str] = "<!-- BEGIN GENERATED:requirements -->"
REQUIREMENTS_END: Final[str] = "<!-- END GENERATED:requirements -->"

# Prefix for the Markdown footnote keys shared by the matrix core-release superscript
# markers and the "Notes" footnote definitions, e.g. footnote 1 is keyed ``cn1``
# (compat-note 1).
FOOTNOTE_KEY_PREFIX: Final[str] = "cn"

# Order in which per-SDK columns/rows are rendered, with their display headers.
SDK_KEYS: Final[tuple[str, ...]] = ("python", "node", "go")
SDK_HEADERS: Final[dict[str, str]] = {
    "python": "Python SDK",
    "node": "Node SDK",
    "go": "Go SDK",
}


def _escape_cell(value: str) -> str:
    """Escape a string so it is safe inside a Markdown table cell.

    Pipes would otherwise be read as column separators; everything else is left
    verbatim so provenance notes render as written.
    """
    return value.replace("|", "\\|")


def load_manifest(path: Path) -> dict[str, object]:
    """Read and parse the TOML manifest at ``path`` into a plain dictionary."""
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _releases(manifest: dict[str, object]) -> list[dict[str, object]]:
    """Return the ``[[release]]`` array, validating its shape."""
    releases = manifest.get("release", [])
    if not isinstance(releases, list):
        raise TypeError("manifest key 'release' must be an array of tables")
    for entry in releases:
        if not isinstance(entry, dict):
            raise TypeError("each [[release]] entry must be a table")
    return releases


def _note_texts(manifest: dict[str, object]) -> dict[str, str]:
    """Return a mapping of footnote key -> note text from the ``[[note]]`` array."""
    notes = manifest.get("note", [])
    if not isinstance(notes, list):
        raise TypeError("manifest key 'note' must be an array of tables")
    texts: dict[str, str] = {}
    for entry in notes:
        if not isinstance(entry, dict):
            raise TypeError("each [[note]] entry must be a table")
        key = str(entry.get("key", ""))
        if not key:
            raise ValueError("each [[note]] entry must have a non-empty 'key'")
        texts[key] = str(entry.get("text", ""))
    return texts


def assign_footnotes(manifest: dict[str, object]) -> tuple[dict[str, int], list[str]]:
    """Number footnotes in first-cited order across the release rows.

    Returns a ``(ref -> number)`` map and the note texts ordered by that number, so
    the matrix markers and the rendered "Notes" list share one consistent numbering.
    Every ``ref`` cited by a release must resolve to a ``[[note]]`` text.
    """
    texts = _note_texts(manifest)
    numbers: dict[str, int] = {}
    ordered: list[str] = []
    for entry in _releases(manifest):
        ref = str(entry.get("ref", ""))
        if not ref or ref in numbers:
            continue
        if ref not in texts:
            raise ValueError(f"release ref {ref!r} has no matching [[note]] entry")
        numbers[ref] = len(ordered) + 1
        ordered.append(texts[ref])
    return numbers, ordered


def render_matrix(manifest: dict[str, object], footnotes: dict[str, int]) -> str:
    """Render the per-core-release compatibility matrix as a compact Markdown table.

    Each row pairs one core release with the SDK release (or range) that speaks its
    wire protocol, plus the protocol contract and lifecycle status. Every cell stays
    short: a version, a range, or the sentinel ``—``. The row's footnote marker is
    appended to the END of the ``Core release`` cell as a Markdown footnote reference
    (e.g. ``v0.0.1-alpha.5[^cn2]``) that mdBook renders as a clickable superscript link
    hanging off the core identifier, jumping to its definition in the "Notes" list
    below; rows that share a note (same ``ref``) emit the same key. There is no
    separate ``Ref`` column.
    """
    header = (
        "| Core release | Status | Protocol | "
        + " | ".join(SDK_HEADERS[key] for key in SDK_KEYS)
        + " |"
    )
    separator = "|---|---|---|" + "---|" * len(SDK_KEYS)

    lines: list[str] = [header, separator]
    for entry in _releases(manifest):
        sdks = entry.get("sdks", {})
        if not isinstance(sdks, dict):
            raise TypeError("each [release.sdks] entry must be a table")
        ref = str(entry.get("ref", ""))
        marker = f"[^{FOOTNOTE_KEY_PREFIX}{footnotes[ref]}]" if ref in footnotes else ""
        core_cell = _escape_cell(str(entry.get("core", "—"))) + marker
        cells = [
            core_cell,
            _escape_cell(str(entry.get("status", "—"))),
            _escape_cell(str(entry.get("proto", "—"))),
        ]
        cells.extend(_escape_cell(str(sdks.get(key, "—"))) for key in SDK_KEYS)
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def render_notes(ordered_notes: list[str]) -> str:
    """Render the "Notes" section as Markdown footnote definitions.

    Each definition (``[^cnN]: text``) matches the ``[^cnN]`` footnote reference the
    matrix emits for the same note, so mdBook renders the matrix markers as clickable
    superscript links that jump here. The long provenance and caveat prose lives in
    these definitions so the table itself stays compact. Definitions are separated by
    blank lines so each is parsed as its own single-paragraph footnote.
    """
    if not ordered_notes:
        return "_No footnotes._"
    lines: list[str] = []
    for index, text in enumerate(ordered_notes, start=1):
        lines.append(f"[^{FOOTNOTE_KEY_PREFIX}{index}]: {text}")
    return "\n\n".join(lines)


def render_requirements(manifest: dict[str, object]) -> str:
    """Render the per-SDK runtime-requirements table as a Markdown table."""
    requirements = manifest.get("requirements", {})
    if not isinstance(requirements, dict):
        raise TypeError("manifest key 'requirements' must be a table")

    header = "| SDK | Runtime requirement | Install | Source |"
    separator = "|---|---|---|---|"
    lines: list[str] = [header, separator]
    for key in SDK_KEYS:
        entry = requirements.get(key)
        if not isinstance(entry, dict):
            raise TypeError(f"missing or malformed [requirements.{key}] table")
        label = str(entry.get("label", SDK_HEADERS[key]))
        runtime = str(entry.get("runtime", "—"))
        install = str(entry.get("install", "—"))
        source = str(entry.get("source", "—"))
        cells = [
            _escape_cell(label),
            _escape_cell(runtime),
            "`" + _escape_cell(install) + "`",
            _escape_cell(source),
        ]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def splice(page: str, begin: str, end: str, body: str) -> str:
    """Replace the content between ``begin`` and ``end`` markers in ``page``.

    The markers themselves are preserved; the body is surrounded by blank lines so
    the Markdown table renders correctly regardless of the surrounding prose.
    """
    start = page.find(begin)
    stop = page.find(end)
    if start == -1 or stop == -1 or stop < start:
        raise ValueError(f"markers {begin!r} / {end!r} not found (or out of order)")
    head = page[: start + len(begin)]
    tail = page[stop:]
    return f"{head}\n\n{body}\n\n{tail}"


def render_page(manifest: dict[str, object], current: str) -> str:
    """Return the page text with every generated block refreshed from the manifest."""
    footnotes, ordered_notes = assign_footnotes(manifest)
    rendered = splice(
        current, MATRIX_BEGIN, MATRIX_END, render_matrix(manifest, footnotes)
    )
    rendered = splice(rendered, NOTES_BEGIN, NOTES_END, render_notes(ordered_notes))
    rendered = splice(
        rendered, REQUIREMENTS_BEGIN, REQUIREMENTS_END, render_requirements(manifest)
    )
    return rendered


def main(argv: list[str] | None = None) -> int:
    """Entry point: regenerate the page, or with --check verify it is up to date."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed page matches the manifest; exit nonzero if stale",
    )
    args = parser.parse_args(argv)

    manifest = load_manifest(MANIFEST_PATH)
    current = PAGE_PATH.read_text(encoding="utf-8")
    rendered = render_page(manifest, current)

    if args.check:
        if rendered != current:
            sys.stderr.write(
                f"{PAGE_PATH} is out of date with {MANIFEST_PATH}.\n"
                "Run: python3 docs/scripts/generate_compatibility.py\n"
            )
            return 1
        return 0

    if rendered != current:
        PAGE_PATH.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
