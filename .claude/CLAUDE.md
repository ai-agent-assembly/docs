# CLAUDE.md — agent-assembly-docs

Guidance for Claude Code (and humans) working in this repository. This file holds
**repo-specific** context only; universal engineering policy lives in the global
config. When a fact here duplicates `README.md`, `docs/book.toml`, or the
`deploy.yml` workflow, treat those as the source of truth and update them, not just
this file.

Org-wide baseline: https://github.com/ai-agent-assembly/.github/blob/main/CLAUDE.md
(org-universal conventions this file doesn't repeat).

## What this repo is

The **canonical public documentation hub** for AI Agent Assembly — the product that
enforces governance on AI agents. It is an [mdBook](https://rust-lang.github.io/mdBook/)
site, built and deployed to GitHub Pages on every push to `main`, and published at
**<https://docs.agent-assembly.com/>**.

This hub **aggregates** the docs of every module into one unified, searchable
site. Each of the product's four independently-versioned components (core + the
three SDKs) ships its **own** docs, built with its native toolchain (mdBook,
mkdocs-material, Docusaurus, Hugo+Hextra); the aggregation pipeline pulls each
one, builds it, and mounts its output under a stable subpath — `/core/`,
`/python-sdk/`, `/node-sdk/`, `/go-sdk/` — with a unified Pagefind search index
over the whole site. See [`AGGREGATION.md`](../AGGREGATION.md) for the full
contract. Alongside the aggregated component docs, this repo also authors the
first-party cross-cutting material: the documentation index, the core↔SDK
compatibility matrix, the security model, the comparison page, the open-core
boundary, and the policy reference.

## Site layout

| Path | Role |
|---|---|
| `docs/book.toml` | mdBook config: theme, `git-repository-url`, `edit-url-template`, preprocessors |
| `docs/src/` | All authored content, plain Markdown (no front-matter) |
| `docs/src/SUMMARY.md` | Table of contents — **every page must be registered here or it won't render** |
| `docs/src/compatibility.md` | **Generated** — do not hand-edit between the `BEGIN/END GENERATED` markers |
| `compatibility.toml` | Source manifest for the compatibility matrix (root of repo) |
| `docs/scripts/generate_compatibility.py` | Renders `compatibility.toml` → `compatibility.md` |
| `docs/theme/` | Brand CSS, light/dark toggle, and the `last-changed.py` "Last updated" git preprocessor |
| `docs/book/` | Build output — **gitignored**, never commit it |
| `design/` | Design specs (versioned `vN/`) for the docs site itself |

mdBook has **no front-matter**: a page's title comes from its `# H1` and its
placement comes from `SUMMARY.md`. The per-page "Last updated" footer is appended
automatically from each chapter's last commit date — there is nothing to edit by hand.

> **Versioning channel model:** the published hub does not yet run the
> latest/pre-release/stable + archived channel layout some sibling docs sites use; it
> currently routes to each component's own site root. Don't assume channel scaffolding
> exists here — verify against `SUMMARY.md` and `book.toml` before referencing it.

## Build, test, serve

See `README.md` for the full list. Common commands (run from the repo root):

```sh
cd docs && mdbook serve     # live-reload preview at http://localhost:3000
cd docs && mdbook build     # build the site (CI gate: must pass with no warnings)
python3 docs/scripts/generate_compatibility.py --check   # fail on matrix drift (CI runs this)
python3 docs/scripts/generate_compatibility.py           # regenerate compatibility.md in place
```

**Prerequisites:** mdBook (CI pins **`v0.4.40`**), `mdbook-mermaid` (the Mermaid
preprocessor), and `python3` (stdlib only — the compatibility generator and the
"Last updated" preprocessor have no third-party deps). There is **no Node toolchain**
and no lefthook in this repo; the only local gate is `mdbook build` + the matrix check.

## Conventions

- **Commits:** `<emoji> (<scope>): <imperative summary>` (gitmoji.dev). One logical
  unit per commit; bisectable. Keep them small and atomic.
- **Branch:** `<release-or-phase>/<ticket>/<type>/<short_summary>`
  (e.g. `v0.0.1/AAASM-3079/docs/claude_md`).
- **PR title:** `[<ticket>] <emoji> (<scope>): <summary>`; base branch **always
  `main`**; body follows `.github/PULL_REQUEST_TEMPLATE.md`; ≥1 Pioneer-team approval.
- **markdownlint:** config in `.markdownlint.json` (MD013/MD033/MD041 disabled).

## Repo-specific gotchas

- **Default branch is `main`** (not `master` like the core monorepo). Branch off and
  PR against `main`.
- **`origin` is canonical** — it points to `AI-agent-assembly/agent-assembly-docs`
  (the org, accessed via the `ai-agent-assembly` → `AI-agent-assembly` case alias).
  Confirm with `git remote -v`; scope changes against `origin/main`, which is often
  ahead of a stale checkout.
- **CI is path-scoped.** `deploy.yml` only triggers on `docs/**`, `compatibility.toml`,
  and `.github/workflows/deploy.yml`. A `.claude/`-only (or other root-file-only)
  change runs **no CI** — it is review-gated, not CI-gated. Validate locally instead.
- **`docs/src/compatibility.md` is generated** — edit `compatibility.toml` and run the
  generator; never hand-edit between the `BEGIN GENERATED` / `END GENERATED` markers.
- **Org GitHub Actions can be billing-blocked** — jobs may abort in seconds with a
  payments message. Check run **annotations** before triaging as a real failure;
  **validate locally** (`mdbook build`) rather than waiting on CI.
- **Never `--no-verify`; never force-push.** There are no commit hooks here, so a
  clean `git push` is normally all that's needed.

## Project policy

- **JIRA:** project AAASM; set **Component** (`customfield_10041`) to the repo
  (`AI-agent-assembly/agent-assembly-docs`); Team (`customfield_10001`) = Pioneer.
  Epic → Story → Subtask (one Subtask ≈ one commit) + a `Verify …` subtask per Story.
- **Self-hosted deployment is out of scope** product-wide — the docs are **SaaS-only**.
  Don't add Helm/Terraform/air-gapped/migration instructions even if the spec mentions
  them (the PR template enforces this checkbox).
- **The Protocol Specification stays in the `agent-assembly` monorepo** — do not author
  spec content here or in a separate `agent-assembly-spec` repo (that repo is archived
  by design). This hub links out; it does not own component or protocol docs.

## Documentation conventions — document the WHY, not the WHAT

Because this is the public hub, the prose **is** the product. Pages should capture the
intent a reader cannot reconstruct from the component docs alone — rationale, scope
boundaries, and trade-offs — not restate version numbers or API surface that lives
(and changes) in each component's own site. Duplicated content rots out of sync.

- **Per page (`# H1` + intro):** state *who the page is for* and *why it exists*
  before the detail (e.g. the security model opens "for enterprise security and
  compliance teams"). One H1 per file; register it in `SUMMARY.md`.
- **Hub-router pages:** link to a component's **site root**, never a deep version-pinned
  URL — the root redirect keeps the link evergreen. Prefer linking out to duplicating.
- **Generated content:** the compatibility matrix is the source of truth for versions;
  reference it, don't restate version numbers in prose where they'll drift.
- **Skip:** copying API reference, install steps, or changelogs that live in a
  component's own docs. The hub's job is orientation and cross-cutting concerns.
- **Big decisions → ADRs**, not scattered into a page footnote. Link the page to the
  ADR / design spec (`design/vN/`) rather than embedding the full rationale inline.

> Net: a reader (human or LLM) landing on a hub page should understand *why it exists*
> and *where to go next* without it duplicating — and inevitably contradicting — the
> component docs it routes to. If a page only restates *what* another site already
> says, link instead.
