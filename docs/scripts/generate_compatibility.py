"""Render the core<->SDK compatibility tables into the docs page from the manifest.

This script is the one-way bridge between ``compatibility.toml`` (the human-edited
source of truth) and ``docs/src/compatibility.md`` (the rendered page). It reads the
manifest with the standard-library ``tomllib`` (no third-party dependency), renders a
release matrix table and a per-SDK requirements table, and splices each into the
Markdown page between its dedicated ``BEGIN GENERATED`` / ``END GENERATED`` markers so
the hand-written prose and the live badge strip are preserved.

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
REQUIREMENTS_BEGIN: Final[str] = "<!-- BEGIN GENERATED:requirements -->"
REQUIREMENTS_END: Final[str] = "<!-- END GENERATED:requirements -->"

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


def render_matrix(manifest: dict[str, object]) -> str:
    """Render the per-core-release compatibility matrix as a Markdown table.

    Each row pairs one core release with the SDK release that speaks its wire
    protocol, plus the protocol contract, lifecycle status, and a provenance note.
    """
    releases = manifest.get("release", [])
    if not isinstance(releases, list):
        raise TypeError("manifest key 'release' must be an array of tables")

    header = (
        "| Core release | Status | Protocol | "
        + " | ".join(SDK_HEADERS[key] for key in SDK_KEYS)
        + " | Notes |"
    )
    separator = "|---|---|---|" + "---|" * len(SDK_KEYS) + "---|"

    lines: list[str] = [header, separator]
    for entry in releases:
        if not isinstance(entry, dict):
            raise TypeError("each [[release]] entry must be a table")
        sdks = entry.get("sdks", {})
        if not isinstance(sdks, dict):
            raise TypeError("each [release.sdks] entry must be a table")
        cells = [
            _escape_cell(str(entry.get("core", "—"))),
            _escape_cell(str(entry.get("status", "—"))),
            _escape_cell(str(entry.get("proto", "—"))),
        ]
        cells.extend(_escape_cell(str(sdks.get(key, "—"))) for key in SDK_KEYS)
        cells.append(_escape_cell(str(entry.get("notes", ""))))
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


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
    """Return the page text with both generated blocks refreshed from the manifest."""
    rendered = splice(current, MATRIX_BEGIN, MATRIX_END, render_matrix(manifest))
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
