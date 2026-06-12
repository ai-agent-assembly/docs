# Why AI Agent Assembly?

**AI Agent Assembly is a security and governance control for AI agents** — a runtime that sits in the agent's action path and *enforces* policy, blocking unsafe tool calls, network egress, and budget overruns *before* they execute. Think of it as a security checkpoint in front of every agent action, not a dashboard that reports on actions after they happen. That category distinction is what this comparison is about.

This page helps readers see where AI Agent Assembly fits next to other tools in the AI governance and observability space. All competitor data is taken from each vendor's public documentation as of 2026-05-05.

In short: most tools in this space **observe** what an agent did after the fact. AI Agent Assembly is built to **enforce** policy before an action runs. The sections below show where that difference matters, and where competitors are ahead.

---

## Feature matrix

Because AI Agent Assembly is an **enforcement** control rather than a pure observability or monitoring tool, the rows below span both categories: the observability rows show that it still gives you the visibility those tools provide, while the policy-enforcement, access-control, and budget-enforcement rows show the security-checkpoint capabilities that monitoring-only tools do not have. Read the matrix with that framing — equal coverage on observability, decisive coverage on enforcement.

Each row is a capability. The columns are AI Agent Assembly (AAASM), Langfuse, Helicone, Opik, and Pillar Security.

Legend: ✓ = full support · partial = limited or gated behind a paid tier · ✗ = not available · n/a = not applicable to the product category.

| Capability | AAASM | Langfuse | Helicone | Opik | Pillar Security |
|---|---|---|---|---|---|
| **Observability** | | | | | |
| LLM call tracing (latency, tokens, cost) | ✓ | ✓ | ✓ | ✓ | partial |
| Multi-turn conversation tracing | ✓ | ✓ | partial | ✓ | ✗ |
| Agent lineage / parent-child spans | ✓ | ✓ | ✗ | partial | ✗ |
| SIEM export (JSON / CEF) | ✓ | ✗ | ✗ | ✗ | partial |
| **Policy enforcement** | | | | | |
| Pre-execution allow / deny (runtime block) | ✓ | ✗ | ✗ | ✗ | partial |
| Policy-as-code (YAML / JSON versioned rules) | ✓ | ✗ | ✗ | ✗ | ✗ |
| Network-level interception (no code change) | ✓ (aa-proxy) | ✗ | ✗ | ✗ | ✗ |
| Kernel-level bypass detection (eBPF) | ✓ | ✗ | ✗ | ✗ | ✗ |
| PII / secret detection at gateway | ✓ (regex rules) | partial (post-hoc) | ✗ | partial (evaluators) | ✓ |
| **Vault-backed secrets management** | | | | | |
| Secrets vault integration | ✗ | ✗ | ✗ | ✗ | ✓ |
| Secret scanning in prompts / outputs | partial (regex policy) | ✗ | ✗ | ✗ | ✓ |
| **Multi-language SDK** | | | | | |
| Python SDK | ✓ | ✓ | ✓ | ✓ | ✓ |
| TypeScript SDK | ✓ | ✓ | ✓ | ✓ | partial |
| Go SDK | ✓ | ✗ | ✗ | ✗ | ✗ |
| **BYO-LLM (provider agnostic)** | | | | | |
| Works with any LLM provider | ✓ | ✓ | ✓ | ✓ | ✓ |
| Open-source SDK core (Apache-2.0) | ✓ | ✓ (MIT) | ✗ | ✓ (Apache-2.0) | ✗ |
| **Access control (RBAC)** | | | | | |
| Role-based access control | ✓ (Owner/Admin/Developer/Viewer) | partial | partial | partial | ✓ |
| SAML 2.0 / OIDC SSO | ✓ | partial (Enterprise) | partial (Enterprise) | partial (Enterprise) | ✓ |
| SCIM user provisioning | ✓ | ✗ | ✗ | ✗ | partial |
| **Approval workflows** | | | | | |
| Human-in-the-loop approval gates | partial (policy deny + alerting) | ✗ | ✗ | ✗ | ✓ |
| Automated approval routing | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Cost analytics** | | | | | |
| Per-team token / cost budgets (enforced) | ✓ | partial (tracking only) | ✓ (tracking + alerts) | partial (tracking only) | ✗ |
| Budget enforcement (hard deny on exceed) | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Audit log immutability** | | | | | |
| Immutable audit log with tamper-evident signatures | ✓ (HMAC-SHA256) | ✗ | ✗ | ✗ | partial |
| Audit log retention > 30 days | ✓ (up to 1 year, Enterprise) | partial (30 days free) | partial | partial | ✓ |
| **On-premises / self-hosted option** | | | | | |
| Self-hosted deployment | ✗ (SaaS only) | ✓ | ✗ (SaaS only) | ✓ | ✓ |

