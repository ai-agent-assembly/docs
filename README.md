# AI Agent Assembly — Documentation Hub

> The centralized, evergreen documentation hub for AI Agent Assembly — the governance-native runtime for AI agents.

[![docs](https://img.shields.io/github/actions/workflow/status/ai-agent-assembly/agent-assembly-docs/deploy.yml?branch=main&logo=githubactions&logoColor=white&label=docs)](https://github.com/ai-agent-assembly/agent-assembly-docs/actions/workflows/deploy.yml)
[![live docs](https://img.shields.io/badge/docs-live-3b82f6?logo=readthedocs&logoColor=white)](https://ai-agent-assembly.github.io/agent-assembly-docs/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue?logo=apache)](LICENSE)

This repository is the **documentation hub** for AI Agent Assembly. It is an
[mdBook](https://rust-lang.github.io/mdBook/) site, built and deployed to GitHub
Pages by the [`deploy.yml`](.github/workflows/deploy.yml) workflow on every push
to `main`. The hub is the central router across the product's independently
versioned components — it stays evergreen by linking to each component's own docs
site root rather than duplicating their content.

## Read the docs

**→ [ai-agent-assembly.github.io/agent-assembly-docs](https://ai-agent-assembly.github.io/agent-assembly-docs/)**

This is the canonical entry point. Start here for the documentation index, the
core↔SDK compatibility matrix, the security model, and the open-core boundary.

## What's inside

The published site (see [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md)) covers:

- **[Documentation index](docs/src/documentation.md)** — the central router to every
  component's own docs site (core + the three SDKs).
- **[Compatibility Matrix](docs/src/compatibility.md)** — the core↔SDK version
  matrix, generated from [`compatibility.toml`](compatibility.toml).
- **Platform & Security**
  - **[Security Model](docs/src/security-model.md)** — how the runtime governs agents.
  - **[Why AI Agent Assembly?](docs/src/comparison.md)** — comparison with alternatives.
  - **[Open Core Boundary](docs/src/open-core-boundary.md)** — what is open source vs. SaaS.
- **Getting Started** — Quick Start (SaaS) and Cloud Deployment (both *Coming soon*).
- **[Policy Reference](docs/src/policy-reference.md)** — the policy language reference.

## Component & SDK docs

AI Agent Assembly ships as four independently versioned programs, each with its
own documentation site. The hub's [router page](docs/src/documentation.md) links
to each site root — which always redirects to that component's newest stable
release, so these references never need maintenance:

| Component | Documentation |
|---|---|
| Core (`agent-assembly`) | <https://ai-agent-assembly.github.io/agent-assembly/> |
| Python SDK | <https://ai-agent-assembly.github.io/python-sdk/> |
| Node SDK | <https://ai-agent-assembly.github.io/node-sdk/> |
| Go SDK | <https://ai-agent-assembly.github.io/go-sdk/> |

## Local development

**Prerequisites**

- [mdBook](https://rust-lang.github.io/mdBook/) (CI pins `v0.4.40`)
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

## Contributing

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
