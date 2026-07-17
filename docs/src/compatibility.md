# Compatibility Matrix

AI Agent Assembly ships as several independently released programs — the **core**
monorepo (gateway, policy engine, sensors, runtime client) and the **Python**,
**Node**, and **Go** SDKs. *Compatibility* here means a cross-component contract:
a core release and the SDK release that speaks its **wire protocol**. An SDK is
compatible with a core release when it is built against — and serializes against —
that core's protocol contract (`aa-proto`).

The pairings below are usually **1:1 per release** — each row maps one core release
to the SDK release verified to speak its protocol — but a cell may also hold a
**version range** (e.g. `>=0.1.0,<0.2.0` or `0.1.x`) when a core release is
compatible with a band of SDK versions rather than one exact tag. Compatibility is
not guaranteed across **breaking changes**: those are tracked through the
**Protocol** column. A bump in a row's protocol value (`protocol/v1` →
`protocol/v2`) marks a breaking boundary, and the affected rows carry a numbered
footnote explaining the break and which SDK range is required. Long provenance and
caveat text lives in the **Notes** footnote list below the table, so the table
itself stays compact — each cell is just a version, a range, or `—`. Each
**Core release** cell carries a small superscript footnote (e.g.
`v0.0.1-alpha.5`²) hanging off the release identifier; clicking it jumps to that
row's provenance note at the bottom of the page.

## Latest published versions

