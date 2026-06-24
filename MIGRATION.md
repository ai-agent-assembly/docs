# Legacy Docs Redirect / Migration Plan (AAASM-3665)

Today each module's documentation is served from its own GitHub Pages site:

| Legacy URL | New canonical URL (on the hub) |
|---|---|
| `https://ai-agent-assembly.github.io/agent-assembly-docs/` | `https://docs.agent-assembly.com/` |
| `https://ai-agent-assembly.github.io/agent-assembly/` | `https://docs.agent-assembly.com/core/` |
| `https://ai-agent-assembly.github.io/python-sdk/` | `https://docs.agent-assembly.com/python-sdk/` |
| `https://ai-agent-assembly.github.io/node-sdk/` | `https://docs.agent-assembly.com/node-sdk/` |
| `https://ai-agent-assembly.github.io/go-sdk/` | `https://docs.agent-assembly.com/go-sdk/` |

This document is the plan for pointing those legacy sites at the new aggregated
hub once `docs.agent-assembly.com` is live. **The live cut-over is owner-gated**
(it needs the custom domain attached and changes pushed into the four SDK repos,
which is out of scope for this hub-only PR).

## Strategy: `rel=canonical` + redirect stub, not hard deletion

We keep the legacy sites reachable but **demote them in search and forward
visitors**, rather than deleting them (deletion would break every existing
inbound link and bookmark):

1. **`rel=canonical`** — every legacy page advertises the matching hub URL as its
   canonical, so search engines consolidate ranking onto `docs.agent-assembly.com`.
2. **Redirect stub** — the legacy site root (and, where cheap, key pages) serves a
   small HTML stub that forwards to the corresponding hub subpath. The modules
   already ship a site-root redirect-stub pattern (e.g. core's
   `docs/site-root-index.html`, go-sdk's `website/redirect/index.html`) that
   reads the channel and forwards — these are the natural insertion points: change
   their target from the channel subpath to the hub subpath.

Example stub (no-JS fallback + JS redirect, mirroring the existing module stubs):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <link rel="canonical" href="https://docs.agent-assembly.com/python-sdk/" />
  <meta http-equiv="refresh" content="0; url=https://docs.agent-assembly.com/python-sdk/" />
  <title>Moved → docs.agent-assembly.com/python-sdk/</title>
</head>
<body>
  <p>This documentation has moved to
     <a href="https://docs.agent-assembly.com/python-sdk/">docs.agent-assembly.com/python-sdk/</a>.</p>
  <script>location.replace("https://docs.agent-assembly.com/python-sdk/" + location.hash);</script>
</body>
</html>
```

(`location.hash` is preserved so deep anchor links survive the hop.)

## Rollout order

Roll out **lowest-risk first**, verifying the hub serves each module before
redirecting that module's legacy site:

1. **Hub goes live** at `docs.agent-assembly.com` (this PR's workflow + owner
   attaches DNS). Verify all five subpaths render and unified search works.
2. **`agent-assembly-docs`** legacy site (`…github.io/agent-assembly-docs/`) →
   redirect to `docs.agent-assembly.com/` first. It is the safest: same repo, same
   content, and the hub *is* its successor.
3. **go-sdk**, then **python-sdk**, then **node-sdk** — add `rel=canonical` to each
   module's docs theme and point its existing root redirect stub at the hub
   subpath. SDKs in ascending order of traffic so any regression is caught on a
   lower-traffic site first.
4. **core** (`…github.io/agent-assembly/`) last — highest traffic and most deep
   links.

At each step: keep the legacy site published (canonical + stub), do **not** delete
it. Only after a deprecation window (suggest ≥1 release cycle) with the hub stable
should the owner consider taking legacy sites down.

## In-repo stubs added in this PR

This PR can only add stubs that live **in this hub repo**. We do not modify the
four SDK repos here (that is owner-gated rollout work). The concrete in-repo
change is on the hub home page: its [component table](docs/src/README.md) now
links the **aggregated** subpaths (`/core/`, `/python-sdk/`, …) as the primary
destination, with the standalone legacy sites kept as a secondary column — so the
hub itself already steers readers to the canonical subpaths.

## Owner-gated items

- Attaching `docs.agent-assembly.com` DNS + GitHub Pages custom domain.
- Adding `rel=canonical` + redirect stubs **inside the four SDK repos** (one small
  PR per repo, per the rollout order above).
- Deciding the deprecation window before any legacy site is taken down.
