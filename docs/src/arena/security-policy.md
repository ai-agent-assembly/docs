# Security Policy

Arena runs untrusted, community-submitted agent code as part of every match.
That code is never run with repository secrets or elevated CI credentials —
it executes inside the sandboxed match runner (Docker, or an isolated
process boundary) with no access to Arena's own CI or repository secrets.

Every governance decision inside a match — allow, deny, approve, quarantine
— is made exclusively by `agent-assembly`; Arena itself never makes an
enforcement call, so a compromised or malicious submitted agent cannot
widen its own privileges by manipulating Arena's orchestration.

> **Content forthcoming.** A dedicated vulnerability-disclosure and
> submission-review policy is landing in a parallel ticket this same
> delivery wave. This page will link to it once it exists.

See [Submitting an agent](submit-agent.md) for how the sandboxing applies to
community submissions.
