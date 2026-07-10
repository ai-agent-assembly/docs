"""Render the docs hub's component tables/lists from ``hub-components.toml``.

This script is the one-way bridge between ``hub-components.toml`` (the human-edited
source of truth for hub component metadata) and the hand-authored pages under
``docs/src/`` that surface component names, hub subpaths, GitHub repo links,
standalone documentation URLs, and per-component build generators.

It reads the manifest with the standard-library ``tomllib`` (no third-party
dependency, matching ``generate_compatibility.py``), renders one generated block
per target page, and splices each into the target Markdown between its dedicated
``<!-- BEGIN GENERATED:hub-components:<key> -->`` / ``<!-- END GENERATED:hub-components:<key> -->``
markers so the hand-written prose is preserved.

Target pages (in the order they are updated):

* ``docs/src/README.md``       -> the landing-page version badges AND the
                                  "SDKs & components" table
* ``docs/src/documentation.md`` -> the Core + SDKs router lists
* ``docs/src/docs-hub-aggregation.md`` -> the Path / Module / Generator table
* ``docs/src/source-of-truth.md`` -> the canonical status map

Run it with no arguments to regenerate the pages in place. Run it with
``--check`` to verify the committed pages already match the manifest (used by
CI to fail on drift). The rendering is deterministic and idempotent: running it
twice produces byte-identical output.

See AAASM-4313 (Epic AAASM-4309) for the design rationale.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Final

# Repo layout: this file lives at docs/scripts/, the manifest at the repo root,
# and the rendered pages at docs/src/. Match the convention used by
# generate_compatibility.py.
SCRIPT_DIR: Final[Path] = Path(__file__).resolve().parent
REPO_ROOT: Final[Path] = SCRIPT_DIR.parent.parent
MANIFEST_PATH: Final[Path] = REPO_ROOT / "hub-components.toml"
SRC_DIR: Final[Path] = REPO_ROOT / "docs" / "src"

README_PATH: Final[Path] = SRC_DIR / "README.md"
DOCUMENTATION_PATH: Final[Path] = SRC_DIR / "documentation.md"
AGGREGATION_PAGE_PATH: Final[Path] = SRC_DIR / "docs-hub-aggregation.md"
SOURCE_OF_TRUTH_PATH: Final[Path] = SRC_DIR / "source-of-truth.md"


def _marker(key: str, kind: str) -> str:
    """Return the exact BEGIN/END marker string for a generated block.

    Marker shape: ``<!-- BEGIN GENERATED:hub-components:<key> -->`` /
    ``<!-- END GENERATED:hub-components:<key> -->``. The ``hub-components``
    namespace segment lets these coexist with the ``matrix`` / ``notes`` /
    ``requirements`` markers used by ``generate_compatibility.py``.
    """
    return f"<!-- {kind} GENERATED:hub-components:{key} -->"


def load_manifest(path: Path) -> dict[str, object]:
    """Read and parse the TOML manifest at ``path`` into a plain dictionary."""
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _components(manifest: dict[str, object]) -> list[dict[str, object]]:
    """Return the ``[[component]]`` array, validating its shape."""
    components = manifest.get("component", [])
    if not isinstance(components, list):
        raise TypeError("manifest key 'component' must be an array of tables")
    for entry in components:
        if not isinstance(entry, dict):
            raise TypeError("each [[component]] entry must be a table")
    _validate_components(components)
    return components


REQUIRED_KEYS: Final[tuple[str, ...]] = (
    "key",
    "display_name",
    "short_name",
    "repo",
    "repo_label",
    "docs_path",
    "docs_label",
    "standalone_url",
    "generator",
    "aggregated",
)


def _validate_components(components: list[dict[str, object]]) -> None:
    """Enforce required fields and unique keys.

    The generator refuses to render a manifest that is missing a field or that
    contains duplicate ``key`` entries — silent skips would produce a stale doc
    that CI's drift check still passes, which is precisely the failure mode
    AAASM-4313 exists to prevent.
    """
    seen: set[str] = set()
    for entry in components:
        for required in REQUIRED_KEYS:
            if required not in entry:
                raise ValueError(
                    f"component entry is missing required key {required!r}: {entry!r}"
                )
        key = str(entry["key"])
        if key in seen:
            raise ValueError(f"duplicate component key: {key!r}")
        seen.add(key)
        # An aggregated component must declare where it mounts; a non-aggregated
        # pointer must not (its docs_path is intentionally blank).
        aggregated = bool(entry["aggregated"])
        docs_path = str(entry["docs_path"])
        if aggregated and not docs_path:
            raise ValueError(
                f"aggregated component {key!r} must set a non-empty 'docs_path'"
            )
        if not aggregated and docs_path:
            raise ValueError(
                f"non-aggregated component {key!r} must leave 'docs_path' blank"
            )


def _aggregated(components: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return only the components that participate in hub aggregation."""
    return [c for c in components if bool(c["aggregated"])]


