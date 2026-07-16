# Troubleshooting

This page is a starting point when something is not working the way the docs
describe. It is for **operators and developers** who have already read the
[Quick start](quickstart-saas.md) or an SDK page and hit a specific problem.

Because AI Agent Assembly is composed of four independently versioned
programs (core plus three SDKs), most concrete runtime symptoms are covered
in the owning component's own troubleshooting section. This page routes you
to the right one and lists cross-cutting issues that don't belong to a
single component.

## Common first-run failures

If you are evaluating AI Agent Assembly for the first time, these are the
symptoms newcomers hit most often — each with the exact fix. If your symptom
isn't here, use the component routing table further down.

| Symptom you see | Cause | Fix |
|---|---|---|
| `pip install agent-assembly` → `ERROR: Could not find a version that satisfies the requirement agent-assembly` / `No matching distribution found` | Only **pre-release** versions are published on PyPI right now; `pip` skips pre-releases by default. | Install with the `--pre` flag: `pip install --pre agent-assembly`. |
| On Python 3.13 / 3.14, agent registration appears to do nothing — no events reach the gateway | Older SDK builds had no wheels for CPython 3.13/3.14, so the native extension silently fell back to a no-op. | Upgrade to **rc.4 or later**, which ships `cp313` and `cp314` wheels: `pip install --pre --upgrade agent-assembly`. Confirm your interpreter with `python --version`. |
| SDK cannot reach the gateway even though a gateway is running | Connecting to the wrong port/protocol — the SDKs speak **gRPC on `50051`**, while the REST/OpenAPI surface (used by the dashboard and `curl` health checks) is **HTTP on `8080`**. | Point the SDK at the gRPC endpoint (`50051`), not the REST port. For a fully local loop with no external gateway, run one yourself: `aasm start` brings up a local gateway the SDK can register against. |
| `ImportError` / `ModuleNotFoundError` for `AgentExecutor` or `create_react_agent` when running a LangChain example | Recent LangChain moved these legacy agent constructors out of the top-level `langchain` package into the `langchain_classic` package. | Import from the new location: `from langchain_classic.agents import AgentExecutor, create_react_agent` (and `pip install langchain-classic` if it isn't already present). |

## Where component-specific troubleshooting lives

| Symptom | Look here |
|---|---|
| SDK cannot register the agent / handshake fails | [Python SDK docs](https://docs.agent-assembly.com/python-sdk/), [Node SDK docs](https://docs.agent-assembly.com/node-sdk/), [Go SDK docs](https://docs.agent-assembly.com/go-sdk/) |
| Sidecar proxy (`aa-proxy`) drops connections | [Core docs](https://docs.agent-assembly.com/core/) — Proxy section |
| eBPF sensor (`aa-ebpf`) fails to load | [Core docs](https://docs.agent-assembly.com/core/) — eBPF section |
| Policy YAML rejected at gateway | [Policy reference](policy-reference.md) |
| Compatibility mismatch between core and an SDK | [Compatibility matrix](compatibility.md) |

## Cross-cutting checks

Before opening an issue, verify:

- The SDK version matches a supported core version — see the
  [Compatibility matrix](compatibility.md).
- The workspace ID and API key are set in the environment (`AAA_WORKSPACE_ID`,
  `AAA_API_KEY`) — an unset credential is the most common cause of
  "agent registration failed".
- The gateway URL is reachable from the host running the agent
  (`https://api.agent-assembly.com` by default).
- The clock on the agent host is not skewed by more than a few minutes —
  Ed25519-signed agent tokens have a bounded TTL and reject skewed
  timestamps.

## Still stuck? Open an issue

If none of the routes above resolve the problem, open a GitHub issue on the
owning repository — the core team monitors each repo's issue tracker and
routes docs bugs back here.

<div class="aa-cta-next">
  <span class="aa-cta-next__label">Still stuck?</span>
  <a href="https://github.com/ai-agent-assembly/agent-assembly/issues/new/choose" data-cta-location="body" rel="noopener">Open a GitHub issue on the core repo →</a>
  <p>Include the SDK version, core version, and a minimal reproducer. Docs bugs
     can be filed on <a href="https://github.com/ai-agent-assembly/docs/issues/new/choose" data-cta-location="body" rel="noopener">this repo's tracker</a> instead.</p>
</div>

---

*Last reviewed: 2026-07-09 — AI Agent Assembly Team*
