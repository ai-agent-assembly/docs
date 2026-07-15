# Self-host observability

This page is for **operators and SREs running the limited-function OSS stack** — the [self-hostable Apache-2.0 crates](open-core-boundary.md) you can bring up locally (via the published Docker Compose example) for evaluation and development. It answers the operator's first question — *"can I monitor what I run?"* — by showing where the shipped binaries expose their liveness/readiness probes and their Prometheus metrics, so you can wire up a health check and a scrape target **without reading the Rust source**.

> **Scope: this is the limited-function self-host stack, not the managed SaaS.** The uptime SLAs (99.5% / 99.9%), on-call rotation, and managed compliance posture described in [Cloud Deployment](cloud-deployment.md) apply to the **AI Agent Assembly cloud only** — not to a stack you self-host. Self-hosting is intended for local evaluation and development; you are responsible for operating and monitoring it. This page documents the observability surface the OSS binaries already expose; it is **not** a production deployment or orchestration guide (no Helm / Terraform / Kubernetes).

---

## What the stack exposes

Three separate binaries each expose their own HTTP surface for health and metrics. They are distinct servers on distinct paths — do not assume one path works everywhere.

| Component | Surface | Default endpoint(s) | Purpose |
|---|---|---|---|
| **`aa-runtime`** | Health + metrics HTTP server | `/health`, `/ready`, `/metrics` on `AA_METRICS_ADDR` (default `0.0.0.0:8080`) | Liveness, readiness, and the Prometheus scrape target |
| **`aa-gateway`** | Liveness probe | `/healthz` | Process-liveness for the gateway (local and remote modes) |
| **`aa-api`** | Health check | `/api/v1/health` | REST API health, including per-subsystem checks |

The rest of this page covers each surface and gives copy-paste probe and scrape examples.

---

## Health and readiness probes

### `aa-runtime` — `/health` and `/ready`