def _escape_cell(value: str) -> str:
    """Escape a string so it is safe inside a Markdown table cell.

    Pipes would otherwise be read as column separators; everything else is left
    verbatim so provenance notes render as written.
    """
    return value.replace("|", "\\|")


def _repo_url(repo: str) -> str:
    """Return the full https URL for a bare ``owner/repo`` reference."""
    return f"https://github.com/{repo}"


# ---------------------------------------------------------------------------
# Renderers — one per generated block. Each returns a string that will be
# spliced between the block's BEGIN/END markers with surrounding blank lines.
# ---------------------------------------------------------------------------


def render_readme_components_table(manifest: dict[str, object]) -> str:
    """Render the "SDKs & components" table shown on ``docs/src/README.md``.

    Columns: Component | On this hub | Standalone site. Only aggregated
    components are listed here (non-aggregated pointers are surfaced elsewhere
    on the page).
    """
    components = _aggregated(_components(manifest))
    lines = [
        "| Component | On this hub | Standalone site |",
        "|---|---|---|",
    ]
    for entry in components:
        short = _escape_cell(str(entry["short_name"]))
        docs_label = _escape_cell(str(entry["docs_label"]))
        docs_path = str(entry["docs_path"])
        standalone = str(entry["standalone_url"])
        key = str(entry["key"])
        # The README renders `core` as `[core docs](...)` for the standalone
        # column and each other component as a bare autolink `<url>`. Preserve
        # that distinction so this generated block matches the current page's
        # visual style verbatim.
        if key == "core":
            standalone_cell = f"[core docs]({standalone})"
        else:
            standalone_cell = f"<{standalone}>"
        lines.append(
            f"| {short} | [{docs_label}]({docs_path}) | {standalone_cell} |"
        )
    return "\n".join(lines)


def render_documentation_lists(manifest: dict[str, object]) -> str:
    """Render the Core + SDKs router content on ``docs/src/documentation.md``.

    The existing page splits its content into two H2 sections ("Core" and
    "SDKs"). Emit both sections inside a single generated block so the whole
    router stays in sync with the manifest, and the surrounding prose (intro
    and blockquote) stays hand-authored.
    """
    components = _aggregated(_components(manifest))
    core = [c for c in components if str(c["key"]) == "core"]
    sdks = [c for c in components if str(c["key"]) != "core"]

    lines: list[str] = ["## Core", ""]
    for entry in core:
        # Core's list entry cites the repo NAME as the link text (matching the
        # current hand-authored line: "**[agent-assembly](.../core/)** — ...").
        repo_label = str(entry["repo_label"])
        standalone = str(entry["standalone_url"])
        lines.append(
            f"- **[{repo_label}]({standalone})** — the core monorepo: gateway, "
            "policy engine, eBPF sensor, sidecar proxy, FFI, WASM, CLI, and API."
        )

    lines.extend(["", "## SDKs", ""])
    # Language phrasing per SDK — hand-authored today ("install and govern
    # agents from Python" / "TypeScript or JavaScript" / "Go"). Keep those
    # exact phrasings under the manifest's control by deriving them from the
    # component key so a new SDK gets a predictable default and existing rows
    # render byte-identically to the current page.
    sdk_language: dict[str, str] = {
        "python-sdk": "Python",
        "node-sdk": "TypeScript or JavaScript",
        "go-sdk": "Go",
    }
    for entry in sdks:
        key = str(entry["key"])
        short = str(entry["short_name"])
        standalone = str(entry["standalone_url"])
        language = sdk_language.get(key, short)
        lines.append(
            f"- **[{short}]({standalone})** — install and govern agents from "
            f"{language}."
        )

    return "\n".join(lines)


