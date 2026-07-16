# Policy Reference

Policies are YAML documents that control what an AI agent may do — which domains it can reach, which tools it can call, how much it can spend, and more. The gateway evaluates the applicable policies before each agent action and allows, denies, or rate-limits it.

This page is a field-by-field reference. Each section lists a policy block with its fields, types, defaults, and validation rules, followed by [worked examples](#examples) at the end.

---

## Document formats

The gateway accepts two formats.

### Envelope format (recommended)

Uses `apiVersion` / `kind` / `metadata` / `spec` wrapping — version-controlled and GitOps-friendly:

```yaml
apiVersion: agent-assembly/v1
kind: Policy
metadata:
  name: my-policy         # shown in console and audit log
  version: "1.0.0"        # your policy revision
  description: ...        # optional
spec:
  scope: team:platform
  network:
    allowlist:
      - api.openai.com
  budget:
    daily_limit_usd: 25.0
```

### Flat format

Minimal format without the envelope wrapper — useful for quick testing:

```yaml
version: "1.0"
scope: global
network:
  allowlist:
    - api.openai.com
```

---

## Top-level fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `version` | string | No | — | Schema version tag (e.g., `"1.0"`). Informational; not validated. |
| `scope` | string | No | `global` | Hierarchical scope this policy applies to. See [Scope](#scope). |
| `network` | object | No | — | Network egress policy. See [network](#network). |
| `schedule` | object | No | — | Active-hours restriction. See [schedule](#schedule). |
| `budget` | object | No | — | Per-day / per-month spend cap. See [budget](#budget). |
| `data` | object | No | — | PII / credential pattern detection. See [data](#data). |
| `tools` | map | No | `{}` | Per-tool allow/deny/rate configuration. See [tools](#tools). |
| `capabilities` | object | No | — | Capability allow/deny lists. See [capabilities](#capabilities). |
| `approval_timeout_secs` | integer | No | `300` | Default seconds before an approval request expires. Must be > 0. |
| `approval` | object | No | — | Per-policy approval escalation overrides. See [approval](#approval). |

---

## Scope

The `scope` field determines which agents a policy applies to. Policies cascade from broadest to narrowest — `Global → Org → Team → Agent → Tool` — with **most-restrictive-wins** merging.

| Value | Example | Applies to |
|---|---|---|
| `global` | `scope: global` | Every agent in the workspace (default when absent) |
| `org:<id>` | `scope: org:acme` | Every agent inside the named organisation |
| `team:<id>` | `scope: team:platform` | Every agent that belongs to the named team |
| `agent:<uuid>` | `scope: agent:01234567-89ab-cdef-0123-456789abcdef` | A single specific agent (UUID format) |
| `tool:<name>` | `scope: tool:slack-mcp` | A specific MCP tool, across all agents otherwise admitted by higher scopes |

`tool:<name>` sits at the most-restrictive end of the cascade. A tool-scoped policy can deny `slack-mcp` for every agent in `team:platform` even when team- and agent-level policies would otherwise allow it.

**Validation:** The `agent:` variant requires a valid hyphenated UUID. The identifier after `:` must not be empty. Unknown scope kinds (e.g., `project:foo`) are rejected with a validation error.

---

## `network`

Controls outbound network connections the agent may initiate.

| Field | Type | Required | Description |
|---|---|---|---|
| `network.allowlist` | list of strings | No | Domain glob patterns the agent may connect to. Empty string entries are rejected. |

When `network` is present but `allowlist` is absent or empty, no outbound connections are permitted.

```yaml
network:
  allowlist:
    - "api.openai.com"
    - "*.slack.com"
    - "internal-api.corp.example"
```

---

## `schedule`

Restricts the time window during which the agent is permitted to run.

### `schedule.active_hours`

| Field | Type | Required | Format | Description |
|---|---|---|---|---|
| `schedule.active_hours.start` | string | Yes (if active_hours present) | `HH:MM` 24-hour | Window start time |
| `schedule.active_hours.end` | string | Yes (if active_hours present) | `HH:MM` 24-hour | Window end time; must be later than `start` |
| `schedule.active_hours.timezone` | string | Yes (if active_hours present) | IANA name | Timezone for window boundary (e.g., `"Asia/Taipei"`, `"UTC"`) |

All three sub-fields are required when `active_hours` is present. `start` must be earlier than `end`.

```yaml
schedule:
  active_hours:
    start: "09:00"
    end: "18:00"
    timezone: "America/New_York"
```

---

## `budget`

Caps per-agent LLM spend. The gateway enforces the budget before allowing the agent action.

| Field | Type | Required | Description |
|---|---|---|---|
| `budget.daily_limit_usd` | float | No | Maximum USD spend per calendar day. Must be > 0. |
| `budget.monthly_limit_usd` | float | No | Maximum USD spend per calendar month. Must be > 0 and ≥ `daily_limit_usd`. |
| `budget.org_daily_limit_usd` | float | No | Maximum USD spend per calendar day, aggregated across the whole organisation. Must be > 0. |
| `budget.org_monthly_limit_usd` | float | No | Maximum USD spend per calendar month, aggregated across the whole organisation. Must be > 0 and ≥ `org_daily_limit_usd`. |
| `budget.timezone` | string | No | IANA timezone for the daily/monthly reset boundary. Defaults to UTC when absent. |
| `budget.action_on_exceed` | `"deny"` \| `"suspend"` | No | Action when budget is exceeded. `deny` (default): blocks individual requests but keeps the agent active. `suspend`: suspends the agent entirely until the budget resets. |
| `budget.window` | string | No | Sub-day rollover window as a humantime duration (e.g. `"5s"`, `"30m"`, `"1h30m"`). When absent, the daily/monthly counters roll over at the calendar-day boundary. Must be a positive duration. |

```yaml
budget:
  daily_limit_usd: 25.0
  monthly_limit_usd: 500.0
  timezone: "America/Los_Angeles"
  action_on_exceed: deny
```

---

## `data`

Scans agent inputs and outputs for PII or credential patterns using regex.

| Field | Type | Required | Description |
|---|---|---|---|
| `data.sensitive_patterns` | list of regex strings | No | RE2-compatible regex patterns. A match causes the agent action to be blocked. Invalid regex is rejected at validation time. |

```yaml
data:
  sensitive_patterns:
    - "sk-[a-zA-Z0-9]{48}"               # OpenAI API key
    - "\\b\\d{3}-\\d{2}-\\d{4}\\b"       # US SSN
    - "(?i)password\\s*[:=]\\s*\\S+"     # password assignment
```

---

## `tools`

Per-tool configuration keyed by tool name. Each key in the `tools` map is a tool name string; the value is a tool policy object.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `tools.<name>.allow` | boolean | No | `true` | Whether this tool is permitted. Set to `false` to block the tool entirely. |
| `tools.<name>.limit_per_hour` | integer | No | unlimited | Maximum calls to this tool per hour. |
| `tools.<name>.requires_approval_if` | string | No | — | CEL expression that triggers human-in-the-loop approval when true. Valid governance level values: `L0`, `L1`, `L2`, `L3`. |

```yaml
tools:
  bash:
    allow: true
    limit_per_hour: 10
    requires_approval_if: "governance_level >= L2"
  execute_shell:
    allow: false
  file_write:
    allow: true
    limit_per_hour: 5
```

**`requires_approval_if` CEL expressions:** The expression is evaluated against the tool call context. The identifier `governance_level` exposes the current agent's governance tier (`L0`–`L3`). Referencing an unknown level (e.g., `L4`) is a validation error.

---

## `capabilities`

Broad capability allow/deny lists that apply across all tools and actions.

| Field | Type | Required | Description |
|---|---|---|---|
| `capabilities.allow` | list of capability strings | No | Capabilities explicitly permitted. |
| `capabilities.deny` | list of capability strings | No | Capabilities explicitly denied. Deny takes precedence over allow. |

### Valid capability strings

| String | Description |
|---|---|
| `file_read` | Read access to the filesystem |
| `file_write` | Write access to the filesystem |
| `network_outbound` | Outbound network connections |
| `network_inbound` | Inbound network connections |
| `terminal_exec` | Execute commands in a terminal/shell |
| `agent_spawn` | Spawn child agents |
| `mcp_tool:<name>` | Use a specific named MCP tool (e.g., `mcp_tool:bash`, `mcp_tool:git`) |
| `model:<name>` | Use a specific named AI model (e.g., `model:gpt-4o`) |

Unknown capability strings are rejected with a validation error. The `mcp_tool:` and `model:` prefixes require a non-empty name after the colon.

```yaml
capabilities:
  allow:
    - file_read
    - network_outbound
    - mcp_tool:git
    - mcp_tool:bash
  deny:
    - terminal_exec
    - file_write
```

---

## `approval`

Per-policy escalation overrides. When absent, team-level routing defaults are used.

| Field | Type | Required | Description |
|---|---|---|---|
| `approval.timeout_seconds` | integer | No | Override the escalation timeout (seconds) for approvals triggered by this policy's rules. |
| `approval.escalation_role` | string | No | Override the approver group or role name for this policy (e.g., `"org-admin"`, `"security-team"`). |

```yaml
approval:
  timeout_seconds: 600
  escalation_role: org-admin
```

The top-level `approval_timeout_secs` sets the default for the whole policy document; `approval.timeout_seconds` overrides it at the per-policy escalation level.

---

## Validation rules

The gateway validates every policy on upload. All errors are collected and returned together; the upload is rejected if any error is present.

| Field | Rule |
|---|---|
| `network.allowlist[n]` | Entry must not be empty |
| `schedule.active_hours.start` | Required when `active_hours` is present; must be `HH:MM` 24-hour format |
| `schedule.active_hours.end` | Required when `active_hours` is present; must be `HH:MM` and later than `start` |
| `schedule.active_hours.timezone` | Required when `active_hours` is present; must be a valid IANA timezone name |
| `budget.daily_limit_usd` | Must be > 0 when present |
| `budget.monthly_limit_usd` | Must be > 0; must be ≥ `daily_limit_usd` when both are set |
| `budget.org_daily_limit_usd` | Must be > 0 when present |
| `budget.org_monthly_limit_usd` | Must be > 0; must be ≥ `org_daily_limit_usd` when both are set |
| `budget.timezone` | Must be a valid IANA timezone name when present |
| `budget.action_on_exceed` | Must be `"deny"` or `"suspend"` when present |
| `budget.window` | Must be a positive humantime duration (e.g. `5s`, `30m`, `1h30m`) when present |
| `data.sensitive_patterns[n]` | Must be a valid RE2 regex |
| `tools.<name>.requires_approval_if` | Must not be empty; must reference only `L0`–`L3` governance levels |
| `capabilities.allow[n]` / `capabilities.deny[n]` | Must be a known capability string |
| `approval_timeout_secs` | Must be > 0 when present |
| `scope` | Must be `global`, `org:<id>`, `team:<id>`, `agent:<uuid>`, or `tool:<name>`; identifier after `:` must not be empty; `agent:` value must be a valid UUID |

Unknown keys — whether at the top level, or nested inside an enforced section (`network`, `schedule`/`schedule.active_hours`, `budget`, `data`, `tools.<name>`, `capabilities`, `approval`) — produce a **hard validation error** that rejects the whole document. This is intentionally fail-closed: a typo'd key (e.g. `capabilties` for `capabilities`, or `dney` for `deny` under `capabilities`) must not silently drop the restriction the author intended while the rest of the policy loads and enforces a weaker posture than was written.

---

## Examples

### Minimal — budget cap only

```yaml
apiVersion: agent-assembly/v1
kind: Policy
metadata:
  name: budget-only
  version: "1.0.0"
spec:
  budget:
    daily_limit_usd: 10.0
    action_on_exceed: deny
```

### Network egress allowlist

```yaml
apiVersion: agent-assembly/v1
kind: Policy
metadata:
  name: allowlist-openai-slack
  version: "1.0.0"
spec:
  scope: team:platform
  network:
    allowlist:
      - "api.openai.com"
      - "*.slack.com"
```

### Capability control

```yaml
apiVersion: agent-assembly/v1
kind: Policy
metadata:
  name: capability-example
  version: "1.0.0"
spec:
  scope: global
  capabilities:
    allow:
      - file_read
      - network_outbound
      - mcp_tool:git
      - mcp_tool:bash
    deny:
      - terminal_exec
      - file_write
```

### Tool rate-limiting with approval gate

```yaml
apiVersion: agent-assembly/v1
kind: Policy
metadata:
  name: guarded-tools
  version: "1.0.0"
spec:
  tools:
    bash:
      allow: true
      limit_per_hour: 10
      requires_approval_if: "governance_level >= L2"
    execute_shell:
      allow: false
```

### Business-hours schedule

```yaml
apiVersion: agent-assembly/v1
kind: Policy
metadata:
  name: business-hours-only
  version: "1.0.0"
spec:
  scope: team:ops
  schedule:
    active_hours:
      start: "09:00"
      end: "18:00"
      timezone: "America/New_York"
```

### PII detection

```yaml
apiVersion: agent-assembly/v1
kind: Policy
metadata:
  name: no-pii-in-output
  version: "1.0.0"
spec:
  data:
    sensitive_patterns:
      - "sk-[a-zA-Z0-9]{48}"
      - "\\b\\d{3}-\\d{2}-\\d{4}\\b"
```

### Full policy — all sections

```yaml
apiVersion: agent-assembly/v1
kind: Policy
metadata:
  name: production-full
  version: "1.0.0"
  description: Full example combining all policy sections.
spec:
  scope: team:platform
  network:
    allowlist:
      - "api.openai.com"
      - "slack.com"
  schedule:
    active_hours:
      start: "09:00"
      end: "18:00"
      timezone: "Asia/Taipei"
  budget:
    daily_limit_usd: 25.0
    monthly_limit_usd: 500.0
    action_on_exceed: deny
  data:
    sensitive_patterns:
      - "sk-[a-zA-Z0-9]{48}"
  tools:
    bash:
      allow: true
      limit_per_hour: 10
    file_write:
      allow: false
  capabilities:
    allow:
      - file_read
      - network_outbound
    deny:
      - terminal_exec
  approval_timeout_secs: 300
  approval:
    escalation_role: org-admin
```

---

## Related documentation

- [Security model](security-model.md) — IronClaw layers and policy engine position in the stack
- [Cloud deployment](cloud-deployment.md) — uploading and activating policies in the console
- [Quick start (SaaS)](quickstart-saas.md) — create and activate your first policy

---

*Last reviewed: 2026-06-11 · AI Agent Assembly Team*
