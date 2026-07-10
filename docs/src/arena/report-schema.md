# Report Schema

Every Arena match produces three artifacts under
`reports/matches/<match-id>/`:

- `arena-report.md` — human-readable match summary.
- `arena-report.json` — the same report in machine-readable form.
- `audit.jsonl` — the raw per-decision audit trail `agent-assembly` recorded
  during the match.

Two deterministic samples, built from the `github-maintainer-dungeon`
scenario, are checked into the [`arena`](https://github.com/ai-agent-assembly/arena)
repo under `docs/samples/` so you can see the actual shape of a report
without running a match yourself: a sample where every trial resolves as
expected (`agent-assembly` wins, zero critical escapes) and a sample where a
prompt-injection trial's direct-push attempt is unexpectedly allowed instead
of denied (`agent-assembly` loses, one critical escape).

> **Content forthcoming.** The full field-by-field JSON schema for
> `arena-report.json` and `audit.jsonl` is landing in a parallel ticket this
> same delivery wave. This page will be updated with the formal schema once
> it ships.
