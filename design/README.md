# Documentation brand kit

The **single source of truth** for the shared documentation style across every AI Agent
Assembly doc surface (the central hub + each SDK/component doc site).

- **[`doc-tokens.md`](./doc-tokens.md)** — every design token (brand accent, neutrals,
  typography, measure, admonition colors) with light/dark values and their dashboard source.
- **[`brand/`](./brand)** — official artwork: `icon.png` (A-mark, no text), `favicon.png`, `logo.png` (full lockup), `social-card.png` (1200×630).
- **[`snippets/`](./snippets)** — copy-verbatim style files, one per generator:
  | Generator | Repos | Files |
  |---|---|---|
  | mdBook | agent-assembly-docs, agent-assembly | `mdbook-additional.css` |
  | MkDocs Material | python-sdk | `mkdocs-extra.css` + `mkdocs-palette.yml` |
  | Docusaurus | node-sdk, inner-document | `docusaurus-custom.css` |
  | Hugo / Hextra | go-sdk | `hextra-custom.css` |

**Path A:** each repo keeps its native generator and copies its snippet. The tokens are
identical across all four, so the sites share one brand/look-and-feel while their layouts
stay native. To rebrand: change `doc-tokens.md`, update each snippet's values, re-sync repos.

Tracked under Epic **AAASM-2732**; this kit is **AAASM-2733** (blocks the per-repo styling stories).
