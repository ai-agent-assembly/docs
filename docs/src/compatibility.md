# Compatibility Matrix

AI Agent Assembly ships as several independently released programs — the **core**
monorepo (gateway, policy engine, sensors, runtime client) and the **Python**,
**Node**, and **Go** SDKs. *Compatibility* here means a cross-component contract:
a core release and the SDK release that speaks its **wire protocol**. An SDK is
compatible with a core release when it is built against — and serializes against —
that core's protocol contract (`aa-proto`).

The pairings below are **1:1 per release**: each row maps one core release to the
SDK release verified to speak its protocol. (The manifest schema keeps each cell a
free-form string so a future release can widen a single cell into a version
*range* without restructuring the table.)

## Latest published versions

[![core](https://img.shields.io/github/v/release/ai-agent-assembly/agent-assembly?include_prereleases&label=core&logo=github)](https://github.com/ai-agent-assembly/agent-assembly/releases)
[![PyPI](https://img.shields.io/pypi/v/agent-assembly?label=python-sdk&logo=pypi)](https://pypi.org/project/agent-assembly/)
[![npm](https://img.shields.io/npm/v/@agent-assembly/sdk/alpha?label=node-sdk&logo=npm)](https://www.npmjs.com/package/@agent-assembly/sdk)
[![Go](https://img.shields.io/github/v/tag/ai-agent-assembly/go-sdk?include_prereleases&label=go-sdk&logo=go)](https://github.com/ai-agent-assembly/go-sdk/tags)

These badges read the **live** latest published version from each registry (PyPI,
npm — `alpha` dist-tag, GitHub releases/tags), so they are always current without
any maintenance.

## Core ↔ SDK matrix

<!-- BEGIN GENERATED:matrix -->

| Core release | Status | Protocol | Python SDK | Node SDK | Go SDK | Notes |
|---|---|---|---|---|---|---|
| tested @ 9cf8a033 (post-v0.0.1-alpha.5, unreleased) | current | protocol/v1 | PyPI 0.0.1a5 / git v0.0.2 | npm @alpha 0.0.1-alpha.5 | v0.0.1-alpha.4 | All three SDKs pin aa-core/aa-proto/aa-sdk-client at git SHA 9cf8a033 (PR #958, 2026-06-05; 587 commits ahead of v0.0.1-alpha.5). This is the ONLY authoritatively-verified core<->SDK pairing: it is the exact revision every current SDK is built against. It is not a published core tag. |
| v0.0.1-alpha.5 | supported | protocol/v1 | — | — | — | Latest published core tag. No SDK tag pins exactly this commit; current SDKs pin a later SHA (see the row above). SDK cells left as — to avoid asserting an unverified tag<->tag pairing. |
| v0.0.1-alpha.4 | supported | protocol/v1 | — | — | — | Published core tag. No SDK tag authoritatively pins this exact commit. |
| v0.0.1-alpha.3 | supported | protocol/v1 | — | — | — | Published core tag. SDKs of the same version string (python/node/go v0.0.1-alpha.3) were released around this line per the core repo's own matrix, but at their tag time the SDK FFI crates did not yet pin a resolvable aa-core rev, so an exact commit<->commit pairing is NOT verifiable. Left as — per the accuracy contract. |
| v0.0.1-alpha.2 | previous | protocol/v1 | — | — | — | Published core tag. Same-version-string SDK tags exist (python/node/go v0.0.1-alpha.2) but no resolvable pin; left as —. |
| v0.0.1-alpha.1 | previous | protocol/v1 | — | — | — | Earliest published core tag. Same-version-string SDK tags exist (python/node/go v0.0.1-alpha.1) but no resolvable pin; left as —. |

<!-- END GENERATED:matrix -->

A cell of `—` means an exact, authoritative core↔SDK pairing could **not** be
determined from a published tag or a committed pin, so none is asserted. See the
**Notes** column for the provenance or caveat behind each row.

> **Why the current row is a commit, not a tag.** Every SDK currently pins the
> core crates (`aa-core` / `aa-proto` / `aa-sdk-client`) at a single git SHA that
> is *newer than the latest published core tag* (`v0.0.1-alpha.5`). That commit —
> not any released core tag — is the revision the published SDKs are actually
> built against, so it is the only authoritatively-verified pairing.

## Runtime requirements

<!-- BEGIN GENERATED:requirements -->

| SDK | Runtime requirement | Install | Source |
|---|---|---|---|
| Python SDK | Python >=3.12,<4.0 | `pip install agent-assembly --pre` | python-sdk pyproject.toml [project].requires-python |
| Node SDK | Node.js >=18.18.0 (pnpm >=10 to build from source) | `npm install @agent-assembly/sdk@alpha` | node-sdk package.json [engines] |
| Go SDK | Go >=1.26.0 | `go get github.com/ai-agent-assembly/go-sdk@latest` | go-sdk go.mod (go directive) |

<!-- END GENERATED:requirements -->

## How this is maintained

This page is **manifest-driven**. The source of truth is
[`compatibility.toml`](https://github.com/ai-agent-assembly/agent-assembly-docs/blob/main/compatibility.toml)
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
git pin (recorded in the **Notes** column and the manifest comments).

_Last verified: 2026-06-11._
