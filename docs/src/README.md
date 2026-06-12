# AI Agent Assembly — enterprise documentation

AI Agent Assembly is a governance layer for AI agents. It sits between your agents and the outside world and does three things:

- **Enforces policy** — decides, before each action runs, whether an agent is allowed to call a tool, reach a domain, or spend more budget.
- **Tracks cost** — meters token and dollar spend per team and blocks agents that exceed their budget.
- **Intercepts unsafe actions** — catches risky calls (and bypass attempts) at the SDK, network, and kernel levels.

It works across your whole fleet of agents and does not require you to rewrite your existing agent code.

## Who this documentation is for

This site is for **enterprise evaluators, security teams, and operators** assessing AI Agent Assembly for production adoption.

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

This hub is the central entry point for AI Agent Assembly documentation. To instrument your agents, you install the SDK for your language — each one ships its own documentation site. Use the table below to go to the SDK that matches your codebase: Python, Node/TypeScript, or Go. Every link points at the component's site root, which always redirects to its newest **stable** release (falling back gracefully before the first 1.0), so these references never need maintenance.

| Component | Documentation |
|---|---|
| Core (monorepo) | <https://ai-agent-assembly.github.io/agent-assembly/> |
| Python SDK | <https://ai-agent-assembly.github.io/python-sdk/> |
| Node SDK | <https://ai-agent-assembly.github.io/node-sdk/> |
| Go SDK | <https://ai-agent-assembly.github.io/go-sdk/> |

## The three-layer interception model

AI Agent Assembly enforces governance through three layers. You can deploy them independently, and each one catches what the layer above it might miss:

1. **SDK layer (in-process)** — the language SDK wraps your agent calls and applies allow/deny decisions before any network request leaves the process. Fastest path, but requires you to adopt the SDK.
2. **Sidecar proxy (`aa-proxy`)** — intercepts outbound HTTPS using a per-host CA, so it can govern agents that do not use the SDK. No code changes required.
3. **eBPF sensor (`aa-ebpf`)** — kernel-level hooks that watch SSL libraries and process syscalls to catch bypass attempts at the OS level. Linux only.

All three layers report to the **gateway**, which evaluates policy and tracks per-team budgets.

---

*Last reviewed: 2026-06-11 — AI Agent Assembly Team*