---

## Where we currently lag

These are capabilities competitors offer that AI Agent Assembly does not yet fully deliver.

1. **Vault-backed secrets management** — Pillar Security provides first-class secrets vault integration with automatic secret rotation and injection. AAASM currently supports secret-pattern detection via regex policies but does not integrate with HashiCorp Vault or AWS Secrets Manager.
2. **Automated human-in-the-loop approval workflows** — Pillar Security provides structured approval routing with escalation chains. AAASM can deny and alert but does not yet route decisions to a named approver queue.
3. **Self-hosted deployment** — Langfuse, Opik, and Pillar Security all support self-hosted deployment. AAASM is SaaS-only in this release; self-hosted is out of scope for the current roadmap (see [Open Core Boundary](open-core-boundary.md)).
4. **Evaluation frameworks and LLM-as-judge scoring** — Langfuse and Opik provide built-in evaluation pipelines, dataset management, and automated LLM-as-judge scoring for output quality. AAASM's policy engine operates on patterns and metadata, not semantic quality.
5. **Prompt management and versioning** — Langfuse provides a managed prompt registry with version history and A/B comparison. AAASM does not include a prompt registry.

---

## Where we lead

These are capabilities where AI Agent Assembly is uniquely strong or differentiated.

1. **Pre-execution runtime enforcement** — AAASM is the only product in this comparison that makes binding allow/deny decisions *before* an agent action executes. All others are observability tools that record what happened after the fact.
2. **Kernel-level bypass detection via eBPF** — `aa-ebpf` intercepts TLS calls at the SSL library level using Linux uprobes, catching bypass attempts that SDK-only solutions cannot see. No competitor in this matrix offers kernel-level enforcement.
3. **Network-layer interception without code changes** — `aa-proxy` performs MitM HTTPS interception via a per-host CA. Governance can be applied to agents that do not use the SDK. No competitor supports sidecar-proxy-level enforcement.
4. **Policy-as-code with GitOps workflow** — AAASM policies are YAML/JSON documents that can be versioned, reviewed, and deployed via standard Git workflows. No competitor in this matrix offers a structured policy language; guardrails in other tools are typically configured through UI forms or proprietary DSLs.
5. **Immutable tamper-evident audit log** — AAASM's audit log entries are signed with HMAC-SHA256, making post-hoc alteration detectable. This is a compliance requirement in regulated industries (PCI-DSS, SOC 2 Type II) that no competitor in this matrix fully addresses.

---

## Competitor documentation references

Last validated 2026-05-05 against each vendor's documentation as of that date.

| Competitor | Documentation URL |
|---|---|
| Langfuse | https://langfuse.com/docs |
| Helicone | https://docs.helicone.ai |
| Opik | https://www.comet.com/docs/opik |
| Pillar Security | https://docs.pillar.security |

---

## Related documentation

- [Security model](security-model.md) — STRIDE threat model, IronClaw defense
- [Open core boundary](open-core-boundary.md) — what is OSS vs. enterprise
- [Quick start (SaaS)](quickstart-saas.md) — get started in minutes

---

*Last reviewed: 2026-06-11 — AI Agent Assembly Team*
