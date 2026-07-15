# Quick start (SaaS)

> 🚧 **Coming soon.** The AI Agent Assembly SaaS / commercial platform described here is planned and not yet generally available. The content below reflects the intended design.

This page takes you from zero to a governed AI agent. The fastest path is the LangChain walkthrough below, which works on any tier. If you want to pick a tier first, jump to [Pro](#pro-tier), [Business](#business-tier), or [Enterprise](#enterprise-tier).

This page covers the managed SaaS onboarding. Choose the tier that matches your team size and compliance needs, then connect your first agent. (A limited-function stack is also self-hostable from the Apache-2.0 crates for local evaluation and development — see [Open core boundary](open-core-boundary.md).)

> **Full functionality is SaaS.** A limited-function stack is self-hostable from the Apache-2.0 crates for local evaluation and development; complete governance, policy evaluation, and audit logging at production grade run in the AI Agent Assembly cloud. See [Open core boundary](open-core-boundary.md) for the licensing model.

---

## Govern a LangChain agent in under 5 minutes

This end-to-end example takes a LangChain agent from zero to fully governed in under 5 minutes, on any tier.

**Prerequisites:** Python 3.12+, an OpenAI API key, and a Pro (or higher) workspace.

### Step 1 — Install packages

Install the Python SDK — see the [Python SDK quick start](https://docs.agent-assembly.com/python-sdk/) for the current install command — plus the LangChain packages this walkthrough uses: `langchain`, `langchain-classic`, `langchain-openai`, `langchain-core`.

### Step 2 — Set credentials

```bash
export AAA_WORKSPACE_ID="<your-workspace-id>"   # from Settings → Workspace
export AAA_API_KEY="<your-api-key>"             # from Settings → API Keys
export OPENAI_API_KEY="<your-openai-key>"
```

### Step 3 — Instrument your LangChain agent

```python
import os
from agent_assembly import init_assembly
from agent_assembly.adapters.langchain import get_active_callback_handler
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool


@tool
def summarise_text(text: str) -> str:
    """Return a one-sentence summary of the provided text."""
    return text[:200] + "..." if len(text) > 200 else text


def run_agent(question: str) -> str:
    # init_assembly registers the agent with the gateway and installs the
    # governance interceptor. get_active_callback_handler() returns the
    # AssemblyCallbackHandler it wired to that interceptor; passing it to
    # LangChain via callbacks=[...] policy-checks and audits every tool/LLM call.
    with init_assembly(
        gateway_url=os.environ.get("AAA_GATEWAY_URL", "https://api.agent-assembly.com"),
        api_key=os.environ["AAA_API_KEY"],
        agent_id="langchain-research-agent",
        mode="sdk-only",
    ):
        handler = get_active_callback_handler()

        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        tools = [summarise_text]

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful research assistant."),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent, tools=tools, callbacks=[handler], verbose=False
        )
        result = executor.invoke({"input": question})
        return result["output"]


if __name__ == "__main__":
    answer = run_agent(
        "What is AI Agent Assembly and why does it matter for enterprise governance?"
    )
    print(answer)
```

The `init_assembly` session plus the wired callback handler do three things, without touching LangChain internals:

- Register `langchain-research-agent` with the gateway.
- Run a policy check before each tool/LLM call, blocking it if policy denies.
- Emit an audit event for every call.

### Step 4 — Activate a starter policy

In the console, open **Policies → New Policy** and apply the starter template (allow all, audit all). This takes under 30 seconds. From now on, every call from `langchain-research-agent` is governed, audited, and visible in the **Audit Log** panel.

### What governance looks like at runtime

```
[AAASM] Agent registered: langchain-research-agent (workspace: ws-a1b2...)
[AAASM] Policy check: ALLOW  event=llm_call  agent=langchain-research-agent
[AAASM] Audit event written: id=evt_01j...  latency=2ms
```

---

## Pro Tier

**Signup**: planned self-serve at `https://app.agent-assembly.com/signup` — **not yet live** while Cloud is in early access. [Request Cloud early access](https://agent-assembly.com/early-access) to be notified when Pro-tier signup opens.

**Included features**: up to 10 agents, basic policy engine (allow/deny/audit), 30-day audit log retention, community forum support.

**Expected onboarding time**: ~10 minutes from signup to first governed agent call.

**Primary contact channel**: self-serve; community forum at `https://community.agent-assembly.com`.

### Pro signup steps

1. **Coming soon** — once Cloud is generally available, you'll navigate to `https://app.agent-assembly.com/signup` and create an account with your work email. The signup endpoint is not live yet; [request early access](https://agent-assembly.com/early-access) in the meantime.
2. Verify your email address.
3. On the **Workspace Setup** page, enter a workspace name (e.g., `acme-ai-ops`) and select your primary region.
4. Copy your **Workspace ID** and generate an **API Key** under **Settings → API Keys**.
5. Install the SDK for your language — see the [Python SDK quick start](https://docs.agent-assembly.com/python-sdk/), [Node SDK quick start](https://docs.agent-assembly.com/node-sdk/), or [Go SDK quick start](https://docs.agent-assembly.com/go-sdk/).

6. Set credentials:

```bash
export AAA_WORKSPACE_ID="<your-workspace-id>"
export AAA_API_KEY="<your-api-key>"
```

7. Instrument your agent entry point:

```python
import os
import openai
from agent_assembly import init_assembly


def run_agent(prompt: str) -> str:
    # Open a governed session for this agent; every call inside the context is
    # registered, policy-checked, and audited by the gateway.
    with init_assembly(
        gateway_url=os.environ.get("AAA_GATEWAY_URL", "https://api.agent-assembly.com"),
        api_key=os.environ["AAA_API_KEY"],
        agent_id="my-first-agent",
        mode="sdk-only",
    ):
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
```

8. Open **Policies → New Policy** in the console and activate a starter policy. Your agent is now governed.

---

## Business Tier

**Signup**: planned self-serve at `https://app.agent-assembly.com/signup` (select **Business** during workspace setup) — **not yet live** while Cloud is in early access. [Request Cloud early access](https://agent-assembly.com/early-access) to be notified when Business-tier signup opens.

**Included features**: up to 50 agents, full policy engine, SSO (SAML 2.0 / OIDC), 90-day audit log retention, SIEM export, business-hours support (24h response).

**Expected onboarding time**: ~30 minutes, including SSO connect.

**Primary contact channel**: support ticket via `https://app.agent-assembly.com/support`.

### Business signup steps

1. **Coming soon** — once Cloud is generally available, you'll sign up at `https://app.agent-assembly.com/signup` and select the **Business** tier. The signup endpoint is not live yet; [request early access](https://agent-assembly.com/early-access) in the meantime.
2. On the **Billing** page, enter your credit card details (processed via Stripe).
3. Complete workspace setup (name, region) as in the Pro flow above.
4. Connect SSO: navigate to **Settings → Authentication → SSO** and follow the [SAML 2.0 or OIDC setup steps](cloud-deployment.md#sso-configuration). SSO is optional at the Business tier but recommended for teams.
5. Invite your team under **Settings → Users** — assign roles (Admin, Developer, Viewer).
6. Instrument agents and create policies as in the Pro flow.

---

## Enterprise Tier

**Signup**: form-driven via `https://app.agent-assembly.com/contact-sales`.

**Included features**: unlimited agents, dedicated region (data residency), SCIM provisioning, tamper-evident audit log, audit log retention up to 1 year, 99.9% SLA, 24/7 support (4h response), dedicated SRE contact.

**Expected onboarding time**: 1–3 weeks, driven by procurement and security review.

**Primary contact channel**: your assigned Sales Engineer (SE).

### Enterprise procurement timeline

| Week | Activity |
|---|---|
| **Week 1** | Submit the `/contact-sales` form → initial SE call (30 min) → receive the Enterprise Order Form and DPA/BAA templates |
| **Week 2** | Legal review of DPA / BAA → IT security review → contract signature |
| **Week 3** | SE-led workspace provisioning → SSO + SCIM setup with your IdP team → pilot agent onboarding |

### Enterprise-specific steps

1. Submit the contact form at `https://app.agent-assembly.com/contact-sales`. Include estimated agent count, primary region preference, and compliance requirements (SOC 2, HIPAA, GDPR).
2. During the SE call, confirm your IdP (Okta, Azure AD, PingFederate, etc.) and data residency requirement.
3. After contract signature, the SE provisions your workspace in the selected dedicated region and sends your Workspace ID and initial API key.
4. Configure **SSO** (SAML or OIDC) per [Cloud Deployment → SSO Configuration](cloud-deployment.md#sso-configuration).
5. Configure **SCIM** provisioning per [Cloud Deployment → SCIM User Provisioning](cloud-deployment.md#scim-user-provisioning) for automated user lifecycle management.
6. Configure **budgets** per [Cloud Deployment → Budget Configuration](cloud-deployment.md#budget-configuration) for per-team LLM spend caps.
7. Instrument agents and create policies as in the Pro flow.

---

## Next steps

- [Cloud deployment](cloud-deployment.md) — SSO/SCIM deep-dive, region selection, billing, SLA tiers
- [Policy reference](policy-reference.md) — full policy rule schema
- [Open core boundary](open-core-boundary.md) — what's in the OSS core vs. the enterprise tier

<div class="aa-cta-next">
  <span class="aa-cta-next__label">Next step</span>
  <a href="https://github.com/ai-agent-assembly/examples?utm_source=docs&amp;utm_medium=docs_link&amp;utm_campaign=oss_install&amp;utm_content=quickstart_next_step" data-cta-location="body" rel="noopener">Run a working example →</a>
  <p>Open the <code>agent-assembly-examples</code> repo and step through a governed
     LangChain, LlamaIndex, or bare-OpenAI agent end-to-end.</p>
</div>

<div class="aa-cta-next">
  <span class="aa-cta-next__label">Ready for a managed workspace?</span>
  <a href="https://agent-assembly.com/early-access?utm_source=docs&amp;utm_medium=docs_link&amp;utm_campaign=early_access&amp;utm_content=quickstart_page" data-cta-location="body" rel="noopener">Request Cloud Early Access →</a>
  <p>Cloud is in early access / design-partner. It is not generally available yet;
     the OSS quickstart above works today.</p>
</div>

---

*Last reviewed: 2026-07-15 · AI Agent Assembly Team*
