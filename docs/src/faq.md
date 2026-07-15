# FAQ

Answers to the questions first-time visitors ask before reading any of the
detailed pages. Each answer links to where the topic is covered in full.

## What is AI Agent Assembly, in one sentence?

It is a **governance layer for AI agents**: it sits between your agents and the
outside world and enforces policy, tracks cost, and intercepts unsafe actions
*before* they run. See the [Introduction](README.md) and
[Why AI Agent Assembly?](comparison.md).

## Do I have to change my agent's code?

Not necessarily. There are three interception layers and you can pick how
invasive to be:

- The **SDK layer** needs a small amount of instrumentation in your code and is
  the fastest path.
- The **sidecar proxy** (`aa-proxy`) governs an agent's network traffic with
  **no code change**.
- The **eBPF sensor** (`aa-ebpf`, Linux only) catches actions at the kernel
  level, including bypass attempts.

See the three-layer interception model in the [Introduction](README.md).

## Does it work with my LLM / framework?

Yes — it is provider-agnostic. It governs agents regardless of which model
provider you use, and ships SDKs for **Python, TypeScript/Node, and Go**, with
framework examples (LangChain, LlamaIndex, bare OpenAI, and more) in the
[examples repository](https://github.com/ai-agent-assembly/examples).

## Is it free? What is open source vs. paid?

The enforcement core — the interception layers, policy engine, SDKs, and CLI —
is **open source under Apache-2.0**. Enterprise operations (SSO, SCIM,
tamper-evident audit, dedicated regions, SLAs) are commercial and delivered on
paid SaaS tiers. See the [Open core boundary](open-core-boundary.md).

## Can I self-host it?

You can self-host a **limited-function** stack from the open-source crates
(using the published Docker Compose example) for local evaluation and
development. The **complete** feature set is delivered through the AI Agent
Assembly cloud (SaaS). See the [Open core boundary](open-core-boundary.md).

## How does it actually block an unsafe action?

Before an agent action runs, the gateway evaluates your policy and returns an
allow or deny decision; a deny stops the action. Budgets are enforced the same
way — once a team is over budget, further calls are denied. See the
[Policy reference](policy-reference.md).

## How is it different from an observability / tracing tool?

Observability tools record what an agent *did*, after the fact. AI Agent
Assembly makes a binding **allow/deny decision before the action executes**.
The [comparison page](comparison.md) maps this against other tools.

## Where do I get started right now?

Clone the [examples repository](https://github.com/ai-agent-assembly/examples)
and run a governed agent end to end — that is the path you can run today. The
managed [Quick start (SaaS)](quickstart-saas.md) is coming soon.

## What do the acronyms mean (eBPF, SCIM, mTLS, STRIDE…)?

See the [Glossary](glossary.md), which defines every recurring term and
acronym in plain language.
