# Docs Hub Aggregation Contract (AAASM-3659)

This repository (`agent-assembly-docs`) is the **central documentation hub**. It
aggregates the documentation of every module into one static site, mounted under
stable subpaths, and deploys it to **`docs.agent-assembly.com`**:

```text
/                hub mdBook (index, concepts, guides, architecture, reference)
/core/           agent-assembly core docs        (mdBook; redirect -> /core/latest/)
/core/versions.json   channels + archived[] manifest for the core version selector
/core/latest/         core docs, latest (master) channel
/core/<tag>/          frozen core docs, one per release git tag (full archived set)
/python-sdk/     python-sdk docs                 (mkdocs-material + mike, full version tree)
/python-sdk/versions.json   mike manifest; per-version dirs + latest/stable/pre-release
/node-sdk/       node-sdk docs                   (Docusaurus, in node-sdk/website/)
/go-sdk/         go-sdk docs                      (Hugo + Hextra; redirect -> /go-sdk/latest/)
/go-sdk/latest/       go docs, latest (master) channel
/go-sdk/<tag>/        frozen go docs, one per release git tag (full archived set)
/pagefind/       unified search index            (Pagefind over the final public/)
```

Each module's **per-version switcher** works in the hub because the hub now
publishes the version machinery each switcher needs under `/<module>/` — the
manifest **and** the version/channel subpaths it references (AAASM-3752). See
"Versioning" below.

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
| core | `ai-agent-assembly/agent-assembly` | mdBook | `docs/` | `mdbook build -d <out>/latest`, then rebuild **every** `v*.*.*` git tag into `<out>/<tag>/`, then `docs/ci/build_versions.py latest latest <out>/versions.json` + `docs/site-root-index.html` → `<out>/index.html` — `latest` + every archived tag under `/core/<tag>/`, manifest at `/core/versions.json`, root redirect; emits **root-relative** assets so it is subpath-safe. The moving pre-release/stable channel pointers are derived **hermetically** from the rebuilt git tags (via the repo's own `docs/ci/channels.py`), not fetched over the network (AAASM-3757) |
| python-sdk | `ai-agent-assembly/python-sdk` | mkdocs-material + mike | `.` (gh-pages) | clone the **`gh-pages`** branch and `cp -RL` it into `<out>` — reuses the full mike version tree (`versions.json` + per-version dirs + aliases); no `mkdocs build` is run, the published layout already matches `/python-sdk/` |
| node-sdk | `ai-agent-assembly/node-sdk` | Docusaurus | `website/` | `pnpm install --ignore-workspace && pnpm build` — `baseUrl` already `/node-sdk/` → absolute assets land under `/node-sdk/`; the version dropdown ships baked-in from committed `versioned_docs/` |
| go-sdk | `ai-agent-assembly/go-sdk` | Hugo+Hextra | `website/` | recompute `data/versions.toml` from git tags (via the repo's `versions_channels.py`), then `PAGES_BASE=/go-sdk … bash website/scripts/build_all_versions.sh` + render `website/redirect/index.html` → `<out>/index.html` — `latest` + moving channels + **every archived tag** under `/go-sdk/<tag>/`, root redirect; assets absolute under `/go-sdk/<channel-or-tag>/` matching `versionsBasePath` |

## Build / copy contract

[`docs/scripts/aggregate.sh`](./docs/scripts/aggregate.sh) is the executable
contract; the workflow ([`.github/workflows/aggregate.yml`](./.github/workflows/aggregate.yml))
just installs the toolchains and runs it. Steps:

1. **Build the hub mdBook first** into `public/` (root). mdBook *cleans* its
   output dir, so it must run before the module subdirs are populated.
2. For each registry entry: clone `repo@ref` (full history — generators read
   `git log` for "last updated"), build with its generator into
   `public/<subpath>/`, applying the base-URL strategy above. python-sdk is the
   exception: instead of a source build it clones the module's `gh-pages` branch
   and copies the already-published mike version tree.
3. Write `public/CNAME` = `docs.agent-assembly.com`.
4. **Verify** every expected dir (`public/`, `public/core/`, `public/python-sdk/`,
   `public/node-sdk/`, `public/go-sdk/`) exists, has a non-empty `index.html`,
   and contains ≥1 HTML file. **The build FAILS** if any module's output is
   missing or empty, or if any module build errored (`set -euo pipefail`).
   This is the Epic acceptance gate. The verify step **also** asserts the
   version-switcher machinery is present (AAASM-3752): `public/python-sdk/versions.json`,
   `public/core/versions.json`, `public/core/latest/index.html`, and
   `public/go-sdk/latest/index.html` — so a regression that drops a module's
   version tree fails the build instead of shipping a 404ing dropdown. It further
   asserts the **archived version sets** (AAASM-3753, hardened in AAASM-3757):
   each module's build records the tags that **must** produce a snapshot in an
   `expected-archived.txt` count-floor (core: every release tag that ships docs;
   go-sdk: every valid semver tag, identical to `archived[]` in `versions.toml`),
   and the gate **fails the build if any expected tag's `/<tag>/index.html` is
   missing**. This catches a *partial* set (a multi-tag rebuild where some tags
   built and others were silently dropped), not merely an empty one — so a
   truncated dropdown can never ship.
5. Run **Pagefind** over the final `public/`, **scoped to each module's default
   channel** (the archived version dirs are moved aside during indexing and
   restored after — see Search), and assert it produced `public/pagefind/pagefind.js`.

## Base-URL strategy

Base paths are handled **entirely at build time in the aggregation** — we do
**not** commit subpath config into the four SDK repos. Per generator:

- **mdBook** (hub, core): emits root-relative paths → works under any prefix, no
  flag needed. The core version selector derives the site root from `path_to_root`
  at runtime, so it resolves `/core/versions.json` correctly from `/core/latest/`
  and from every frozen `/core/<tag>/` snapshot.
- **mkdocs-material + mike** (python-sdk): the `gh-pages` tree is reused verbatim;
  its layout (gh-pages root == `/python-sdk/`) is byte-for-byte the layout the
  standalone site serves, so the relative asset paths and the mike version
  dropdown resolve unchanged. Alias symlinks are dereferenced (`cp -RL`) because
  GitHub Pages does not follow symlinks.
- **Docusaurus** (node-sdk): `baseUrl` is already `/node-sdk/`, so its absolute
  asset URLs (`/node-sdk/assets/...`) resolve correctly when copied to
  `public/node-sdk/`.
- **Hugo+Hextra** (go-sdk): `build_all_versions.sh` builds each channel/tag with
  `--baseURL /go-sdk/<subpath>/`, so assets are absolute under that subpath; the
  selector's `versionsBasePath=/go-sdk` links (`/go-sdk/latest/`, `/go-sdk/<tag>/`,
  …) resolve in the hub exactly as on the standalone site. Because the dropdown is
  baked at build time from `data/versions.toml`, that file is recomputed from git
  tags (via the repo's `versions_channels.py`) **before** the build. The channel
  *logic* is reused from `versions_channels.py` and cannot drift; the TOML
  *serializer* is a hand-kept mirror of go-sdk's `docs-site.yml` (go-sdk exposes
  no reusable serializer script), so `aggregate.sh` parse-checks the recomputed
  `versions.toml` with `tomllib` and fails loudly if the mirror drifts into
  malformed output (AAASM-3757).

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

**Default-channel scoping (AAASM-3753):** now that core, go-sdk, and python-sdk
each publish their **full** archived version set, indexing every version dir would
return N near-duplicate hits per page (one per archived version). Pagefind exposes
only a single inclusion `--glob` (no path negation/union), so `aggregate.sh`
temporarily **moves the non-default version dirs aside** (core: `archived[]` from
its manifest; go-sdk: every `v*` tag dir + `stable`/`pre-release`; python-sdk:
every version + alias dir from its mike manifest — all keeping `latest`), runs
Pagefind, then **restores** them (via an `EXIT` trap so they return even if
indexing fails). Search therefore covers each module's current docs only; the
archived snapshots remain fully served and reachable through the switcher.

## Versioning (AAASM-3752 / AAASM-3753 — per-module version switcher in the hub)

Each module ships its **own** per-version switcher (mike dropdown, Docusaurus
dropdown, or a channel selector). The first aggregation cut built only a flat
default-channel page per module and dropped the version machinery, so the
switchers 404'd on `docs.agent-assembly.com` while still working on the
standalone `*.github.io` sites. AAASM-3752 restored the machinery; AAASM-3753
extended core and go-sdk to the **full** archived version set so every module's
hub switcher now matches its standalone site:

| Module | Mechanism | What the switcher lists in the hub |
|---|---|---|
| python-sdk | **Reuse** the `gh-pages` mike tree verbatim | the **full** version set (latest, stable, every alpha/beta, pre-release) — identical to the standalone site |
| core | **Build** `master` HEAD into `/core/latest/` **and rebuild every release git tag** into `/core/<tag>/`, then compute `versions.json` via the repo's `docs/ci/build_versions.py` + root redirect | the **full** version set (latest, pre-release/stable channels, every archived tag) |
| go-sdk | **Recompute** `data/versions.toml` from git tags (via the repo's `versions_channels.py`), then **run** `build_all_versions.sh` to materialise `/go-sdk/<tag>/` for every entry + root redirect | the **full** version set (latest, pre-release/stable channels, every archived tag) |
| node-sdk | unchanged — dropdown baked in from committed `versioned_docs/` | the committed versions |

**git is the source of truth.** python-sdk keeps a persistent `gh-pages` branch
holding its entire mike tree, so the full set is reused for free. core and go-sdk
publish via a deploy-time GitHub Pages artifact (no persistent versioned branch):
their committed `versions.json` / `versions.toml` describe only the `latest`
channel, and the moving channels + archived tag list are computed by the **release
job from git tags** and live only on the deployed artifact. AAASM-3753 reproduces
that in the hub by doing exactly what each module's deploy job does — rebuilding
every release **git tag** (the core deploy abandoned mirroring the live Pages site
in AAASM-2827 because it was lossy; the hub follows suit). The per-tag rebuild is
self-healing: a tag that exists in git is recovered even if its standalone deploy
never published. core's moving `pre-release`/`stable` channel pointers are derived
**hermetically from the rebuilt git tags** — newest stable and newest pre-release,
selected with core's own semver logic (`docs/ci/channels.py`) and gated by
`build_versions.py` — so the hub has **no build-time network dependency** and a
channel can only ever point at a tag the hub actually rebuilt (AAASM-3757). This
replaces the earlier non-hermetic `curl` of the deployed `versions.json`, which
was silently non-fatal and could ship stale or empty pointers. No change to any
module repo's deploy workflow was required — the hub reuses each repo's own build
scripts.

## Deploy / custom domain

The workflow deploys the combined `public/` to GitHub Pages today (proof). The
`CNAME` file pins `docs.agent-assembly.com`; **the DNS / custom-domain attachment
is owner-gated** — once the owner points the domain at GitHub Pages and attaches
it in repo settings, the same artifact serves at `docs.agent-assembly.com`.