def render_aggregation_table(manifest: dict[str, object]) -> str:
    """Render the Path / Module / Generator table on ``docs-hub-aggregation.md``.

    The first row is the hub itself (mdBook at ``/``); every subsequent row is
    an aggregated component mounted under its ``docs_path``.
    """
    components = _aggregated(_components(manifest))
    lines = [
        "| Path | Module | Generator |",
        "|---|---|---|",
        "| `/` | This hub | mdBook |",
    ]
    for entry in components:
        docs_path = str(entry["docs_path"])
        docs_label = str(entry["docs_label"])
        repo_label = str(entry["repo_label"])
        generator = str(entry["generator"])
        key = str(entry["key"])
        # The existing table distinguishes core ("agent-assembly (core
        # monorepo)") from the SDKs (bare repo name). Preserve that phrasing
        # so the generated output matches the current page verbatim.
        if key == "core":
            module_cell = f"`{repo_label}` (core monorepo)"
        else:
            module_cell = f"`{repo_label}`"
        lines.append(
            f"| [`{docs_label}`]({docs_path}) | {module_cell} | {generator} |"
        )
    return "\n".join(lines)


def render_landing_badges(manifest: dict[str, object]) -> str:
    """Render the version-badge block at the top of ``docs/src/README.md``.

    Each aggregated component has one shields.io version badge that reads its
    latest published version live (GitHub releases for core and Go, PyPI for
    Python, npm's ``rc`` dist-tag for Node). The badge image URL and the
    trailing link URL vary per registry, so both are looked up by ``key`` here
    rather than derived from generic manifest fields — a new component in
    ``hub-components.toml`` will not silently gain a badge until an entry is
    added below.

    The license badge points at the hub's own repository (not a component) and
    is emitted here as a literal trailing line. It sits inside the block so the
    five badges stay in a single Markdown paragraph and render as one contiguous
    row of images, matching the current page byte-for-byte.
    """
    components = _aggregated(_components(manifest))
    # Per-component badge image URL and target URL. Keys must match the
    # manifest's component keys. Missing keys are skipped, matching the
    # behaviour of the source-of-truth renderer.
    badge: dict[str, tuple[str, str]] = {
        "core": (
            "https://img.shields.io/github/v/release/ai-agent-assembly/"
            "agent-assembly?include_prereleases&sort=semver&label=core&"
            "logo=github&color=3b82f6",
            "https://github.com/ai-agent-assembly/agent-assembly/releases",
        ),
        "python-sdk": (
            "https://img.shields.io/pypi/v/agent-assembly?label=python-sdk&"
            "logo=pypi",
            "https://github.com/ai-agent-assembly/python-sdk",
        ),
        "node-sdk": (
            "https://img.shields.io/npm/v/@agent-assembly/sdk/rc?"
            "label=node-sdk&logo=npm",
            "https://github.com/ai-agent-assembly/node-sdk",
        ),
        "go-sdk": (
            "https://img.shields.io/github/v/tag/ai-agent-assembly/go-sdk?"
            "sort=semver&label=go-sdk&logo=go&color=3b82f6",
            "https://github.com/ai-agent-assembly/go-sdk/tags",
        ),
    }
    lines: list[str] = []
    for entry in components:
        key = str(entry["key"])
        if key not in badge:
            continue
        img, target = badge[key]
        lines.append(f"[![{key}]({img})]({target})")
    # Trailing hub-owned license badge — kept inside the block as a literal
    # line so all five badges stay in one Markdown paragraph.
    lines.append(
        "[![license]("
        "https://img.shields.io/badge/license-Apache--2.0-green)]("
        "https://github.com/ai-agent-assembly/docs/blob/main/LICENSE)"
    )
    return "\n".join(lines)


