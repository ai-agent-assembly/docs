# Arena

Arena is the public trial ground for agent-assembly governance. Agents enter,
agent-assembly defends, and every match leaves a report.

Arena is a public, plug-in based proving ground for
[agent-assembly](https://ai-agent-assembly.github.io/agent-assembly/)
governance — it is **not** another agent framework, and it does **not**
reimplement agent-assembly's governance logic. AI agents built on different
frameworks (LangGraph, CrewAI, PydanticAI, AutoGen, raw Python, and others)
enter controlled scenarios and attempt normal work alongside deliberate
boundary violations — prompt injection, secret leaks, destructive shell
commands, unapproved releases. `agent-assembly` is the sole governance
defender: it makes every allow/deny/approve/quarantine decision. Arena only
orchestrates the match, runs the scenario, records what happened, and
publishes the report.

## Arena vs. examples

Don't confuse Arena with
[`examples`](https://github.com/ai-agent-assembly/examples), the sibling repo
already linked from this hub:

- **`examples`** is small, instructional, happy-path runnable samples that
  show how to *integrate* agent-assembly into your own agent code — copy
  these into a real project.
- **`arena`** is cross-framework governance trials: adversarial scenarios,
  behavior profiles, deterministic mock/replay agents, and published match
  reports. Arena answers "does agent-assembly actually hold up under
  attack?", not "how do I wire this up?"

## What Arena is (and isn't)

- Arena **is** an orchestrator: it loads agent plugins via manifest, runs
  them through scenario/trial definitions, and captures the resulting
  decisions and outcomes into a report.
- Arena **is not** a new agent framework — it provides no agent runtimes,
  planning loops, or tool-calling abstractions; agents bring their own
  framework of choice and plug in.
- Arena **is not** a governance engine. It never makes an allow/deny/approve/
  quarantine call itself; every enforcement decision comes from
  `agent-assembly`, and Arena treats those decisions as the source of truth
  when it records them.

## Status

Arena ships as its own public, independent repository:
[ai-agent-assembly/arena](https://github.com/ai-agent-assembly/arena). Most
of its detailed documentation — behavior profiles, LLM modes, the report
schema, and published match reports — is landing across a series of parallel
tickets in this same delivery wave. See the
[Source of Truth & Status](../source-of-truth.md) page for the current
maturity label; the pages under this section will fill in as that content
ships.

## Next steps

- [Quickstart](quickstart.md) — clone the repo and run your first match.
- [Submitting an agent](submit-agent.md) — how to add your own agent plugin.
- [Report Schema](report-schema.md) — the shape of a match report.
