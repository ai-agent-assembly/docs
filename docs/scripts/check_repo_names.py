"""Audit tracked docs prose/config for stale pre-rename repository names.

Hand-patching stale repo names one file at a time does not stop them coming
back: the 2026-07-09 org-wide rename (Epic AAASM-4341) is the third rename this
hub has absorbed, and every time a few references drift. This script turns that
recurring class of bug into a CI gate, mirroring the shared-metadata pattern the
``examples`` repo adopted in Epic AAASM-4718 (generator + orphan-literal
``--check``): the canonical repo names come from ``hub-components.toml`` (the same
manifest that drives the generated component tables), a small explicit alias map
records the dead old→new names the rename retired, and the audit fails the build
on any occurrence of a retired name in a tracked prose/config file.

Two checks run:

1. STALE REPO NAME — every retired old name in ``RENAME_ALIASES`` is searched
   for as a whole token across tracked ``.md`` / ``.toml`` / ``.json`` /
   ``.yml`` / ``.yaml`` / ``.hbs`` files, the ``CODEOWNERS`` file (which has no
   suffix), and the ``.po`` / ``.pot`` translation catalogs. Any hit fails,
   naming the replacement.
2. PROGRAM COUNT — prose that asserts "<N> independently[- ]versioned
   programs/components" must agree with the number of *aggregated* components in
   ``hub-components.toml`` (core + the SDKs + Arena). A count that drifts from the
   manifest (e.g. after a component is added) fails. Also scans ``.po``/``.pot``
   translation catalogs, so an extracted msgid left behind after a source-prose
   count change self-detects the same way a stale ``.md`` page would.

The canonical current names come from the manifest so a *new* rename only needs
the manifest updated plus one alias-map line here — the audit then keeps every
prose/config reference honest without another hand sweep.

Run with no arguments (or ``--check``; they are equivalent — this script never
edits files, it only reports) and it exits non-zero on any violation, printing
each ``path:line`` and the fix. Wire it into CI next to
``generate_hub_components.py --check``.

Exclusions are deliberate and narrow:
  * ``MIGRATION.md`` documents the real pre-rename URLs/names as history.
  * this script defines the alias map, so it necessarily contains old names.
  * ``agent-assembly-enterprise`` is NOT a retired name — it kept its prefix by
    design — so it is simply absent from the alias map and never flagged.

See AAASM-4742 (and the AAASM-4341 rename it stems from) for context.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Final

# Repo layout: this file lives at docs/scripts/, the manifest at the repo root.
# Match the convention used by generate_hub_components.py / generate_compatibility.py.
SCRIPT_DIR: Final[Path] = Path(__file__).resolve().parent
REPO_ROOT: Final[Path] = SCRIPT_DIR.parent.parent
MANIFEST_PATH: Final[Path] = REPO_ROOT / "hub-components.toml"

# The 2026-07-09 org-wide repo rename (Epic AAASM-4341) dropped the redundant
# ``agent-assembly-`` prefix from most repos and gave the E2E/internal repos
# clearer names. Each entry maps a now-DEAD old repo name to its current
# canonical name. ``agent-assembly-enterprise`` deliberately KEPT its prefix and
# is therefore intentionally absent — it must never be flagged.
RENAME_ALIASES: Final[dict[str, str]] = {
    "agent-assembly-cloud": "cloud",
    "agent-assembly-docs": "docs",
    "inner-document": "internal-docs",
    "agent-assembly-examples": "examples",
    "agent-assembly-integration-tests": "e2e-public",
    "agent-assembly-private-e2e": "e2e-private",
}

# Files that legitimately contain an old name and must not trip the audit.
# Paths are repo-root-relative POSIX strings.
EXCLUDED_PATHS: Final[frozenset[str]] = frozenset(
    {
        "MIGRATION.md",  # documents the actual pre-rename URLs/names as history
        "docs/scripts/check_repo_names.py",  # defines the alias map above
    }
)

# Prose + config extensions the rename touches. Binaries and source that never
# names a repo (e.g. CSS) are skipped. ``.hbs`` is the mdBook theme template
# surface (e.g. docs/theme/head.hbs) — it embeds repo names in URLs/analytics
# config and was previously unswept (AAASM-4943).
SCANNED_SUFFIXES: Final[frozenset[str]] = frozenset(
    {".md", ".toml", ".json", ".yml", ".yaml", ".hbs"}
)

# Suffix-less tracked files that still name repos and must be swept. ``CODEOWNERS``
# routes review by ``@org/team`` and repo path, so a retired name there silently
# misroutes reviews; matched by exact filename since it has no suffix (AAASM-4943).
SCANNED_FILENAMES: Final[frozenset[str]] = frozenset({"CODEOWNERS"})

# gettext translation catalogs. Kept out of SCANNED_SUFFIXES because they are
# discovered separately (see ``tracked_po_files``), but as of AAASM-4943 they are
# swept for stale repo names too, and the program-count assertion — which gets
# duplicated verbatim into extracted msgid strings — also checks them, so a
# catalog regenerated before a source-prose edit lands (or never re-synced after
# one) drifts out of date self-detectably (AAASM-4791).
PO_SUFFIXES: Final[frozenset[str]] = frozenset({".po", ".pot"})

# English number words the program-count prose uses, mapped to their integer.
COUNT_WORDS: Final[dict[str, int]] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

# Match "<number-word> independently[- ]versioned" (the phrasing the hub uses to
# assert how many independently versioned programs/components ship). Only an
# explicit count is checked; vaguer phrasings ("several independently versioned")
# are intentionally not constrained.
COUNT_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(" + "|".join(COUNT_WORDS) + r")\s+independently[- ]versioned",
    re.IGNORECASE,
)


def _alias_pattern(old: str) -> re.Pattern[str]:
    """Compile a whole-token matcher for a retired repo name.

    The name must not be flanked by another identifier character (alphanumeric,
    underscore, or hyphen) so ``agent-assembly-docs`` does not match inside
    ``agent-assembly-docstore`` and the retired names never collide with the
    still-valid ``agent-assembly`` core repo or the ``ai-agent-assembly`` org.
    """
    return re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(old) + r"(?![A-Za-z0-9_-])")


def load_manifest(path: Path) -> dict[str, object]:
    """Read and parse the TOML manifest at ``path`` into a plain dictionary."""
    with path.open("rb") as handle:
        return tomllib.load(handle)


def aggregated_component_count(manifest: dict[str, object]) -> int:
    """Return the number of aggregated components (the independently versioned programs).

    Non-aggregated pointers (the examples repo, the Homebrew tap) are link-only
    entries, not independently versioned programs with their own docs site, so
    they are excluded from the count the prose asserts.
    """
    components = manifest.get("component", [])
    if not isinstance(components, list):
        raise TypeError("manifest key 'component' must be an array of tables")
    return sum(1 for c in components if isinstance(c, dict) and bool(c.get("aggregated")))


def tracked_files() -> list[Path]:
    """Return repo-tracked files to sweep, excluding EXCLUDED_PATHS.

    A file is swept if its suffix is in ``SCANNED_SUFFIXES`` or its bare filename
    is in ``SCANNED_FILENAMES`` (for suffix-less files like ``CODEOWNERS``).
    """
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    files: list[Path] = []
    for rel in out.split("\0"):
        if not rel:
            continue
        if rel in EXCLUDED_PATHS:
            continue
        path = REPO_ROOT / rel
        if path.suffix.lower() in SCANNED_SUFFIXES or path.name in SCANNED_FILENAMES:
            files.append(path)
    return files


def tracked_po_files() -> list[Path]:
    """Return repo-tracked ``.po``/``.pot`` translation catalogs.

    Deliberately separate from ``tracked_files()``: these live outside
    ``SCANNED_SUFFIXES`` and are discovered here, then fed into *both* audits by
    ``main`` — the stale-repo-name audit (a retired name copied into an msgid) and
    ``audit_program_count`` (a catalog whose msgid drifted behind the source
    prose it was extracted from).
    """
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    files: list[Path] = []
    for rel in out.split("\0"):
        if not rel:
            continue
        path = REPO_ROOT / rel
        if path.suffix.lower() in PO_SUFFIXES:
            files.append(path)
    return files


def audit_stale_names(files: list[Path]) -> list[str]:
    """Return one violation string per retired-name occurrence found in ``files``."""
    patterns = {old: _alias_pattern(old) for old in RENAME_ALIASES}
    violations: list[str] = []
    for path in files:
        rel = path.relative_to(REPO_ROOT).as_posix()
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for old, pattern in patterns.items():
                if pattern.search(line):
                    violations.append(
                        f"{rel}:{lineno}: stale repo name {old!r} "
                        f"(renamed to {RENAME_ALIASES[old]!r} in AAASM-4341)"
                    )
    return violations


def audit_program_count(files: list[Path], expected: int) -> list[str]:
    """Return one violation string per prose count that disagrees with ``expected``.

    ``files`` may include ``.po``/``.pot`` catalogs alongside ``.md`` pages: a
    gettext msgid line carries the full sentence verbatim (e.g. ``"...composed
    of four independently versioned..."``), so the same line-level regex catches
    a catalog that fell behind a source-prose count change.
    """
    violations: list[str] = []
    for path in files:
        if path.suffix.lower() not in {".md", *PO_SUFFIXES}:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for match in COUNT_RE.finditer(line):
                stated = COUNT_WORDS[match.group(1).lower()]
                if stated != expected:
                    violations.append(
                        f"{rel}:{lineno}: prose asserts {match.group(1)!r} "
                        f"independently versioned programs, but hub-components.toml "
                        f"has {expected} aggregated components"
                    )
    return violations


def main(argv: list[str] | None = None) -> int:
    """Run both audits; exit non-zero (with a report) on any violation."""
    # --check is accepted for symmetry with the sibling generators, but this
    # script is read-only either way, so the flag is a no-op.
    manifest = load_manifest(MANIFEST_PATH)
    expected = aggregated_component_count(manifest)
    files = tracked_files()
    po_files = tracked_po_files()

    violations = audit_stale_names(files + po_files) + audit_program_count(
        files + po_files, expected
    )
    if violations:
        sys.stderr.write(
            "Stale pre-rename repo-name audit failed "
            f"({len(violations)} violation(s)):\n"
        )
        for violation in violations:
            sys.stderr.write(f"  - {violation}\n")
        sys.stderr.write(
            "Update the reference to the current name "
            "(canonical names live in hub-components.toml; retired names in "
            "docs/scripts/check_repo_names.py RENAME_ALIASES). MIGRATION.md is "
            "exempt as intentional history.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
