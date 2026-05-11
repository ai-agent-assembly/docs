# Open Core Boundary

AI Agent Assembly follows an **open-core** model. The interception infrastructure, policy engine, SDK shims, and CLI are Apache-2.0 open source. Enterprise features — SSO, SCIM, advanced audit, multi-region data residency — are covered by the AAA-Commercial license and available on paid SaaS tiers.

> **Self-hosted deployment is not available.** Regardless of license, AI Agent Assembly is a SaaS-only product. The Apache-2.0 crates are open source for inspection, contribution, and SDK integration — not for self-hosted deployment. There is no bring-your-own-infrastructure path. See [Cloud Deployment](cloud-deployment.md) and [Quick Start (SaaS)](quickstart-saas.md) for the available onboarding paths.

---

## Why Open Core?

The interception and enforcement infrastructure that sits between AI agents and the outside world must be trustworthy, inspectable, and independently auditable. Keeping the core open source is not a marketing decision — it is a direct consequence of the product's security posture. An enterprise deploying AI agents cannot take our word for how the policy engine evaluates rules, how eBPF probes intercept system calls, or how the sidecar proxy terminates TLS. Open source means the enforcement path can be read, reviewed, and verified by a third party without involving us.

The boundary between what is open and what is commercial follows a single principle: **enforcement is always open; operational convenience and enterprise compliance infrastructure are commercial.** If a feature controls *what agents can do*, it belongs in the Apache-2.0 core. If a feature controls *how operators manage, scale, or audit the system at enterprise grade* — SSO federation, automated user lifecycle via SCIM, long-retention tamper-evident audit logs, multi-region data residency — it belongs in the commercial tier. This principle means that a motivated team can always fork, read, or contribute to every security control in the stack, regardless of their subscription status.

Open-sourcing the core also creates a community feedback loop that makes the enforcement logic stronger over time. Security researchers who find a gap in the policy engine, proxy TLS handling, or eBPF program can open an issue or send a pull request. The Apache-2.0 license was chosen specifically because it permits commercial integration without a copyleft obligation — SDK users can embed the shims in proprietary products without the license propagating to their codebase.

Finally, open core without self-hosting is a deliberate choice. We ship the crates as open source so teams can read, audit, and contribute — not so they can run their own private deployment. Operating a multi-tenant SaaS with the security and reliability commitments described in the [Security Model](security-model.md) requires infrastructure, on-call, and operational expertise that goes far beyond what a compiled binary provides. Keeping deployment SaaS-only lets us uphold the SLA and compliance posture without fragmenting the product across self-managed installs.

---

## Feature Matrix

| Feature | Apache-2.0 (OSS) | AAA-Commercial (Enterprise) |
|---|---|---|
| **Core interception layers** | | |
| Language SDK (Python, TypeScript, Go) | ✅ | ✅ |
| Sidecar proxy (`aa-proxy`) | ✅ | ✅ |
| eBPF sensor (`aa-ebpf`) | ✅ | ✅ |
| **Gateway and policy** | | |
| Agent registry | ✅ | ✅ |
| Policy engine (allow/deny/audit) | ✅ | ✅ |
| Per-team budget enforcement | ✅ | ✅ |
| Policy-as-code (YAML/JSON) | ✅ | ✅ |
| **Authentication and access** | | |
| API key authentication | ✅ | ✅ |
| SAML 2.0 / OIDC SSO | ❌ | ✅ |
| SCIM user provisioning | ❌ | ✅ |
| Role-based access control (RBAC) | Basic | Full (Owner/Admin/Developer/Viewer) |
| **Audit and compliance** | | |
| Basic audit log | ✅ | ✅ |
| Tamper-evident signed audit log | ❌ | ✅ |
| Audit log retention > 30 days | ❌ | ✅ (configurable, up to 1 year) |
| SIEM export (JSON / CEF) | ❌ | ✅ |
| **Deployment and SLA** | | |
| SaaS — shared region | ✅ (Free/Team tier) | ✅ |
| SaaS — dedicated region | ❌ | ✅ (Enterprise tier) |
| Multi-region data residency | ❌ | ✅ |
| 99.9% uptime SLA | ❌ | ✅ (Enterprise tier) |
| Dedicated SRE contact | ❌ | ✅ (Enterprise tier) |
| **Support** | | |
| Community forum | ✅ | ✅ |
| Business-hours support | ❌ | ✅ (Team tier) |
| 24/7 support | ❌ | ✅ (Enterprise tier) |

---

## Crate Licensing

All Cargo crates in the `agent-assembly` workspace are Apache-2.0:

| Crate | License | Notes |
|---|---|---|
| `aa-core` | Apache-2.0 | Core domain types — always OSS |
| `aa-proto` | Apache-2.0 | Protobuf definitions — always OSS |
| `aa-runtime` | Apache-2.0 | Async runtime utilities — always OSS |
| `aa-gateway` | Apache-2.0 | Gateway with policy engine — OSS core; enterprise features gated behind SaaS config |
| `aa-api` | Apache-2.0 | REST API surface — OSS |
| `aa-proxy` | Apache-2.0 | Sidecar proxy — always OSS |
| `aa-ebpf` | Apache-2.0 | eBPF user-space loader — always OSS |
| `aa-ebpf-common` | Apache-2.0 | eBPF shared types — always OSS |
| `aa-ffi-python` | Apache-2.0 | Python SDK native shim — always OSS |
| `aa-ffi-node` | Apache-2.0 | TypeScript SDK native binding — always OSS |
| `aa-ffi-go` | Apache-2.0 | Go SDK CGo shim — always OSS |
| `aa-wasm` | Apache-2.0 | WebAssembly build — always OSS |
| `aa-cli` | Apache-2.0 | `aasm` operator CLI — always OSS |
| `conformance` | Apache-2.0 | Conformance test suite — always OSS |

### Apache 2.0 key terms

The Apache License 2.0 grants users the right to use, reproduce, prepare derivative works, distribute, and sublicense the software with or without modification. It does not grant trademark rights, and it requires preservation of copyright notices and attribution in distributed works. See the full license text at https://www.apache.org/licenses/LICENSE-2.0.

Enterprise features (SSO, SCIM, tamper-evident audit, dedicated regions) are delivered via SaaS-side configuration — not via separate closed-source crates. The OSS codebase contains all interception and enforcement logic.

---

## Contributing to the OSS Core

The Apache-2.0 crates welcome community contributions. See `CONTRIBUTING.md` in the `agent-assembly` repository for:

- Branching and commit conventions
- How to run the test suite (`cargo nextest run --workspace`)
- The CLA requirement for non-trivial contributions
- How to file issues and feature requests

Enterprise feature requests (SSO, SCIM, audit extensions) are tracked as AAASM JIRA tickets in the Enterprise component and delivered by the AI Agent Assembly team.

---

## Related Documentation

- [Security Model](security-model.md) — cryptographic primitives and audit log details
- [Cloud Deployment](cloud-deployment.md) — SSO, SCIM, SLA tier comparison
- [Why AI Agent Assembly?](comparison.md) — open-source posture vs competitors

---

*Last reviewed: 2026-05-10 · Legal approver: @legal-team*
