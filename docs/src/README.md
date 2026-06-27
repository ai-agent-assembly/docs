# AI Agent Assembly Documentation

[![core](https://img.shields.io/github/v/release/ai-agent-assembly/agent-assembly?include_prereleases&sort=semver&label=core&logo=github&color=3b82f6)](https://github.com/ai-agent-assembly/agent-assembly/releases)
[![python-sdk](https://img.shields.io/pypi/v/agent-assembly?label=python-sdk&logo=pypi)](https://github.com/ai-agent-assembly/python-sdk)
[![node-sdk](https://img.shields.io/npm/v/@agent-assembly/sdk/beta?label=node-sdk&logo=npm)](https://github.com/ai-agent-assembly/node-sdk)
[![go-sdk](https://img.shields.io/github/v/tag/ai-agent-assembly/go-sdk?sort=semver&label=go-sdk&logo=go&color=3b82f6)](https://github.com/ai-agent-assembly/go-sdk/tags)
[![license](https://img.shields.io/badge/license-Apache--2.0-green)](https://github.com/ai-agent-assembly/agent-assembly-docs/blob/main/LICENSE)

Quick links to each component, its current version, and its license. Every version badge reads the latest published version live — core and Go from GitHub, Python from PyPI, Node from npm's `beta` dist-tag — so they stay current with no manual updates. The project is in release candidate (`v0.0.1-rc`).

AI Agent Assembly is a governance layer for AI agents. It sits between your agents and the outside world and does three things:

- **Enforces policy** — decides, before each action runs, whether an agent is allowed to call a tool, reach a domain, or spend more budget.
- **Tracks cost** — meters token and dollar spend per team and blocks agents that exceed their budget.
- **Intercepts unsafe actions** — catches risky calls (and bypass attempts) at the SDK, network, and kernel levels.

It works across your whole fleet of agents and does not require you to rewrite your existing agent code.

## Who this documentation is for

This site is for **teams, security engineers, and operators** evaluating or running AI Agent Assembly for production adoption.

If you are a developer who wants to contribute or integrate at the code level, see the [open-source documentation](https://ai-agent-assembly.github.io/agent-assembly/) instead.

## Find what you need

Pick the page that matches what you are trying to do.

| I want to… | Go to |
|---|---|
| Govern my first agent in a few minutes | [Quick start (SaaS)](quickstart-saas.md) |
| Understand the security posture and threat model | [Security model](security-model.md) |
| Compare AI Agent Assembly to other tools | [Why AI Agent Assembly?](comparison.md) |
| Know what is open source vs. paid | [Open core boundary](open-core-boundary.md) |
| Set up SSO, SCIM, regions, and billing | [Cloud deployment](cloud-deployment.md) |
| Look up a policy field or write a policy | [Policy reference](policy-reference.md) |

## SDKs & components

This hub is the central entry point for AI Agent Assembly documentation. To instrument your agents, you install the SDK for your language — each one ships its own documentation site. Use the table below to go to the SDK that matches your codebase: Python, Node/TypeScript, or Go.

Every module's docs are **aggregated into this hub** under a stable subpath (`/core/`, `/python-sdk/`, `/node-sdk/`, `/go-sdk/`), so you can read and search all of them from one place. The standalone, per-version sites remain available for release-specific (mike / Docusaurus / Hugo channel) browsing.

| Component | On this hub | Standalone site |
|---|---|---|
| Core (monorepo) | [/core/](/core/) | [core docs](https://ai-agent-assembly.github.io/agent-assembly/) |
| Python SDK | [/python-sdk/](/python-sdk/) | <https://ai-agent-assembly.github.io/python-sdk/> |
| Node SDK | [/node-sdk/](/node-sdk/) | <https://ai-agent-assembly.github.io/node-sdk/> |
| Go SDK | [/go-sdk/](/go-sdk/) | <https://ai-agent-assembly.github.io/go-sdk/> |

## Runnable examples

Prefer learning by running code? The
[**agent-assembly-examples**](https://github.com/ai-agent-assembly/agent-assembly-examples)
repo collects small, framework-specific Agent Assembly examples for Python,
Node.js/TypeScript, Go, policy enforcement, approvals, audit, trace, and runtime
workflows. Clone it and run an example end to end to see governance in action
before instrumenting your own agents.

## The three-layer interception model

AI Agent Assembly enforces governance through three layers. You can deploy them independently, and each one catches what the layer above it might miss:

1. **SDK layer (in-process)** — the language SDK wraps your agent calls and applies allow/deny decisions before any network request leaves the process. Fastest path, but requires you to adopt the SDK.
2. **Sidecar proxy (`aa-proxy`)** — intercepts outbound HTTPS using a per-host CA, so it can govern agents that do not use the SDK. No code changes required.
3. **eBPF sensor (`aa-ebpf`)** — kernel-level hooks that watch SSL libraries and process syscalls to catch bypass attempts at the OS level. Linux only.

All three layers report to the **gateway**, which evaluates policy and tracks per-team budgets.

---

*Last reviewed: 2026-06-27 — AI Agent Assembly Team*
