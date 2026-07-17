# AI Agent Assembly — Documentation Hub

> The centralized, evergreen documentation hub for AI Agent Assembly — the governance-native runtime for AI agents.

[![docs](https://img.shields.io/github/actions/workflow/status/ai-agent-assembly/docs/aggregate.yml?branch=main&logo=githubactions&logoColor=white&label=docs)](https://github.com/ai-agent-assembly/docs/actions/workflows/aggregate.yml)
[![live docs](https://img.shields.io/badge/docs-live-3b82f6?logo=readthedocs&logoColor=white)](https://docs.agent-assembly.com/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue?logo=apache)](LICENSE)

This repository is the **documentation hub** for AI Agent Assembly. It is an
[mdBook](https://rust-lang.github.io/mdBook/) site, built and deployed to GitHub
Pages by the [`aggregate.yml`](.github/workflows/aggregate.yml) workflow on every push
to `main`. The hub aggregates the docs of every independently versioned
component — building each with its own native toolchain and mounting it under a
stable subpath (`/core/`, `/python-sdk/`, `/node-sdk/`, `/go-sdk/`) — into one
unified, searchable site.

## Read the docs

**→ [docs.agent-assembly.com](https://docs.agent-assembly.com/)**

This is the canonical entry point. Start here for the documentation index, the
core↔SDK compatibility matrix, the security model, and the open-core boundary.

## What's inside

The published site (see [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md)) covers:

- **[Documentation index](docs/src/documentation.md)** — the central router to every
  component's own docs site (core + the three SDKs).
- **[Compatibility Matrix](docs/src/compatibility.md)** — the core↔SDK version
  matrix, generated from [`compatibility.toml`](compatibility.toml).
- **[Source of Truth & Status](docs/src/source-of-truth.md)** — the canonical map
  of which repo owns each area and whether it is public, private/internal, alpha,
  or planned.
- **Platform & Security**
  - **[Security Model](docs/src/security-model.md)** — how the runtime governs agents.
  - **[Why AI Agent Assembly?](docs/src/comparison.md)** — comparison with alternatives.
  - **[Open Core Boundary](docs/src/open-core-boundary.md)** — what is open source vs. SaaS.
- **Getting Started** — Quick Start (SaaS) and Cloud Deployment (both *Coming soon*).
- **[Policy Reference](docs/src/policy-reference.md)** — the policy language reference.

## Component & SDK docs

AI Agent Assembly ships as several independently versioned programs, each with
its own source repository and (for the public ones) its own documentation site.
The hub's [router page](docs/src/documentation.md) links to each component's docs
site root — which always redirects to that component's newest stable release, so
these references never need maintenance. The
[**Source of Truth & Status**](docs/src/source-of-truth.md) page is the canonical
status map for every area below.

| Area | Source repository | Docs |
|---|---|---|
| Core (`agent-assembly`) | [agent-assembly](https://github.com/ai-agent-assembly/agent-assembly) | <https://docs.agent-assembly.com/core/> |
| Python SDK | [python-sdk](https://github.com/ai-agent-assembly/python-sdk) | <https://docs.agent-assembly.com/python-sdk/> |
| Node SDK | [node-sdk](https://github.com/ai-agent-assembly/node-sdk) | <https://docs.agent-assembly.com/node-sdk/> |
| Go SDK | [go-sdk](https://github.com/ai-agent-assembly/go-sdk) | <https://docs.agent-assembly.com/go-sdk/> |
| Runnable examples | [examples](https://github.com/ai-agent-assembly/examples) | repo `README` |
| Homebrew / install | [homebrew-tap](https://github.com/ai-agent-assembly/homebrew-tap) | repo `README` |
| Specs (protocol & policy) | in the `agent-assembly` monorepo | [Policy reference](docs/src/policy-reference.md) |
| Releases & compatibility | this hub + component tags | [Compatibility matrix](docs/src/compatibility.md) |
| Cloud (SaaS) | `cloud` *(private, planned)* | [Cloud deployment](docs/src/cloud-deployment.md) |
| Enterprise | `agent-assembly-enterprise` *(private, planned)* | [Open core boundary](docs/src/open-core-boundary.md) |

## Source-of-truth labels

The hub spans public and private repositories at different maturity levels. Every
area on the [Source of Truth & Status](docs/src/source-of-truth.md) page carries
two labels so readers know how much weight to give a page:

- **Visibility** — 🟢 *Public* (source repo is public) or 🔒 *Private / internal*
  (source repo is private; docs describe intent, not a browsable codebase).
- **Maturity** — 🧪 *Release candidate* (ships today, may change; the product is
  currently `v0.0.1-rc`) or 🗺️ *Planned* (designed and documented, not yet generally
  available).

When adding or editing a page that describes a new area, update the status map so
the public/private and alpha/planned state stays accurate.

## How content reaches the site

The hub's own first-party pages under [`docs/src/`](docs/src/) are hand-written
Markdown, registered in [`SUMMARY.md`](docs/src/SUMMARY.md) and built with
`mdbook build`. On every push to `main`, the
[`aggregate.yml`](.github/workflows/aggregate.yml) workflow builds this hub mdBook
**and pulls each component's own docs site**, builds every one with its native
toolchain (mdBook, mkdocs-material, Docusaurus, Hugo + Hextra), and assembles them
into a single static site — each module mounted under a stable subpath (`/core/`,
`/python-sdk/`, `/node-sdk/`, `/go-sdk/`) with one unified Pagefind search index —
then deploys the combined site to GitHub Pages.

The machine-readable module registry, the build/copy contract, and the
per-generator base-URL strategy are the executable aggregation contract in
[`AGGREGATION.md`](AGGREGATION.md), implemented by
[`docs/scripts/aggregate.sh`](docs/scripts/aggregate.sh) and run by `aggregate.yml`.
For the reader-facing overview, see
[How this hub is assembled](docs/src/docs-hub-aggregation.md).

## Local development

**Prerequisites**

- [mdBook](https://rust-lang.github.io/mdBook/) (CI pins `v0.5.2`)
- [`mdbook-mermaid`](https://github.com/badboy/mdbook-mermaid) — the Mermaid diagram preprocessor
- `python3` — for the compatibility-matrix generator and the "Last updated" preprocessor (standard library only, no third-party deps)

**Serve locally**

```sh
cd docs && mdbook serve
```

This builds and live-reloads the site at <http://localhost:3000>.

**Check the compatibility matrix is in sync**

```sh
python3 docs/scripts/generate_compatibility.py --check
```

[`generate_compatibility.py`](docs/scripts/generate_compatibility.py) renders the
core↔SDK tables into [`docs/src/compatibility.md`](docs/src/compatibility.md) from
[`compatibility.toml`](compatibility.toml). Run it with `--check` to fail on drift
(CI runs the same check); run it with no arguments to regenerate the page in place.

The per-page **"Last updated"** footer is appended automatically by the
[`last-changed.py`](docs/theme/last-changed.py) git preprocessor, which reads each
chapter's last commit date — there is nothing to update by hand.

## Validation

Before opening a PR, run the same checks CI runs and review the navigation:

1. **Build** — `cd docs && mdbook build` must complete with no warnings. CI runs
   the identical command in [`aggregate.yml`](.github/workflows/aggregate.yml) and blocks
   the merge on any failure.
2. **Compatibility matrix in sync** — `python3 docs/scripts/generate_compatibility.py --check`
   must pass (CI runs this too); it fails on any drift between
   [`compatibility.toml`](compatibility.toml) and the generated tables.
3. **Cross-link check** — verify internal links resolve. mdBook reports broken
   relative links during `mdbook build`; for a deeper sweep you can run
   `mdbook-linkcheck` (optional, validates external links too). Every page must be
   registered in [`SUMMARY.md`](docs/src/SUMMARY.md) or mdBook will not render it.
4. **Navigation review** — `cd docs && mdbook serve`, open
   <http://localhost:3000>, and walk the sidebar top to bottom: confirm every area
   (core, SDKs, cloud, enterprise, Homebrew, specs, releases, operations) is
   reachable and the [Source of Truth & Status](docs/src/source-of-truth.md) labels
   are accurate.

## Ownership

This hub is maintained by the AI Agent Assembly team. Review is routed by
[`.github/CODEOWNERS`](.github/CODEOWNERS); at least one Code Owner approval is
required to merge. Content that crosses the open-core boundary (Cloud, Enterprise,
licensing, security posture) is **held for owner content review** before publish.
The content itself is sourced from:

- **Each component's own docs site** — the hub links to component site roots
  rather than copying their content (see the table above).
- **[`compatibility.toml`](compatibility.toml)** — the human-edited manifest that
  generates the compatibility matrix.
- **Git history** — the per-page "Last updated" footer is derived automatically by
  the [`last-changed.py`](docs/theme/last-changed.py) preprocessor.

## Contributing

See **[`CONTRIBUTING.md`](CONTRIBUTING.md)** for the full guide: how to add or edit
pages, the directory layout, how to run markdownlint and the lychee link checker
locally, and the PR process. The essentials:

- Content lives under [`docs/src/`](docs/src/), authored in Markdown.
- Every page must be registered in [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md).
- The compatibility matrix is **generated** — edit [`compatibility.toml`](compatibility.toml)
  and run the generator; never hand-edit the content between the `BEGIN GENERATED`
  / `END GENERATED` markers in `compatibility.md`.
- Run `cd docs && mdbook build` and confirm it passes with no warnings before opening a PR.
- Follow the GitEmoji commit convention and keep commits small and atomic.

See [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) for the
full PR checklist.

## License

Licensed under the [Apache License 2.0](LICENSE).
