# Docs Hub Aggregation Contract (AAASM-3659)

This repository (`agent-assembly-docs`) is the **central documentation hub**. It
aggregates the documentation of every module into one static site, mounted under
stable subpaths, and deploys it to **`docs.agent-assembly.com`**:

```text
/                hub mdBook (index, concepts, guides, architecture, reference)
/core/           agent-assembly core docs        (mdBook)
/python-sdk/     python-sdk docs                 (mkdocs-material)
/node-sdk/       node-sdk docs                   (Docusaurus, in node-sdk/website/)
/go-sdk/         go-sdk docs                      (Hugo + Hextra, in go-sdk/website/)
/pagefind/       unified search index            (Pagefind over the final public/)
```

## Why pull/aggregate (not one generator)

Each module already ships a polished, generator-specific docs site (mdBook,
mkdocs-material, Docusaurus, Hugo+Hextra) with its own versioning, theming, and
release wiring. We do **not** force them onto one generator. Instead the hub
**pulls** each module, builds it with **its own toolchain** under the correct
subpath base URL, and assembles the outputs into one `public/` tree. This keeps
each module's standalone site untouched and lets the hub evolve independently.

## Module registry

The single source of truth is [`modules.json`](./modules.json). Each entry:

| Field | Meaning |
|---|---|
| `name` | logical id (used for the local checkout dir) |
| `repo` | `owner/repo` on GitHub |
| `ref` | git ref to build (default channel = `master`/`main` HEAD; pin a tag/SHA to freeze a release line) |
| `generator` | `mdbook` \| `mkdocs-material` \| `docusaurus` \| `hugo-hextra` |
| `subpath` | mount point under the hub (`/core/`, `/python-sdk/`, …) |
| `doc_dir` | where the docs project lives inside the repo |
| `channel` | which version line is aggregated (see Versioning) |
| `base_url_strategy` | how the subpath base URL is applied for that generator |
| `build` | the build command |

The hub mdBook itself is built from **this** repo's `docs/` at the site root and
is not listed in the registry.

## Module → generator → build

| Module | Repo | Generator | Doc dir | Build (→ subpath base URL) |
|---|---|---|---|---|
| core | `ai-agent-assembly/agent-assembly` | mdBook | `docs/` | `cd docs && mdbook build -d <out>` — emits **root-relative** assets, subpath-safe with no flag |
| python-sdk | `ai-agent-assembly/python-sdk` | mkdocs-material | `.` | `uv sync --group docs && uv run mkdocs build --site-dir <out>` — relative assets; `site_url` already `/python-sdk/` |
| node-sdk | `ai-agent-assembly/node-sdk` | Docusaurus | `website/` | `pnpm install --ignore-workspace && pnpm build` — `baseUrl` already `/node-sdk/` → absolute assets land under `/node-sdk/` |
| go-sdk | `ai-agent-assembly/go-sdk` | Hugo+Hextra | `website/` | `hugo mod get github.com/imfing/hextra && hugo --gc --minify -b /go-sdk/ -d <out>` — `-b` makes root-relative assets resolve under `/go-sdk/` |

## Build / copy contract

[`docs/scripts/aggregate.sh`](./docs/scripts/aggregate.sh) is the executable
contract; the workflow ([`.github/workflows/aggregate.yml`](./.github/workflows/aggregate.yml))
just installs the toolchains and runs it. Steps:

1. **Build the hub mdBook first** into `public/` (root). mdBook *cleans* its
   output dir, so it must run before the module subdirs are populated.
2. For each registry entry: clone `repo@ref` (full history — generators read
   `git log` for "last updated"), build with its generator into
   `public/<subpath>/`, applying the base-URL strategy above.
3. Write `public/CNAME` = `docs.agent-assembly.com`.
4. **Verify** every expected dir (`public/`, `public/core/`, `public/python-sdk/`,
   `public/node-sdk/`, `public/go-sdk/`) exists, has a non-empty `index.html`,
   and contains ≥1 HTML file. **The build FAILS** if any module's output is
   missing or empty, or if any module build errored (`set -euo pipefail`).
   This is the Epic acceptance gate.
5. Run **Pagefind** over the final `public/` and assert it produced
   `public/pagefind/pagefind.js`.

## Base-URL strategy

Base paths are handled **entirely at build time in the aggregation** — we do
**not** commit subpath config into the four SDK repos. Per generator:

- **mdBook** (hub, core): emits root-relative paths → works under any prefix, no
  flag needed.
- **mkdocs-material** (python-sdk): emits relative asset paths; its `site_url` is
  already `/python-sdk/`, matching the subpath.
- **Docusaurus** (node-sdk): `baseUrl` is already `/node-sdk/`, so its absolute
  asset URLs (`/node-sdk/assets/...`) resolve correctly when copied to
  `public/node-sdk/`.
- **Hugo+Hextra** (go-sdk): pass `-b /go-sdk/`; Hugo then writes root-relative
  assets under `/go-sdk/...`.

If a generator ever needs a post-build path rewrite, do it in `aggregate.sh` /
the workflow — never in the module repo.

## Search

**Pagefind** runs over the **final aggregated `public/`**, indexing the built
HTML of every generator. This yields one **truly unified** index across the hub
and all four modules — we do not try to merge the four generators' native search
indexes. The hub injects a Pagefind UI search box (see `docs/theme/head.hbs`);
it searches the hub + core + python-sdk + node-sdk + go-sdk together. The Pagefind
assets live at `/pagefind/` (root-relative; the hub is at the site root). When the
hub is built standalone (the legacy `deploy.yml`, no aggregation), `/pagefind/` is
absent and the widget silently no-ops while the mdBook native search still works.

## Versioning decision (owner-default, can be overridden)

For the hub's canonical view we aggregate each module's **default channel** — the
**latest** line, built from `master`/`main` HEAD — at `/<module>/`. We deliberately
do **not** reproduce each module's per-version mike / Docusaurus / Hugo channel
trees inside the hub for this first cut. The per-module **standalone** sites keep
their full versioned channel browsing as-is (and the hub's component table links
out to them).

**Follow-up (not in this pass):** mount selected per-module version channels under
the hub (e.g. `/python-sdk/stable/`, `/node-sdk/next/`) by building multiple refs
per module and adding a hub-level version switcher. Tracked as a follow-up to
AAASM-3659.

## Deploy / custom domain

The workflow deploys the combined `public/` to GitHub Pages today (proof). The
`CNAME` file pins `docs.agent-assembly.com`; **the DNS / custom-domain attachment
is owner-gated** — once the owner points the domain at GitHub Pages and attaches
it in repo settings, the same artifact serves at `docs.agent-assembly.com`.
