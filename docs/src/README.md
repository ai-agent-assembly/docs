# AI Agent Assembly Documentation

AI Agent Assembly is a governance layer for AI agents. Use this hub to evaluate its boundaries, integrate a governed path, operate it, or verify a claim.

**Release candidate** — see the [compatibility matrix](compatibility.md) for component versions.

## Find what you need

Pick the page that matches what you are trying to do.

| I want to… | Go to |
|---|---|
| Govern an agent right now (runnable today) | [Runnable examples](#runnable-examples) |
| Read the design preview for managed SaaS onboarding (planned, not available) | [Managed SaaS onboarding](quickstart-saas.md) |
| Understand the security posture and threat model | [Security model](security-model.md) |
| Compare AI Agent Assembly to other tools | [Why AI Agent Assembly?](comparison.md) |
| Know what is open source vs. paid | [Open core boundary](open-core-boundary.md) |
| See what the managed control plane is intended to add (planned, not available) | [Managed control plane](cloud-deployment.md) |
| Look up a policy field or write a policy | [Policy reference](policy-reference.md) |

## Who this documentation is for

This site is for **teams, security engineers, and operators** evaluating or running AI Agent Assembly for production adoption.

If you are a developer who wants to contribute or integrate at the code level, see the [open-source documentation](https://docs.agent-assembly.com/core/) instead.

For scope and availability, read [What ships today](what-ships-today.md), [Choose your enforcement path](choose-your-enforcement-path.md), and [Capability status](capability-status.md).

Governance applies per agent, on the paths you wire up — you do not have to rewrite your agent's logic, but each agent has to be launched through a governed path (an SDK your code initializes, or the sidecar proxy). An agent started outside those paths is not governed. See [Known limitations](https://docs.agent-assembly.com/core/latest/devtools/limitations.html) for what is measured, unmeasured, and unsupported today.

## SDKs & components

<!-- BEGIN GENERATED:hub-components:landing-badges -->

[![core](https://img.shields.io/github/v/release/ai-agent-assembly/agent-assembly?include_prereleases&sort=semver&label=core&logo=github&color=3b82f6)](https://github.com/ai-agent-assembly/agent-assembly/releases)
[![python-sdk](https://img.shields.io/pypi/v/agent-assembly?label=python-sdk&logo=pypi)](https://github.com/ai-agent-assembly/python-sdk)
[![node-sdk](https://img.shields.io/npm/v/@agent-assembly/sdk/rc?label=node-sdk&logo=npm)](https://github.com/ai-agent-assembly/node-sdk)
[![go-sdk](https://img.shields.io/github/v/tag/ai-agent-assembly/go-sdk?sort=semver&label=go-sdk&logo=go&color=3b82f6)](https://github.com/ai-agent-assembly/go-sdk/tags)
[![license](https://img.shields.io/badge/license-Apache--2.0-green)](https://github.com/ai-agent-assembly/docs/blob/main/LICENSE)

<!-- END GENERATED:hub-components:landing-badges -->

<!-- Generated badges remain owned by hub-components.toml and its renderer. -->

Every version badge reads the latest published version live — core and Go from GitHub, Python from PyPI, Node from npm's `rc` dist-tag — so they stay current with no manual updates.

This hub is the central entry point for AI Agent Assembly documentation. To instrument your agents, you install the SDK for your language — each one ships its own documentation site. Use the table below to go to the SDK that matches your codebase (Python, Node/TypeScript, or Go), or to Arena, the cross-framework governance trial ground.

Every module's docs are **aggregated into this hub** under a stable subpath (`/core/`, `/python-sdk/`, `/node-sdk/`, `/go-sdk/`, `/arena/`), so you can read and search all of them from one place. The standalone, per-version sites remain available for release-specific (mike / Docusaurus / Hugo channel) browsing.

<!-- BEGIN GENERATED:hub-components:sdks-and-components -->

| Component | On this hub | Standalone site |
|---|---|---|
| Core (monorepo) | [/core/](/core/) | [core docs](https://docs.agent-assembly.com/core/) |
| Python SDK | [/python-sdk/](/python-sdk/) | <https://docs.agent-assembly.com/python-sdk/> |
| Node SDK | [/node-sdk/](/node-sdk/) | <https://docs.agent-assembly.com/node-sdk/> |
| Go SDK | [/go-sdk/](/go-sdk/) | <https://docs.agent-assembly.com/go-sdk/> |
| Arena | [/arena/](/arena/) | <https://docs.agent-assembly.com/arena/> |

<!-- END GENERATED:hub-components:sdks-and-components -->

<!-- The table above is generated from hub-components.toml by
     docs/scripts/generate_hub_components.py — do not hand-edit between the
     BEGIN/END GENERATED markers. See AAASM-4313. -->

## Runnable examples

Prefer learning by running code? The
[**examples**](https://github.com/ai-agent-assembly/examples)
repo collects small, framework-specific Agent Assembly examples for Python,
Node.js/TypeScript, Go, policy enforcement, approvals, audit, trace, and runtime
workflows. Clone it and run an example end to end to see governance in action
before instrumenting your own agents.

## The interception mechanisms

Governance is assembled from independently-deployable interception mechanisms, and a deployment runs whichever subset it installs. They are **not** a fallback chain and **not** a ranking: each reaches a different claim level, and a mechanism you do not deploy is reported as absent rather than picked up by another. The numbering below is presentational and implies no order of precedence:

1. **SDK layer (in-process)** — the language SDK wraps your agent's framework tool calls and raises on a deny before the wrapped call runs. Fastest path, but **advisory**: it requires you to adopt the SDK and call its initializer, a non-cooperating process simply never calls it, and it does not intercept raw HTTP, subprocess spawns, or file access. Treat it as defense-in-depth, not the gate.
2. **Sidecar proxy (`aa-proxy`)** — intercepts outbound HTTP/1.1 that is routed to it, using per-host certificates minted from a local root CA, so it can govern agents that do not use the SDK. No *agent code* changes, but the process must honour `HTTP_PROXY`/`HTTPS_PROXY` and trust the CA (on macOS the install is *attempted* at proxy start via `security add-trusted-cert`, which requires admin authorization — macOS prompts, and a refusal fails proxy startup; on Linux run `sudo aasm proxy install-ca`; Windows is unsupported). On MitM'd hosts, HTTP/2, gRPC, and WebSocket cannot be inspected — on other hosts they are tunnelled uninspected.
3. **eBPF sensor (`aa-ebpf`)** — kernel hooks that watch OpenSSL and process syscalls. **Observe-only**: it reports what it sees and is consulted in no allow/deny decision, so its claim level is *Observed* and *Detected* — never prevention. It does not block, and it is not a mechanism the others fall back to. Linux only (the file-I/O kprobes are x86_64-only), and it degrades rather than failing closed if it cannot attach.

Each mechanism reports to the **gateway**, which evaluates policy and tracks per-team budgets. Coverage is the union of the layers you deploy, bounded by each layer's own precondition — see [Known limitations](https://docs.agent-assembly.com/core/latest/devtools/limitations.html).

These interception points describe *where* a decision is applied; they sit inside the **Boundary** layer of the broader [five-layer defense model](security-model.md), which describes *what* is protected. Same system, two views.

<div class="aa-cta-next">
  <span class="aa-cta-next__label">Next step</span>
  <a href="https://github.com/ai-agent-assembly/examples?utm_source=docs&amp;utm_medium=docs_link&amp;utm_campaign=oss_install&amp;utm_content=landing_next_step" data-cta-location="body" rel="noopener">Run a governed example →</a>
  <p>Clone the <code>examples</code> repo and run a governed LangChain
     agent end to end — the path you can run today. The managed control
     plane is <a href="quickstart-saas.md">planned, not available</a>.</p>
</div>

---

*Last reviewed: 2026-06-27 — AI Agent Assembly Team*
