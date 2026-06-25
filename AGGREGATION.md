# Docs Hub Aggregation Contract (AAASM-3659)

This repository (`agent-assembly-docs`) is the **central documentation hub**. It
aggregates the documentation of every module into one static site, mounted under
stable subpaths, and deploys it to **`docs.agent-assembly.com`**:

```text
/                hub mdBook (index, concepts, guides, architecture, reference)
/core/           agent-assembly core docs        (mdBook; redirect -> /core/latest/)
/core/versions.json   channel manifest for the core version selector
/core/latest/         core docs, latest (master) channel
/python-sdk/     python-sdk docs                 (mkdocs-material + mike, full version tree)
/python-sdk/versions.json   mike manifest; per-version dirs + latest/stable/pre-release
/node-sdk/       node-sdk docs                   (Docusaurus, in node-sdk/website/)
/go-sdk/         go-sdk docs                      (Hugo + Hextra; redirect -> /go-sdk/latest/)
/go-sdk/latest/       go docs, latest (master) channel
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
| core | `ai-agent-assembly/agent-assembly` | mdBook | `docs/` | `mdbook build -d <out>/latest` + copy `docs/versions.json` → `<out>/versions.json` + `docs/site-root-index.html` → `<out>/index.html` — book under `/core/latest/`, manifest at `/core/versions.json`, root redirect; emits **root-relative** assets so it is subpath-safe |
| python-sdk | `ai-agent-assembly/python-sdk` | mkdocs-material + mike | `.` (gh-pages) | clone the **`gh-pages`** branch and `cp -RL` it into `<out>` — reuses the full mike version tree (`versions.json` + per-version dirs + aliases); no `mkdocs build` is run, the published layout already matches `/python-sdk/` |
| node-sdk | `ai-agent-assembly/node-sdk` | Docusaurus | `website/` | `pnpm install --ignore-workspace && pnpm build` — `baseUrl` already `/node-sdk/` → absolute assets land under `/node-sdk/`; the version dropdown ships baked-in from committed `versioned_docs/` |
| go-sdk | `ai-agent-assembly/go-sdk` | Hugo+Hextra | `website/` | `PAGES_BASE=/go-sdk … bash website/scripts/build_all_versions.sh` + render `website/redirect/index.html` → `<out>/index.html` — every channel in `data/versions.toml` under `/go-sdk/<channel>/`, root redirect; assets absolute under `/go-sdk/<channel>/` matching `versionsBasePath` |

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
   version tree fails the build instead of shipping a 404ing dropdown.
5. Run **Pagefind** over the final `public/` and assert it produced
   `public/pagefind/pagefind.js`.

## Base-URL strategy

Base paths are handled **entirely at build time in the aggregation** — we do
**not** commit subpath config into the four SDK repos. Per generator:

- **mdBook** (hub, core): emits root-relative paths → works under any prefix, no
  flag needed. The core version selector derives the site root from `path_to_root`
  at runtime, so it resolves `/core/versions.json` correctly from `/core/latest/`.
- **mkdocs-material + mike** (python-sdk): the `gh-pages` tree is reused verbatim;
  its layout (gh-pages root == `/python-sdk/`) is byte-for-byte the layout the
  standalone site serves, so the relative asset paths and the mike version
  dropdown resolve unchanged. Alias symlinks are dereferenced (`cp -RL`) because
  GitHub Pages does not follow symlinks.
- **Docusaurus** (node-sdk): `baseUrl` is already `/node-sdk/`, so its absolute
  asset URLs (`/node-sdk/assets/...`) resolve correctly when copied to
  `public/node-sdk/`.
- **Hugo+Hextra** (go-sdk): `build_all_versions.sh` builds each channel with
  `--baseURL /go-sdk/<channel>/`, so assets are absolute under that subpath; the
  selector's `versionsBasePath=/go-sdk` links (`/go-sdk/latest/`, …) resolve in
  the hub exactly as on the standalone site.

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

## Versioning (AAASM-3752 — per-module version switcher in the hub)

Each module ships its **own** per-version switcher (mike dropdown, Docusaurus
dropdown, or a channel selector). The first aggregation cut built only a flat
default-channel page per module and dropped the version machinery, so the
switchers 404'd on `docs.agent-assembly.com` while still working on the
standalone `*.github.io` sites. AAASM-3752 restores the machinery by publishing,
under each `/<module>/`, the manifest **and** the version/channel subpaths the
switcher references — reusing each module's already-published versioned output
where one exists:

| Module | Mechanism | What the switcher lists in the hub |
|---|---|---|
| python-sdk | **Reuse** the `gh-pages` mike tree verbatim | the **full** version set (latest, stable, every alpha/beta, pre-release) — identical to the standalone site |
| core | **Build** `master` HEAD into `/core/latest/` + copy committed `docs/versions.json` + root redirect | the channels in the committed manifest (default channel = `latest`) |
| go-sdk | **Run** the repo's `build_all_versions.sh` over committed `data/versions.toml` + root redirect | every channel in the committed manifest (default channel = `latest`) |
| node-sdk | unchanged — dropdown baked in from committed `versioned_docs/` | the committed versions |

**Why python is "full" but core/go are "default channel":** python-sdk keeps a
persistent `gh-pages` branch holding its entire mike tree, so the full set is
reused for free. core and agent-assembly publish via a deploy-time GitHub Pages
artifact (no persistent versioned branch); their committed `versions.json` /
`versions.toml` describe only the `latest` channel — the moving channels and
archived tag list are computed by the **release job** from git tags and live only
on the deployed artifact. Reproducing those in the hub would mean rebuilding every
historical tag, which is out of scope here. The switcher therefore lists exactly
the channels each module's committed manifest declares, and every listed target
resolves (no 404) — that is the AAASM-3752 acceptance bar.

**Follow-up (not in this pass):** mirror core/go archived tag snapshots into the
hub (rebuild each tag, or read the live deployed manifest) so their hub switchers
match python's full breadth. Also: Pagefind now indexes every python version dir,
so search may surface near-duplicate hits across versions — restrict the index to
the default channel if that becomes noisy.

## Deploy / custom domain

The workflow deploys the combined `public/` to GitHub Pages today (proof). The
`CNAME` file pins `docs.agent-assembly.com`; **the DNS / custom-domain attachment
is owner-gated** — once the owner points the domain at GitHub Pages and attaches
it in repo settings, the same artifact serves at `docs.agent-assembly.com`.
