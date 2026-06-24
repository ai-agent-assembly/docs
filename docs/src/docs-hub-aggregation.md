# How this documentation hub is assembled

This site is a **central hub** that aggregates the documentation of every AI
Agent Assembly module into one place, under stable subpaths, with one unified
search. Each module keeps its own documentation toolchain — the hub **pulls** and
**assembles** them rather than forcing a single generator.

| Path | Module | Generator |
|---|---|---|
| `/` | This hub | mdBook |
| [`/core/`](/core/) | `agent-assembly` (core monorepo) | mdBook |
| [`/python-sdk/`](/python-sdk/) | `python-sdk` | mkdocs-material |
| [`/node-sdk/`](/node-sdk/) | `node-sdk` | Docusaurus |
| [`/go-sdk/`](/go-sdk/) | `go-sdk` | Hugo + Hextra |

## What gets aggregated

For the hub's canonical view, each module's **default channel** (its *latest*
line, built from `master`/`main` HEAD) is mounted at `/<module>/`. The per-module
**standalone** sites keep their full per-version channel browsing — the
[component table on the home page](README.md#sdks--components) links out to them.

## Unified search

A single **Pagefind** index is built over the final assembled site, so the search
box on this hub finds pages across the hub *and* every module in one query — even
though each module was built by a different generator.

## The contract

The machine-readable module registry, the build/copy contract, the per-generator
base-URL strategy, and the versioning decision are documented in
[`AGGREGATION.md`](https://github.com/ai-agent-assembly/agent-assembly-docs/blob/main/AGGREGATION.md)
at the repository root, and implemented by `docs/scripts/aggregate.sh` +
`.github/workflows/aggregate.yml`.
