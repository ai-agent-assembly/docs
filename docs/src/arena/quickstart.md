# Arena Quickstart

> **Coming soon.** Arena's project skeleton (uv-managed Python package, CLI
> entrypoint, manifest/scenario schemas) is landing in parallel tickets this
> same delivery wave and is not fully wired up yet. This page documents the
> intended flow; it will be updated with verified steps once the runner
> ships.

The intended flow, once the `aasm-arena` CLI lands:

```bash
git clone https://github.com/ai-agent-assembly/arena.git
cd arena
uv sync
uv run aasm-arena --help
```

`aasm-arena` is the intended CLI entrypoint for running scenarios and
inspecting reports locally. Exact subcommands and flags will be documented
here as they land.

See [Submitting an agent](submit-agent.md) to add your own agent plugin, and
[Latest Reports](latest-reports.md) for sample output.
