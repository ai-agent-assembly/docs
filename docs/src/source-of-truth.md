# Source of truth & status

This hub routes across many independently shipped programs and repositories. Not
all of them are public, and not all of them are generally available yet. This
page is the **canonical status map**: for every documented area it records which
repository owns the content, whether that source is public or private/internal,
and whether the area is shipping today, in release candidate, or still planned.

When a page elsewhere in this hub describes a capability, look here first to know
how much weight to put on it.

## Status labels

Every area below is tagged with one visibility label and one maturity label.

**Visibility — where the source lives and who can read it:**

| Label | Meaning |
|---|---|
| 🟢 **Public** | Source repository is public on [github.com/ai-agent-assembly](https://github.com/orgs/ai-agent-assembly/repositories); anyone can read it. |
| 🔒 **Private / internal** | Source repository is private; only the AI Agent Assembly team can read it. Documentation here describes intent, not a browsable codebase. |

**Maturity — how much to trust the described behaviour:**

| Label | Meaning |
|---|---|
| 🧪 **Release candidate** | Ships today as a release candidate; the API and behaviour are stabilizing but may still change before GA. The whole product is currently `v0.0.1-rc`. |
| 🗺️ **Planned** | Designed and documented as intent, but **not yet generally available**. Treat as a roadmap, not a contract. |

## Area status map

| Area | Owning repository | Visibility | Maturity | Where to read |
|---|---|---|---|---|
| **Core** (gateway, policy engine, eBPF, proxy, FFI, WASM, CLI, API) | [`agent-assembly`](https://github.com/ai-agent-assembly/agent-assembly) | 🟢 Public | 🧪 Release candidate | [core docs](https://ai-agent-assembly.github.io/agent-assembly/) |
| **Python SDK** | [`python-sdk`](https://github.com/ai-agent-assembly/python-sdk) | 🟢 Public | 🧪 Release candidate | [python-sdk docs](https://ai-agent-assembly.github.io/python-sdk/) |
| **Node / TypeScript SDK** | [`node-sdk`](https://github.com/ai-agent-assembly/node-sdk) | 🟢 Public | 🧪 Release candidate | [node-sdk docs](https://ai-agent-assembly.github.io/node-sdk/) |
| **Go SDK** | [`go-sdk`](https://github.com/ai-agent-assembly/go-sdk) | 🟢 Public | 🧪 Release candidate | [go-sdk docs](https://ai-agent-assembly.github.io/go-sdk/) |
| **Runnable examples** | [`agent-assembly-examples`](https://github.com/ai-agent-assembly/agent-assembly-examples) | 🟢 Public | 🧪 Release candidate | repo `README` |
| **Homebrew / install channel** | [`homebrew-tap`](https://github.com/ai-agent-assembly/homebrew-tap) | 🟢 Public | 🧪 Release candidate | repo `README` |
| **Specs** (protocol & policy spec) | [`agent-assembly`](https://github.com/ai-agent-assembly/agent-assembly) monorepo | 🟢 Public | 🧪 Release candidate | [Policy reference](policy-reference.md) · core docs |
| **Releases** (versions & compatibility) | this hub + each component's tags | 🟢 Public | 🧪 Release candidate | [Compatibility matrix](compatibility.md) |
| **Cloud** (SaaS control plane) | `agent-assembly-cloud` | 🔒 Private / internal | 🗺️ Planned | [Cloud deployment](cloud-deployment.md) |
| **Enterprise** (SSO, SCIM, advanced audit) | `agent-assembly-enterprise` | 🔒 Private / internal | 🗺️ Planned | [Open core boundary](open-core-boundary.md) |
| **Operations** (running & onboarding) | this hub | 🟢 Public | 🗺️ Planned | [Quick start (SaaS)](quickstart-saas.md) |

> The **protocol specification stays in the `agent-assembly` monorepo** by project
> policy. The reserved `agent-assembly-spec` repository is intentionally not used
> as the spec source.

## Why some areas are private or planned

AI Agent Assembly is **open core, SaaS-only**. The enforcement path — every
interception layer, the policy engine, the SDK shims, and the CLI — is open
source and public. The commercial control plane (Cloud) and the enterprise
operations features (Enterprise) are delivered as a managed SaaS and live in
private repositories; their documentation here describes intended behaviour, not
a browsable codebase. See the [Open core boundary](open-core-boundary.md) for the
full split.

---

*Last reviewed: 2026-06-27 — AI Agent Assembly Team*
