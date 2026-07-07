# Contributing to agent-assembly-docs

Thanks for helping improve the **AI Agent Assembly documentation hub**. This repo
is an [mdBook](https://rust-lang.github.io/mdBook/) site, built and deployed to
GitHub Pages by [`aggregate.yml`](.github/workflows/aggregate.yml) on every push to
`main`. This guide covers how to add or edit pages, validate them locally, and open
a PR.

> New here? Read [`README.md`](README.md) first for what this repo is, the live
> site URL, and the local-development quickstart. This file is the deeper how-to.

## Prerequisites

The site builds with mdBook and two small helpers — no Node.js or npm is involved.

| Tool | Why | Install |
|---|---|---|
| [mdBook](https://rust-lang.github.io/mdBook/) (CI pins `v0.4.40`) | builds and serves the book | `cargo install mdbook` or a [release binary](https://github.com/rust-lang/mdBook/releases) |
| [`mdbook-mermaid`](https://github.com/badboy/mdbook-mermaid) | Mermaid diagram preprocessor | `cargo install mdbook-mermaid` |
| `python3` (standard library only) | compatibility-matrix generator + "Last updated" footer preprocessor | system Python ≥ 3.8 |

Optional, for the validation checks below:

| Tool | Why | Install |
|---|---|---|
| [`markdownlint-cli2`](https://github.com/DavidAnson/markdownlint-cli2) | lint Markdown style | `npm install -g markdownlint-cli2` |
| [`lychee`](https://github.com/lycheeverse/lychee) | check links resolve | `cargo install lychee` or `brew install lychee` |

## Directory structure

```text
agent-assembly-docs/
├── README.md                 # this repo, at a glance (you are reading its sibling)
├── CONTRIBUTING.md           # this file
├── compatibility.toml        # source of truth for the compatibility matrix
├── .markdownlint.json        # markdownlint config (the rules the linter enforces)
├── .github/
│   ├── workflows/aggregate.yml  # build + GitHub Pages deploy
│   └── PULL_REQUEST_TEMPLATE.md
├── design/                   # shared brand kit (tokens, artwork, per-generator CSS)
└── docs/
    ├── book.toml             # mdBook config (theme, preprocessors)
    ├── src/                  # ← all published pages live here
    │   ├── SUMMARY.md        # the book's table of contents / nav
    │   ├── README.md         # rendered as the Introduction page
    │   ├── documentation.md  # router to each component's own docs site
    │   ├── compatibility.md  # GENERATED — do not hand-edit the marked block
    │   └── …                 # one Markdown file per page
    ├── scripts/
    │   └── generate_compatibility.py
    └── theme/                # custom CSS/JS + the "Last updated" preprocessor
```

Pages you author by hand live under [`docs/src/`](docs/src/). The book renders
**only** pages that are registered in [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md);
an unlisted file is silently skipped.

> **Manually-authored vs. synced content.** Every page in this repo is currently
> authored here by hand. The hub does **not** vendor the component repos' docs — it
> links to each component's own published site root (see the table in `README.md`).
> An automated cross-repo sync (where each SDK repo's `docs/` would be copied into a
> read-only `docs/<repo-name>/` subtree on release) is **designed but not yet built**
> — see [`docs/sync-architecture.md`](docs/sync-architecture.md). Once it ships, any
> synced subtree will be **read-only here**: edit those pages in their source repo,
> not in this hub.

## Adding or editing a page

1. Create or edit a Markdown file under [`docs/src/`](docs/src/).
2. Register it in [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md) under the right
   section (or it will not appear in the built site).
3. Preview locally with `cd docs && mdbook serve` (live-reloads at
   <http://localhost:3000>).
4. Run the validation checks below.
5. Commit with a small, atomic GitEmoji commit (see [Commit and PR process](#commit-and-pr-process)).

**The compatibility matrix is generated, not hand-written.** To change it, edit
[`compatibility.toml`](compatibility.toml) and run:

```sh
python3 docs/scripts/generate_compatibility.py        # regenerate the page in place
python3 docs/scripts/generate_compatibility.py --check # verify it is in sync (CI runs this)
```

Never edit the content between the `BEGIN GENERATED` / `END GENERATED` markers in
[`docs/src/compatibility.md`](docs/src/compatibility.md) by hand — the generator
overwrites it.

## Validate before opening a PR

Run all four checks. CI runs the build + compatibility check and blocks the merge on
failure; markdownlint and lychee are run here locally to keep style and links clean.

### 1. Build the book

```sh
cd docs && mdbook build
```

Must complete with no warnings. This is the exact command CI runs.

### 2. Compatibility matrix in sync

```sh
python3 docs/scripts/generate_compatibility.py --check
```

Fails on any drift between [`compatibility.toml`](compatibility.toml) and the
generated tables.

### 3. Lint Markdown style (markdownlint)

The rule set lives in [`.markdownlint.json`](.markdownlint.json). Run the linter
from the repo root:

```sh
markdownlint-cli2 "**/*.md" "#docs/book"
```

(The `#docs/book` glob excludes the built output, which is git-ignored anyway.) Fix
every reported error — zero errors is the bar.

### 4. Check links (lychee)

Verify internal links resolve. Use `--offline` to check only on-disk relative links
(fast, no network), or drop the flag to also validate external URLs:

```sh
lychee --offline README.md CONTRIBUTING.md "docs/src/**/*.md"   # internal links only
lychee README.md CONTRIBUTING.md "docs/src/**/*.md"             # also checks external URLs
```

Every link must resolve. mdBook also reports broken **relative** links during
`mdbook build`, so step 1 is a second line of defence.

## Commit and PR process

- **Branch** off `main`:
  `<release-or-phase>/<ticket>/<type>/<short-summary>` —
  e.g. `v0.0.1/AAASM-319/docs/contributing`.
- **Commits** are small and atomic, one logical change each, in the GitEmoji style:
  `<emoji> (<scope>): <imperative summary>` — e.g.
  `📝 (docs): Add sync-architecture page`.
- **PR title:** `[<ticket>] <emoji> (<scope>): <summary>`. Base branch is always
  `main`.
- Fill out [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) —
  confirm the build passes, links are verified, new pages are registered in
  `SUMMARY.md`, and no self-hosted instructions are included (the project is
  SaaS-only in scope).
- Review is routed by [`.github/CODEOWNERS`](.github/CODEOWNERS); at least one Code
  Owner approval is required to merge. Content that crosses the open-core boundary
  (Cloud, Enterprise, licensing, security posture) is **held for owner content
  review** before publish.

## Triggering a docs sync for testing

The automated cross-repo sync pipeline (`repository_dispatch` → `sync-docs.yml` →
`scripts/sync-docs.sh`) **does not exist yet** — it is designed under **AAASM-302**
and described in [`docs/sync-architecture.md`](docs/sync-architecture.md). There is
nothing to trigger today.

When that pipeline lands, the planned way to run it manually for testing will be to
fire the dispatch event yourself against this repo:

```sh
# PLANNED — not yet wired up (AAASM-302). Documented here so the flow is clear.
gh api repos/ai-agent-assembly/agent-assembly-docs/dispatches \
  -f event_type=docs-release \
  -f client_payload[repo]=python-sdk \
  -f client_payload[tag]=v0.3.0
```

Until then, to preview the **current** site simply run `cd docs && mdbook serve` and
open <http://localhost:3000>; the live site is rebuilt automatically on every push to
`main`.
