# AI Agent Assembly — Enterprise Documentation

Welcome to the AI Agent Assembly enterprise documentation site.

AI Agent Assembly is a governance-native runtime for AI agents. It enforces policy, tracks costs, and intercepts unsafe actions across your entire AI agent fleet — without changing your existing agent code.

## Who this documentation is for

This site is for **enterprise evaluators, security teams, and operators** assessing AI Agent Assembly for production adoption.

If you are a developer looking to contribute or integrate at the code level, see the [open-source documentation](https://github.com/AI-agent-assembly/agent-assembly/tree/master/docs).

## What you will find here

| Section | Purpose |
|---|---|
| [Security Model](security-model.md) | STRIDE threat analysis, IronClaw five-layer defense, cryptographic primitives |
| [Why AI Agent Assembly?](comparison.md) | Feature comparison against Langfuse, Helicone, Opik, and Pillar Security |
| [Open Core Boundary](open-core-boundary.md) | What is Apache-2.0 licensed vs. proprietary; the open-core business model |
| [Quick Start (SaaS)](quickstart-saas.md) | Zero to governed agent in under 5 minutes using the SaaS platform |
| [Cloud Deployment](cloud-deployment.md) | Tenant provisioning, SSO, billing, and region selection |
| [Policy Reference](policy-reference.md) | Every YAML policy field documented with type, default, and examples |

## The three-layer interception model

AI Agent Assembly enforces governance through three independently deployable layers:

1. **SDK layer (in-process)** — language SDKs wrap your agent calls and enforce pre-execution allow/deny before any network egress occurs.
2. **Sidecar proxy (`aa-proxy`)** — intercepts outbound HTTPS via MitM with a per-host CA, catching anything the SDK misses without code changes.
3. **eBPF sensor (`aa-ebpf`)** — kernel-level hooks watching SSL libraries and process syscalls; catches bypass attempts at the OS level (Linux only).

All three layers report to the gateway, which evaluates policy and tracks per-team budgets.

---

*Last reviewed: 2026-05-10 — AI Agent Assembly Team*