def render_source_of_truth_table(manifest: dict[str, object]) -> str:
    """Render the full canonical status map table on ``source-of-truth.md``.

    The status map is a 5-column Markdown table (Area | Owning repository |
    Visibility | Maturity | Where to read). Its first block of rows lists the
    hub components — Core, the three SDKs, runnable examples, and the Homebrew
    tap — and is driven by ``hub-components.toml``. The remaining rows (Specs,
    Releases, Cloud, Enterprise, Operations) are non-component narrative areas
    that reference the monorepo indirectly or carry Private/Planned status not
    represented in the component schema; they are emitted verbatim so that the
    single visible table on the page stays intact.

    The whole table — header, separator, component rows, and narrative rows —
    is emitted here so the BEGIN/END GENERATED markers can wrap the table as a
    block (a Markdown table split by an HTML-comment marker inside would be
    parsed as two separate blocks and stop rendering as a table). Per-row Area
    phrasing and the "Where to read" cell for component rows vary
    per-component, so both are looked up by ``key`` from small tables here.
    The result is byte-identical to the hand-authored table it replaces.
    """
    components = _components(manifest)
    # Per-component overrides. Only components with rows in this page appear.
    area_label: dict[str, str] = {
        "core": "**Core** (gateway, policy engine, eBPF, proxy, FFI, WASM, CLI, API)",
        "python-sdk": "**Python SDK**",
        "node-sdk": "**Node / TypeScript SDK**",
        "go-sdk": "**Go SDK**",
        "examples": "**Runnable examples**",
        "homebrew-tap": "**Homebrew / install channel**",
    }
    # "Where to read" cell — SDKs cite their docs site as `<key> docs`, core
    # cites `core docs`, and the non-aggregated pointers fall back to their
    # repo README. Preserve the current page's exact phrasing.
    where_docs_label: dict[str, str] = {
        "core": "core docs",
        "python-sdk": "python-sdk docs",
        "node-sdk": "node-sdk docs",
        "go-sdk": "go-sdk docs",
    }

    lines: list[str] = [
        "| Area | Owning repository | Visibility | Maturity | Where to read |",
        "|---|---|---|---|---|",
    ]
    for entry in components:
        key = str(entry["key"])
        if key not in area_label:
            # Skip any future component that has not been given an explicit
            # row phrasing here; the source-of-truth page keeps its narrative
            # rows hand-authored and does not silently gain new rows.
            continue
        repo = str(entry["repo"])
        repo_label = str(entry["repo_label"])
        standalone = str(entry["standalone_url"])
        area = area_label[key]
        repo_cell = f"[`{repo_label}`]({_repo_url(repo)})"
        if key in where_docs_label:
            where_cell = f"[{where_docs_label[key]}]({standalone})"
        else:
            where_cell = "repo `README`"
        lines.append(
            f"| {area} | {repo_cell} | 🟢 Public | 🧪 Release candidate | "
            f"{where_cell} |"
        )
    # Non-component narrative rows — kept as literal lines because they either
    # reference the monorepo indirectly ("agent-assembly monorepo") or describe
    # areas (Cloud, Enterprise, Operations) that are Private/internal and/or
    # Planned rather than public and release-track. Editing these lines is a
    # hand-edit in this file (they are not driven by hub-components.toml).
    lines.extend(
        [
            "| **Specs** (protocol & policy spec) | "
            "[`agent-assembly`](https://github.com/ai-agent-assembly/agent-assembly)"
            " monorepo | 🟢 Public | 🧪 Release candidate | "
            "[Policy reference](policy-reference.md) · core docs |",
            "| **Releases** (versions & compatibility) | "
            "this hub + each component's tags | 🟢 Public | "
            "🧪 Release candidate | [Compatibility matrix](compatibility.md) |",
            "| **Cloud** (SaaS control plane) | `cloud` | "
            "🔒 Private / internal | 🗺️ Planned | "
            "[Cloud deployment](cloud-deployment.md) |",
            "| **Enterprise** (SSO, SCIM, advanced audit) | "
            "`agent-assembly-enterprise` | 🔒 Private / internal | "
            "🗺️ Planned | [Open core boundary](open-core-boundary.md) |",
            "| **Operations** (running & onboarding) | this hub | "
            "🟢 Public | 🗺️ Planned | [Quick start (SaaS)](quickstart-saas.md) |",
        ]
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Splice + orchestration
# ---------------------------------------------------------------------------


def splice(page: str, begin: str, end: str, body: str) -> str:
    """Replace the content between ``begin`` and ``end`` markers in ``page``.

    The markers themselves are preserved; the body is surrounded by blank lines
    so a Markdown table renders correctly regardless of the surrounding prose.
    """
    start = page.find(begin)
    stop = page.find(end)
    if start == -1 or stop == -1 or stop < start:
        raise ValueError(f"markers {begin!r} / {end!r} not found (or out of order)")
    head = page[: start + len(begin)]
    tail = page[stop:]
    return f"{head}\n\n{body}\n\n{tail}"


def _render_page(page: Path, key: str, body: str) -> tuple[str, str]:
    """Return ``(current, rendered)`` for the target ``page`` and block ``key``."""
    current = page.read_text(encoding="utf-8")
    rendered = splice(current, _marker(key, "BEGIN"), _marker(key, "END"), body)
    return current, rendered


def _render_page_blocks(
    page: Path, blocks: list[tuple[str, str]]
) -> tuple[str, str]:
    """Return ``(current, rendered)`` for a page carrying multiple generated blocks.

    ``blocks`` is a list of ``(key, body)`` pairs — one per BEGIN/END marker
    pair on the page. Splices are applied sequentially against the running
    rendered string so that a page like docs/src/README.md can carry both the
    landing-badges block and the sdks-and-components block without one
    overwriting the other.
    """
    current = page.read_text(encoding="utf-8")
    rendered = current
    for key, body in blocks:
        rendered = splice(rendered, _marker(key, "BEGIN"), _marker(key, "END"), body)
    return current, rendered


def render_all(manifest: dict[str, object]) -> list[tuple[Path, str, str]]:
    """Return ``(path, current, rendered)`` for every managed page."""
    return [
        (
            README_PATH,
            *_render_page_blocks(
                README_PATH,
                [
                    ("landing-badges", render_landing_badges(manifest)),
                    (
                        "sdks-and-components",
                        render_readme_components_table(manifest),
                    ),
                ],
            ),
        ),
        (
            DOCUMENTATION_PATH,
            *_render_page(
                DOCUMENTATION_PATH,
                "router",
                render_documentation_lists(manifest),
            ),
        ),
        (
            AGGREGATION_PAGE_PATH,
            *_render_page(
                AGGREGATION_PAGE_PATH,
                "aggregation-table",
                render_aggregation_table(manifest),
            ),
        ),
        (
            SOURCE_OF_TRUTH_PATH,
            *_render_page(
                SOURCE_OF_TRUTH_PATH,
                "source-of-truth-table",
                render_source_of_truth_table(manifest),
            ),
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    """Entry point: regenerate the pages, or with ``--check`` verify freshness."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed pages match the manifest; exit nonzero if stale",
    )
    args = parser.parse_args(argv)

    manifest = load_manifest(MANIFEST_PATH)
    results = render_all(manifest)

    if args.check:
        stale = [path for path, current, rendered in results if current != rendered]
        if stale:
            sys.stderr.write(
                "Docs hub component metadata is out of date with "
                f"{MANIFEST_PATH.relative_to(REPO_ROOT)}:\n"
            )
            for path in stale:
                sys.stderr.write(f"  - {path.relative_to(REPO_ROOT)}\n")
            sys.stderr.write(
                "Run: python3 docs/scripts/generate_hub_components.py\n"
            )
            return 1
        return 0

    for path, current, rendered in results:
        if rendered != current:
            path.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
