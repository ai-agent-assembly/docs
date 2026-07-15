# Glossary

Plain-language definitions of the terms and acronyms used across this
documentation. It exists so a first-time or non-specialist reader can decode
the security and architecture jargon without leaving the page they are on.

## Product concepts

**AI Agent Assembly (AAASM)**
: The product this hub documents: a governance layer that sits between your AI
agents and the outside world and enforces policy, tracks cost, and intercepts
unsafe actions before they run.

**Governance layer**
: The one-line description of what AI Agent Assembly *is* — a control that
evaluates and enforces what an agent is allowed to do, rather than only
observing what it did after the fact.

**Gateway (`aa-gateway`)**
: The central service that holds the agent registry, evaluates policy, and
tracks per-team budgets. Every interception layer reports to it.

**Agent**
: An autonomous or semi-autonomous program that calls tools, models, or
network services on your behalf — the thing AI Agent Assembly governs.

**Policy**
: A set of allow / deny / audit rules that decide whether an agent action is
permitted. See the [Policy reference](policy-reference.md).

**Policy-as-code**
: Expressing those rules as versioned YAML/JSON documents that can be reviewed
and deployed through normal Git workflows, instead of clicking through a UI.

**Budget**
: A per-team cap on token or dollar spend. When exceeded, the gateway can deny
further agent calls.

## Interception layers

**SDK layer**
: In-process governance: the language SDK wraps your agent's calls and applies
allow/deny decisions before any request leaves the process.

**Sidecar proxy (`aa-proxy`)**
: A companion process that intercepts an agent's outbound HTTPS traffic to
enforce policy without changing the agent's code.

**eBPF sensor (`aa-ebpf`)**
: A kernel-level sensor (Linux only) that watches TLS libraries and process
syscalls to catch actions — and bypass attempts — that the layers above miss.

## Security & identity terms

**eBPF** (extended Berkeley Packet Filter)
: A Linux kernel technology for safely running small sandboxed programs inside
the kernel to observe or filter events, without modifying kernel source.

**uprobe** (user-space probe)
: An eBPF hook attached to a function in a user-space library (for example, an
SSL library) so the sensor can observe calls at that point.

**Sidecar**
: A deployment pattern where a helper process runs alongside your application
and handles a cross-cutting concern (here, traffic interception).

**MitM** (man-in-the-middle)
: Sitting in the path of a connection to inspect or control it. The proxy
performs *authorized* MitM of an agent's HTTPS using a per-host certificate
authority so it can apply egress policy.

**mTLS** (mutual TLS)
: TLS where **both** the client and the server present certificates, so each
side cryptographically verifies the other's identity.

**STRIDE**
: A threat-modeling framework categorizing risks as Spoofing, Tampering,
Repudiation, Information disclosure, Denial of service, and Elevation of
privilege. Used in the [Security model](security-model.md).

**SCIM** (System for Cross-domain Identity Management)
: A standard protocol for automatically provisioning and de-provisioning users
and groups from your identity provider into an application.

**SSO / SAML 2.0 / OIDC**
: Single sign-on and the two federation protocols (SAML 2.0 and OpenID
Connect) used to let operators log in with an enterprise identity provider.

**Ed25519**
: A modern public-key signature algorithm, used here to sign agent identity
tokens.

**AES-256-GCM**
: A symmetric authenticated-encryption algorithm, used here to encrypt stored
secrets at rest.

**HMAC-SHA256**
: A keyed hash used to sign audit-log entries and webhook payloads so
tampering is detectable.

**IronClaw five-layer defense**
: The name for AI Agent Assembly's defense-in-depth model — five security
*layers* (Boundary, Identity, Policy, Vault, Telemetry). These are distinct
from the three *interception points* (SDK, proxy, eBPF), which all live inside
the Boundary layer. See the [Security model](security-model.md).

**Audit log**
: The append-only, tamper-evident record of every agent action (policy checks,
events, budget debits).