The runtime runs a combined health/metrics HTTP server bound to `AA_METRICS_ADDR` (see [Metrics endpoint](#prometheus-metrics-endpoint) below for the env var and its default). It serves two probe routes:

- **`GET /health`** — liveness. Returns `200 OK` with a JSON body reporting `status`, process uptime, events processed, and which enforcement layers are active or degraded. Use this as a liveness probe.
- **`GET /ready`** — readiness. Returns `200 OK` (body `ready`) once the runtime is ready to accept work, or `503 Service Unavailable` (body `not ready`) before then. Use this as a readiness/startup gate.

```console
$ curl -fsS http://localhost:8080/health
{"status":"healthy","uptime_secs":42, ...}

$ curl -fsS http://localhost:8080/ready
ready
```

### `aa-gateway` — `/healthz`

The gateway exposes a process-liveness probe at **`GET /healthz`** in both of its run modes. It returns `200 OK` with a small JSON body as long as the gateway is responding to HTTP:

- **local mode** reports `mode: "local"` with SQLite-backed storage (local mode also mounts `/api/v1/health`).
- **remote mode** reports `mode: "remote"` with `postgres` or in-memory storage depending on how it is configured.

```console
$ curl -fsS http://localhost:<gateway-port>/healthz
{"mode":"local","version":"...","storage":"sqlite","uptime_secs":...}
```

The gateway's HTTP port depends on how you launch it in the Docker Compose example — check your compose file's port mapping rather than assuming a fixed value.

### `aa-api` — `/api/v1/health`

The REST API exposes a health check at **`GET /api/v1/health`** (all API routes are nested under `/api/v1/`). It returns `200 OK` when every subsystem check passes, or `503 Service Unavailable` when any is degraded. The JSON body includes the build `version`, `api_version`, uptime, and a `checks` map with per-subsystem status for the policy engine, registry, audit, and alerts.

```console
$ curl -fsS http://localhost:<api-port>/api/v1/health
{"status":"ok","version":"...","api_version":"v1","checks":{"policy_engine":"ok", ...}}
```

---

## Prometheus metrics endpoint

The `aa-runtime` health/metrics server exposes a Prometheus text-format scrape endpoint.

| Setting | Value |
|---|---|
| Env var | `AA_METRICS_ADDR` |
| Default bind address | `0.0.0.0:8080` |
| Metrics path | `/metrics` |
| Scrape target | `http://<runtime-host>:8080/metrics` (with the default bind address) |

`AA_METRICS_ADDR` is the single environment variable that controls this server's bind address; the same server serves `/health`, `/ready`, and `/metrics`. Set it to change the interface or port, e.g. `AA_METRICS_ADDR=127.0.0.1:9090` to bind loopback only. (`0.0.0.0` is a *bind* address — point your scraper at a routable host/IP for the runtime, not at `0.0.0.0`.)

```console
$ curl -fsS http://localhost:8080/metrics
# Prometheus text exposition format
aa_events_received_total 0
aa_events_emitted_total 0
...
```

### Baseline metrics

The runtime pre-registers six baseline metrics at `0` on startup, so the `/metrics` surface is **stable from the very first scrape** (a metric never "appears late" the first time it is incremented). The names and types below are taken directly from the runtime source; the "What it represents" column is explanatory (the source registers names and types only, without HELP text). Additional metrics may appear as the runtime does work.

| Metric | Type | What it represents |
|---|---|---|
| `aa_events_received_total` | counter | Governance events the runtime has received |
| `aa_events_emitted_total` | counter | Events the runtime has emitted downstream |
| `aa_policy_violations_total` | counter | Policy violations observed |
| `aa_policy_evaluations_total` | counter | Policy evaluations performed (currently reports `0`; reserved for a forthcoming release) |
| `aa_active_connections` | gauge | Currently active connections |
| `aa_channel_utilization_ratio` | gauge | Internal channel utilization ratio |

> **Note:** these six are the *baseline* surface. Only `aa_active_connections` and `aa_channel_utilization_ratio` are gauges; the other four are counters. None are histograms. Because they start at `0`, an all-zero scrape shortly after startup is expected, not a sign of a broken exporter.

### Minimal scrape configuration

Point a Prometheus server at the runtime's metrics endpoint. A minimal `prometheus.yml` scrape job:

```yaml
scrape_configs:
  - job_name: aa-runtime
    metrics_path: /metrics
    static_configs:
      - targets: ["<runtime-host>:8080"]   # matches AA_METRICS_ADDR's port
```

Replace `<runtime-host>` with the address where the runtime is reachable (for the Docker Compose example, the runtime service's name/port on the compose network). If you override `AA_METRICS_ADDR`, update the target port to match.

For a liveness/health check outside Prometheus, probe `/health` (runtime), `/healthz` (gateway), or `/api/v1/health` (API) as shown above — each returns a non-`200` status when unhealthy, so `curl -f` is enough to gate a health check.

---

## Where to confirm these details

These endpoints live in the Apache-2.0 crates in the [`agent-assembly`](https://github.com/ai-agent-assembly/agent-assembly) repository, so you can verify them against the source you run:

- `aa-runtime/src/config.rs` — `AA_METRICS_ADDR` and its default.
- `aa-runtime/src/runtime.rs` and `aa-runtime/src/health/` — the health/metrics server and the baseline metrics.
- `aa-gateway/src/routes/healthz.rs` — the `/healthz` liveness probe (local and remote modes).
- `aa-api/src/routes/health.rs` — the `/api/v1/health` check.

---

## Related documentation

- [Open core boundary](open-core-boundary.md) — what the limited-function OSS stack includes vs. the SaaS feature set.
- [Cloud Deployment](cloud-deployment.md) — the managed SaaS platform, its SLA tiers, and on-call (SaaS only).
- [Security model](security-model.md) — the Telemetry layer and the broader defense-in-depth posture.
- [Troubleshooting](troubleshooting.md) — common issues when running the stack.

---

*Last reviewed: 2026-07-15 · AI Agent Assembly Team*
