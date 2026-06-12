#!/usr/bin/env python3
"""mdBook preprocessor that appends a per-page "Last updated" footer.

For each chapter that maps to a real source file, the chapter's last commit
date is read from git (``git log -1 --format=%cs``) and a footer is appended:

    ---

    *Last updated: <date> by AI Agent Assembly Team*

The committer is shown as the static team name "AI Agent Assembly Team"
(matching ``book.toml`` authors), never an individual contributor.

Protocol (https://rust-lang.github.io/mdBook/for_developers/preprocessors.html):

* ``<cmd> supports <renderer>`` -> exit 0 (this preprocessor supports every
  renderer).
* Otherwise read ``[context, book]`` JSON on stdin and write the modified
  ``book`` JSON to stdout.

mdBook serializes the chapter list under ``book["sections"]`` (0.4.x) or
``book["items"]`` (0.5.x); both are handled. Stdlib only.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

TEAM_NAME = "AI Agent Assembly Team"


def chapter_date(source_path: str) -> str | None:
    """Return the last commit date (YYYY-MM-DD) for ``src/<source_path>``.

    Returns ``None`` when the file has no git history or git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", f"src/{source_path}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    date = result.stdout.strip()
    return date or None


def process_chapter(chapter: dict[str, Any]) -> None:
    """Append the footer to one chapter, then recurse into its sub-items."""
    source_path = chapter.get("source_path") or chapter.get("path")
    if isinstance(source_path, str) and source_path:
        date = chapter_date(source_path)
        if date is not None:
            content = chapter.get("content", "")
            chapter["content"] = (
                f"{content}\n\n---\n\n*Last updated: {date} by {TEAM_NAME}*\n"
            )
    for item in chapter.get("sub_items", []):
        process_item(item)


def process_item(item: Any) -> None:
    """Process a single book item; only ``Chapter`` items carry content."""
    if isinstance(item, dict):
        chapter = item.get("Chapter")
        if isinstance(chapter, dict):
            process_chapter(chapter)


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "supports":
        return 0

    context_and_book = json.load(sys.stdin)
    _context, book = context_and_book
    items = book.get("items")
    if items is None:
        items = book.get("sections")
    if isinstance(items, list):
        for item in items:
            process_item(item)

    json.dump(book, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