[![core](https://img.shields.io/github/v/release/ai-agent-assembly/agent-assembly?include_prereleases&sort=semver&label=core&logo=github&color=3b82f6)](https://github.com/ai-agent-assembly/agent-assembly/releases)
[![PyPI](https://img.shields.io/pypi/v/agent-assembly?label=python-sdk&logo=pypi)](https://pypi.org/project/agent-assembly/)
[![npm](https://img.shields.io/npm/v/@agent-assembly/sdk/rc?label=node-sdk&logo=npm)](https://www.npmjs.com/package/@agent-assembly/sdk)
[![Go](https://img.shields.io/github/v/tag/ai-agent-assembly/go-sdk?sort=semver&label=go-sdk&logo=go&color=3b82f6)](https://github.com/ai-agent-assembly/go-sdk/tags)

All four badges read the **live** latest published version, so they stay current
without maintenance. **Python** reads PyPI and **Node** reads npm's `rc`
dist-tag. **Core** uses shields.io's `github/v/release` endpoint
(`include_prereleases&sort=semver`): the monorepo carries a non-release `spec/*`
tag that pollutes plain `github/v/tag` semver sorting, and core cuts GitHub
Releases, so the release endpoint is the authoritative dynamic source. **Go** uses
`github/v/tag` (`sort=semver`) because go-sdk publishes version tags but no GitHub
Releases. Each badge links to the relevant registry or release/tag list for the
authoritative current version.

## Core ↔ SDK matrix

<!-- BEGIN GENERATED:matrix -->

| Core release | Status | Protocol | Python SDK | Node SDK | Go SDK |
|---|---|---|---|---|---|
| v0.0.1-rc.6[^cn1] | current | protocol/v1 | 0.0.1-rc.6 (PyPI 0.0.1rc6) | npm @rc 0.0.1-rc.6 | v0.0.1-rc.6 |
| v0.0.1-rc.5[^cn2] | supported | protocol/v1 | 0.0.1-rc.5 (PyPI 0.0.1rc5) | npm @rc 0.0.1-rc.5 | v0.0.1-rc.5 |
| v0.0.1-rc.4[^cn3] | supported | protocol/v1 | 0.0.1-rc.4 (PyPI 0.0.1rc4) | npm @rc 0.0.1-rc.4 | v0.0.1-rc.4 |
| v0.0.1-rc.3[^cn4] | supported | protocol/v1 | 0.0.1-rc.3 (PyPI 0.0.1rc3) | npm @rc 0.0.1-rc.3 | v0.0.1-rc.3 |
| v0.0.1-rc.2[^cn5] | supported | protocol/v1 | 0.0.1-rc.2 (PyPI 0.0.1rc2) | npm @rc 0.0.1-rc.2 | v0.0.1-rc.2 |
| v0.0.1-rc.1[^cn6] | supported | protocol/v1 | 0.0.1-rc.1 (PyPI 0.0.1rc1) | npm @rc 0.0.1-rc.1 | v0.0.1-rc.1 |
| v0.0.1-beta.4[^cn7] | supported | protocol/v1 | 0.0.1-beta.4 (PyPI 0.0.1b4) | npm @beta 0.0.1-beta.4 | v0.0.1-beta.4 |
| v0.0.1-beta.3[^cn8] | supported | protocol/v1 | 0.0.1-beta.3 (PyPI 0.0.1b3) | npm @beta 0.0.1-beta.3 | v0.0.1-beta.3 |
| v0.0.1-beta.2[^cn9] | supported | protocol/v1 | 0.0.1-beta.2 (PyPI 0.0.1b2) | npm @beta 0.0.1-beta.2 | v0.0.1-beta.2 |
| v0.0.1-beta.1[^cn10] | supported | protocol/v1 | 0.0.1-beta.1 (PyPI 0.0.1b1) | npm @beta 0.0.1-beta.1 | v0.0.1-beta.1 |
| v0.0.1-alpha.9[^cn11] | supported | protocol/v1 | — | — | — |
| v0.0.1-alpha.8[^cn11] | supported | protocol/v1 | — | — | — |
| v0.0.1-alpha.7[^cn11] | supported | protocol/v1 | — | — | — |
| v0.0.1-alpha.6[^cn11] | supported | protocol/v1 | — | — | — |
| tested @ 9cf8a033 (post-v0.0.1-alpha.5, unreleased)[^cn12] | supported | protocol/v1 | PyPI 0.0.1a5 / git v0.0.2 | npm @alpha 0.0.1-alpha.5 | v0.0.1-alpha.4 |
| v0.0.1-alpha.5[^cn13] | supported | protocol/v1 | — | — | — |
| v0.0.1-alpha.4[^cn14] | supported | protocol/v1 | — | — | — |
| v0.0.1-alpha.3[^cn15] | supported | protocol/v1 | — | — | — |
| v0.0.1-alpha.2[^cn15] | previous | protocol/v1 | — | — | — |
| v0.0.1-alpha.1[^cn15] | previous | protocol/v1 | — | — | — |

<!-- END GENERATED:matrix -->

A cell of `—` means an exact, authoritative core↔SDK pairing could **not** be
determined from a published tag or a committed pin, so none is asserted. The
superscript on each **Core release** cell links that row to its provenance
footnote in the **Notes** list below.

### Notes

<!-- BEGIN GENERATED:notes -->

[^cn1]: Latest published core tag and the current product line. Sixth release-candidate in the v0.0.1 series, cut as a coordinated release across agent-assembly + python-sdk + node-sdk + go-sdk: all four repos carry a v0.0.1-rc.6 tag, PyPI publishes 0.0.1rc6, and npm publishes @agent-assembly/sdk@0.0.1-rc.6 under the rc dist-tag. Each SDK at this tag is built against the matching rc.6 core revision, so the tag<->tag pairing is authoritative.

[^cn2]: Published core tag. Fifth release-candidate in the v0.0.1 series, cut as a coordinated release across agent-assembly + python-sdk + node-sdk + go-sdk: all four repos carry a v0.0.1-rc.5 tag, PyPI publishes 0.0.1rc5, and npm publishes @agent-assembly/sdk@0.0.1-rc.5 under the rc dist-tag. Each SDK at this tag is built against the matching rc.5 core revision, so the tag<->tag pairing is authoritative.

[^cn3]: Published core tag. Fourth release-candidate in the v0.0.1 series, cut as a coordinated release across agent-assembly + python-sdk + node-sdk + go-sdk: all four repos carry a v0.0.1-rc.4 tag, PyPI publishes 0.0.1rc4, and npm publishes @agent-assembly/sdk@0.0.1-rc.4 under the rc dist-tag. A release-pipeline completeness cut with no wire-protocol change: it ships the previously-omitted aa-api-server binary and publishes the aa-gateway container image, adds a release-artifact completeness gate, builds every supported Python interpreter (cp312/cp313/cp314), bundles the Node native .node binding, and serves local-mode gRPC agent registration on loopback 127.0.0.1:50051. Each SDK at this tag is built against the matching rc.4 core revision, so the tag<->tag pairing is authoritative.

[^cn4]: Published core tag. Third release-candidate in the v0.0.1 series, cut as a coordinated release across agent-assembly + python-sdk + node-sdk + go-sdk: all four repos carry a v0.0.1-rc.3 tag, PyPI publishes 0.0.1rc3, and npm publishes @agent-assembly/sdk@0.0.1-rc.3 under the rc dist-tag. Each SDK at this tag is built against the matching rc.3 core revision, so the tag<->tag pairing is authoritative.

[^cn5]: Published core tag. Second release-candidate in the v0.0.1 series, cut as a coordinated release across agent-assembly + python-sdk + node-sdk + go-sdk: all four repos carry a v0.0.1-rc.2 tag, PyPI publishes 0.0.1rc2, and npm publishes @agent-assembly/sdk@0.0.1-rc.2 under the rc dist-tag. Each SDK at this tag is built against the matching rc.2 core revision, so the tag<->tag pairing is authoritative.

[^cn6]: Published core tag. First release-candidate in the v0.0.1 series, promoting the channel up from beta. Coordinated across all four repos: agent-assembly + python-sdk + node-sdk + go-sdk each carry a v0.0.1-rc.1 tag (PyPI 0.0.1rc1, npm @agent-assembly/sdk@0.0.1-rc.1 under the rc dist-tag).

[^cn7]: Published core tag. Cut as a coordinated release across all four repos: agent-assembly + python-sdk + node-sdk + go-sdk each carry a v0.0.1-beta.4 tag (PyPI 0.0.1b4, npm @agent-assembly/sdk@0.0.1-beta.4 under the beta dist-tag).

[^cn8]: Published core tag. Cut as a coordinated release across all four repos: agent-assembly + python-sdk + node-sdk + go-sdk each carry a v0.0.1-beta.3 tag (PyPI 0.0.1b3, npm @agent-assembly/sdk@0.0.1-beta.3 under the beta dist-tag).

[^cn9]: Published core tag. Cut as a coordinated release across agent-assembly + python-sdk + node-sdk + go-sdk (monorepo AAASM-3004): all four repos carry a v0.0.1-beta.2 tag, PyPI publishes 0.0.1b2, and npm publishes @agent-assembly/sdk@0.0.1-beta.2 under the beta dist-tag. Each SDK at this tag is built against the matching beta.2 core revision, so the tag<->tag pairing is authoritative.

[^cn10]: Published core tag. First beta-channel pre-release in the v0.0.1 series (monorepo AAASM-2951), promoting the channel up from alpha. Coordinated across all four repos: agent-assembly + python-sdk + node-sdk + go-sdk each carry a v0.0.1-beta.1 tag (PyPI 0.0.1b1, npm @agent-assembly/sdk@0.0.1-beta.1).

[^cn11]: Published core tag (2026-06-12 to 2026-06-14), between v0.0.1-alpha.5 and the beta.1 coordinated release. No SDK repository published a matching tag at this point in the alpha line: python-sdk's alpha tags stop at v0.0.1-alpha.3, node-sdk's at v0.0.1-alpha.4, and go-sdk's at v0.0.1-alpha.5. SDK cells left as — per the accuracy contract.

[^cn12]: All three SDKs pin aa-core/aa-proto/aa-sdk-client at git SHA 9cf8a033 (PR #958, 2026-06-05; 587 commits ahead of v0.0.1-alpha.5). This was the authoritatively-verified core<->SDK pairing before the beta line was cut. It is not a published core tag.

[^cn13]: Latest published core tag. No SDK tag pins exactly this commit; current SDKs pin a later SHA (see the pinned-commit row). SDK cells left as — to avoid asserting an unverified tag<->tag pairing.

[^cn14]: Published core tag. No SDK tag authoritatively pins this exact commit.

[^cn15]: Published core tag. SDK tags carrying the same version string (python/node/go of the matching alpha) exist, but at their tag time the SDK FFI crates did not yet pin a resolvable aa-core rev, so an exact commit<->commit pairing is NOT verifiable. Left as — per the accuracy contract.

<!-- END GENERATED:notes -->

## Runtime requirements

<!-- BEGIN GENERATED:requirements -->

| SDK | Runtime requirement | Install | Source |
|---|---|---|---|
| Python SDK | Python >=3.12,<4.0 | [Install guide](https://docs.agent-assembly.com/python-sdk/) | python-sdk pyproject.toml [project].requires-python |
| Node SDK | Node.js >=18.18.0 (pnpm >=10 to build from source) | [Install guide](https://docs.agent-assembly.com/node-sdk/) | node-sdk package.json [engines] |
| Go SDK | Go >=1.26.0 | [Install guide](https://docs.agent-assembly.com/go-sdk/) | go-sdk go.mod (go directive) |

<!-- END GENERATED:requirements -->

## How this is maintained

This page is **manifest-driven**. The source of truth is
[`compatibility.toml`](https://github.com/ai-agent-assembly/docs/blob/main/compatibility.toml)
at the repository root. The matrix and requirements tables above are rendered from
it by `docs/scripts/generate_compatibility.py`; the content between the
`BEGIN GENERATED` / `END GENERATED` markers is generated — **do not hand-edit it**.
Edit the manifest and regenerate:

```bash
python3 docs/scripts/generate_compatibility.py
```

A CI step runs the same script with `--check`, so any drift between the manifest
and this page fails the build. The manifest is updated at each coordinated
release; every cell traces to a published tag, a registry release, or a committed
git pin (recorded in the **Notes** footnotes and the manifest comments). SDK cells
may be a single version or a **range**, and breaking changes are recorded by
bumping a row's protocol value and adding a footnote — see the manifest comments
for the range and breaking-change conventions, including a commented example.

_Last verified: 2026-06-27._
