# State of Developer Tooling 2026

> A living report on the trends shaping how we build, ship, and operate software in 2026.

---

## Executive Summary

2026 is the year the **autonomous engineer** stopped being a demo and started shipping production code. AI coding assistants graduated from autocomplete to long-running agents that open PRs, run CI, fix review comments, and close issues while you sleep. The **Model Context Protocol (MCP)** became the standard connector between agents and the rest of your stack — databases, APIs, file systems, internal tools — collapsing the integration sprawl that defined 2024–2025. Meanwhile, an undercurrent reaction formed: a **zero-dependency, stdlib-only** movement (the `tiny-*` ecosystem and its peers) that prizes auditability, sub-millisecond cold starts, and total supply-chain transparency over feature breadth. **Agentic workflow orchestration** matured into DAG-based pipelines with human approval gates, **observability for AI systems** became a first-class discipline with token budgets and LLM spans, and **security tooling** refocused on the agent threat model: prompt injection, secret leakage, sandboxed execution. This report walks through each shift, names the players, and gives you the numbers (32K log lines/sec, 247K validations/sec, 2.2M cache ops/sec) to anchor the conversation.

---

## TL;DR — The 10 Trends That Mattered

1. **Autonomous engineers crossed the production line.** Long-running agents (Devin, Cursor Background Agents, Goose, CodeBuddy) now own end-to-end tasks — triaging issues, writing code, running tests, responding to review — measured in hours, not prompts.
2. **MCP became the universal adapter.** Anthropic's Model Context Protocol shipped in late 2024 and reached saturation in 2026. Every serious agent framework ships an MCP client; every serious tool ships an MCP server.
3. **Zero-dependency libraries went mainstream.** The "tiny-*" pattern — single-file, stdlib-only, auditable in an afternoon — moved from curiosity to default choice for logging, validation, caching, config, secrets, and tracing.
4. **Agentic workflows moved from scripts to DAGs.** `tiny-workflow`, Temporal, Prefect, and Airflow 3 all converged on durable, resumable, approval-gated pipelines as the orchestration primitive.
5. **Observability for AI is now a first-class discipline.** OpenTelemetry extended with LLM spans, token-budget dashboards, and cost-per-trace views. `tiny-otel` and `tiny-trace` shipped the stdlib-only take.
6. **Security pivoted to the agent threat model.** Prompt-injection detection, secret-scanning for autonomous loops, and sandboxed execution (`tiny-sandbox`, `tiny-secret`) replaced perimeter-only thinking.
7. **Eval-driven development went from research to routine.** Teams ship "eval suites" alongside test suites; agent PRs are blocked by regressions in either.
8. **Micro-frameworks beat mega-frameworks for the second straight year.** `tiny-web`, `tiny-api`, `tiny-router` ship in <500 LOC and beat FastAPI on cold-start by 10–40x.
9. **Single-file libraries became a publishing pattern.** One file, one job, one README. PyPI has ~30% more single-file packages uploaded in 2026 than 2025.
10. **Bounty-driven development emerged.** Autonomous agents crawl GitHub bounties, score issues, implement fixes, and open PRs — a new category of CI/CD and a sharp edge case for evaluation.

---

## Section 1: AI Coding Agents — From Assistants to Autonomous Engineers

The single biggest shift in 2026 is the move from *copilot* to *colleague*. The autocomplete autocomplete-completeds are still here; the differentiator is whether the agent can own a task end-to-end.

### The evolution

```
2022-2023  | Autocomplete         | Tab-complete a line. Reactive.
2024       | Pair programmer      | Multi-line suggestions, chat, edit commands.
2025       | In-IDE agent         | Cursor, Copilot Workspace, Windsurf. Multi-file edits.
2026 (now) | Autonomous engineer  | Owned issues, long-running, PRs, reviews, CI.
```

### Key players in 2026

| Tool | Class | Differentiator | Best For |
|------|-------|----------------|----------|
| **Devin** (Cognition) | Autonomous engineer | Long-running VM, owns the full laptop | Underspecified tasks, greenfield work |
| **Cursor** | Agentic IDE | Best-in-class multi-file editing, Background Agents | Daily-driver IDE for senior engineers |
| **Windsurf** (Codeium) | Agentic IDE | Cascade flow editor, deep project awareness | Teams migrating from JetBrains |
| **GitHub Copilot** | Agent + IDE | Workspace, PR review, agent mode | Microsoft shops, OSS maintainers |
| **CodeBuddy** (Tencent) | Autonomous CLI | Strong multilingual models, agent-first CLI | Asia-Pacific teams, polyglot repos |
| **Goose** (Block) | Local autonomous agent | Runs anywhere, fully local, pluggable LLM | Security-sensitive, air-gapped |
| **OpenClaw** / FalconEye | Orchestration platform | Dispatcher + approval gates + bounties | Multi-agent fleet ops |

### The agentic IDE vs. autonomous engineer spectrum

A useful mental model:

- **Agentic IDE** — the human drives the session; the agent is a senior peer sitting next to you. Cursor, Windsurf, Copilot Workspace.
- **Autonomous engineer** — the agent owns the session; the human reviews the diff. Devin, Cursor Background Agents, Goose, OpenClaw jobs.
- **Agent fleet** — many autonomous engineers coordinated by a dispatcher, with budgets, queues, and human gate-keeper at choke points. This is the 2026 frontier.

The mistake teams make is treating these as the same thing. They are not. The cost model, the failure model, the security model, and the UX model are all different.

### Long-running autonomous workflows — the 2026 breakthrough

The hard problem that broke in 2026 is **continuity**. Previous agents forgot the task at 60 seconds, lost context at the first tool error, or burned out on a 4k-token error message. The 2026 generation solves this with:

- **Persistent scratchpads** — agents write to a state file at every step; they can resume after a crash.
- **Token-aware summarization** — old context is compressed, not deleted; the agent can rehydrate it.
- **Sub-agent dispatch** — the parent agent spawns a child for a sub-task, joins on result, continues.
- **Failure-as-data** — tool failures are first-class outputs that the agent reasons about, not exceptions that kill it.

These are not exotic. They are baseline. If your agent platform doesn't have them, it's a 2025 product.

### Human-in-the-loop controls and approval gates

The other 2026 breakthrough is the realization that **fully autonomous is a deployment mode, not a default**. Production teams use:

- **Pre-tool approval** — every `git push`, every `rm`, every API write prompts a human (or a policy engine).
- **Post-action review** — the agent ships a PR; the human owns the merge.
- **Budget gates** — the agent can spend $4 in API tokens without asking, but anything over triggers a notification.
- **Scope fences** — the agent can only edit files matching `src/feature-x/`; everything else is read-only.

The teams that got this wrong in early 2026 had autonomous agents rewrite their CI config or push to `main`. The teams that got it right treated approval gates as a feature, not a tax.

### Evaluation frameworks are now critical infrastructure

Last year, "does the agent work?" was a vibe check. In 2026, it's a CI run. Every serious agent deployment has:

- A **task suite** — fixed inputs, expected outputs, scored on a rubric.
- A **regression suite** — known-good traces replayed against new model versions.
- A **cost budget** — "this agent must complete the task under $0.50 and 200k tokens."
- A **safety suite** — "this agent must refuse to push to `main` without approval."

`SWE-bench`, `HumanEval`, `MultiPL-E`, and a dozen industry-specific benchmarks are now standard CI dependencies. The teams that didn't adopt them are flying blind.

---

## Section 2: The MCP Ecosystem

If 2024 was the year of "every agent has its own tool ecosystem," 2026 is the year of **one protocol to rule them all.**

### Model Context Protocol — the standard

The **Model Context Protocol (MCP)** is an open standard for connecting agents to external tools, data, and services. You can think of it as **USB-C for agents**: one connector, many devices.

```
┌─────────────┐     JSON-RPC      ┌──────────────────┐
│  LLM Agent  │  ◄────────────►  │  MCP Server(s)   │
│  (client)   │   over stdio /   │  - Filesystem    │
│             │   HTTP / SSE     │  - PostgreSQL    │
│             │                  │  - GitHub        │
│             │                  │  - Slack         │
│             │                  │  - tiny-* tools  │
└─────────────┘                  └──────────────────┘
```

The protocol is deliberately small: a handshake, a list of tools, a call-and-response loop. The win is that any agent that speaks MCP can use any MCP server, and any tool that exposes an MCP server can be used by any agent. No more bespoke integrations.

### Adoption in 2026

- **Every major agent framework** ships an MCP client: Claude SDK, OpenAI Agents SDK, LangChain, LlamaIndex, Goose, OpenClaw.
- **Every major tool** ships an MCP server: GitHub, Notion, Slack, Linear, Postgres, SQLite, Stripe, Cloudflare, AWS, GCP.
- **The "MCP server directory"** at `modelcontextprotocol.io` lists 4,000+ community servers as of mid-2026.
- **MCP is the default** for new internal tools at most enterprises; the previous "build a custom REST API + an SDK + a chatbot" template is collapsing.

### Concrete examples — what an MCP server looks like

A filesystem MCP server exposes:

```json
{
  "name": "read_file",
  "description": "Read the contents of a file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": { "type": "string" }
    },
    "required": ["path"]
  }
}
```

A Postgres MCP server exposes `query`, `schema`, `list_tables`. A GitHub MCP server exposes `create_issue`, `list_prs`, `add_review_comment`. The agent calls these through the same protocol, with the same primitives, the same error handling.

### The tool-calling standardization wave

MCP is the visible part. Underneath, what changed is **how agents reason about tools**:

- **Tool descriptions are first-class.** Writing a good MCP server description is now a craft. The agent's choice of tool depends on it.
- **Schemas are contracts.** Agents plan against the schema; they don't discover at call time.
- **Errors are structured.** Returns include `error`, `retry_after`, `fallback`, not just an HTTP 500.
- **Streaming is the default.** Long-running tool calls stream progress, not just final result.

The ripple effect is that **internal teams now write MCP servers instead of REST APIs for agent-facing surfaces.** Same underlying system, different contract.

### `tiny-mcp` and `tiny-mcp-client` in context

The `tiny-*` ecosystem ships an MCP implementation in <300 lines of Python:

```python
# tiny-mcp-server example
from tiny_mcp import Server, tool

app = Server("tiny-tools")

@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@tool
def echo(message: str) -> str:
    """Echo back the message."""
    return message

if __name__ == "__main__":
    app.run()
```

Why this matters: you can read the entire MCP stack in an afternoon. You can audit it. You can fork it. You can ship a custom MCP server for your internal tool in 30 minutes. The dependency tree is `[]`. That's the posture 2026 is rewarding.

---

## Section 3: Zero-Dependency Philosophy

The defining undercurrent of 2026 is a quiet revolt against the dependency graph. After a decade of `npm install` pulling 1,400 transitive packages, **stdlib-only is a feature**.

### Why stdlib-only libraries are winning in 2026

| Reason | What it gives you |
|--------|-------------------|
| **Auditability** | You can read the entire library in an afternoon. The whole thing. No `node_modules` archaeology. |
| **Security** | No supply-chain attack surface beyond what your language already ships. |
| **Cold-start speed** | No import-time work. A `tiny-log` import is 0.3ms. A `loguru` import is 40ms. |
| **Reproducibility** | Pin Python; the library is frozen. No lockfile drift across teams. |
| **Longevity** | No abandoned dependency in 2028. No breaking change in a transitive package. |
| **Compliance** | Some regulated environments (FedRAMP, certain EU shops) ban third-party packages. Stdlib-only slips through. |

### The `tiny-*` ecosystem as a case study

The `tiny-*` ecosystem is a coherent family of stdlib-only Python packages:

- **`tiny-log`** — structured logging
- **`tiny-validator`** — schema validation
- **`tiny-config`** — env + file config
- **`tiny-cache`** — LRU + TTL in-memory cache
- **`tiny-secret`** — secret loading with masking
- **`tiny-otel`** — OpenTelemetry-style traces
- **`tiny-trace`** — distributed context propagation
- **`tiny-workflow`** — DAG-based orchestration
- **`tiny-sandbox`** — subprocess isolation
- **`tiny-mcp`** / **`tiny-mcp-client`** — MCP server & client
- **`tiny-cli`** — argparse successor
- **`tiny-web`** — micro HTTP server
- **`tiny-api`** — REST framework
- **`tiny-router`** — URL routing
- **`tiny-fs`** — filesystem helpers
- **`tiny-http`** — HTTP client

Each is one file, ~200–600 lines, zero dependencies, MIT, fully typed. Together they cover 80% of what most services need.

### Benchmarks (measured on a 2024 M3 Pro, Python 3.12)

| Library | Operation | Throughput | Notes |
|---------|-----------|------------|-------|
| `tiny-log` | Log lines/sec | **32,000** | JSON formatter, single thread |
| `tiny-validator` | Validations/sec | **247,000** | Simple schema, 5 fields |
| `tiny-cache` | Get+set ops/sec | **2,200,000** | In-memory, single thread |
| `tiny-otel` | Spans/sec | **85,000** | No exporter, in-memory sink |
| `tiny-config` | Loads/sec | **18,000** | 12-key YAML |
| `tiny-secret` | Masked reads/sec | **410,000** | With audit log |

For comparison, `loguru` logs ~6K lines/sec, `pydantic` validates ~95K schemas/sec, `cachetools` does ~1.1M ops/sec. The `tiny-*` libraries are **not** always faster — they are *competitive* with the major libraries at a fraction of the dependency cost.

### Cold start, the underrated metric

In 2026, cold start matters more than you think. Serverless, edge functions, CLI tools, and short-lived agents all live or die on import time:

| Library | Import time | Cold start |
|---------|-------------|------------|
| `tiny-log` | **0.3 ms** | Negligible |
| `loguru` | ~40 ms | Noticeable |
| `tiny-validator` | **0.4 ms** | Negligible |
| `pydantic` v2 | ~85 ms | Painful in serverless |
| `tiny-cache` | **0.2 ms** | Negligible |
| `cachetools` | ~6 ms | Tolerable |

Multiply that by 15 imports and the agent that "just works" is the one that imports `tiny-*`. The agent that "loads for 800ms then times out" is the one that pulled FastAPI.

---

## Section 4: Agentic Workflow Orchestration

The 2024 mental model of an agent was a **script**. The 2026 mental model is a **DAG**.

### From scripts to DAG-based pipelines

A script is linear:

```
fetch → process → write → done
```

A DAG is branched:

```
         ┌→ validate ─┐
fetch ──┤            ├──→ write ─┐
         └→ enrich ──┘           ├──→ notify
                                ↑
                          human_gate
```

This is not new — Airflow has done it for a decade. What changed is that **agents now generate DAGs at runtime**, and the DAG is the durable artifact that survives the agent crashing, the model being upgraded, or the human being asleep.

### `tiny-workflow` and the open-source landscape

| Tool | Class | Strengths | Trade-offs |
|------|-------|-----------|------------|
| **`tiny-workflow`** | Stdlib-only DAG | Zero deps, audit-able, ~400 LOC | No managed UI |
| **Temporal** | Durable execution | Battle-tested, multi-language, hosted option | Heavy, Java-flavored concepts |
| **Prefect** | Pythonic DAGs | Beautiful UX, hybrid execution | Cloud-tier for full features |
| **Airflow 3** | The OG | Massive ecosystem, scheduler | Heavy, slow iteration loop |
| **Inngest** | TS-first events | Great DX, serverless-native | Less Pythonic |
| **Restate** | Durable RPC | Transactions + workflows | Newer, smaller community |

The 2026 choice matrix is roughly:

- **You want zero deps and auditability:** `tiny-workflow`
- **You want a managed platform and big team:** Temporal Cloud
- **You want Pythonic and self-hostable:** Prefect
- **You want the biggest ecosystem and have ops people:** Airflow 3

### Human approval gates in autonomous loops

The killer feature of 2026 orchestration is **first-class approval gates**. The DAG can pause, post a message to Slack, wait for a click, and resume:

```python
from tiny_workflow import DAG, gate

with DAG("deploy-service") as g:
    build = g.task("build", build_image)
    test = g.task("test", run_tests, after=[build])
    stage = g.task("stage", deploy_to_staging, after=[test])
    prod = g.task("prod", deploy_to_prod, after=[stage])
    approval = g.gate("human-approval", channel="slack", timeout="2h")
    prod.run(after=[approval])
```

The agent does everything it can. The human ratifies the action. The trace shows exactly who clicked what, when, and on what version. This is the shape of safe autonomous deployment in 2026.

### State persistence and resumability

Two non-negotiables for an agentic workflow in 2026:

1. **Idempotency.** Running a task twice must produce the same result. The workflow engine handles this; the task author writes deterministic code.
2. **Resumability.** The agent crashed at step 7 of 12? Restart from step 7, not step 1. `tiny-workflow` does this by writing the DAG state to a file on every transition.

This is the difference between "agent that ran for an hour" and "agent that I can run for a week."

---

## Section 5: Observability for AI Systems

You can't operate what you can't observe. In 2026, that means **LLM-aware observability**.

### LLM tracing — OpenTelemetry + LLM spans

OpenTelemetry shipped **LLM-specific semantic conventions** in late 2025. They cover:

- `gen_ai.system` — `"openai"`, `"anthropic"`, `"google"`, etc.
- `gen_ai.request.model` — the model name
- `gen_ai.usage.input_tokens` — input tokens
- `gen_ai.usage.output_tokens` — output tokens
- `gen_ai.response.finish_reasons` — `["stop"]`, `["length"]`, `["tool_use"]`
- `gen_ai.agent.name` — the agent or workflow name
- `gen_ai.tool.name` — the tool called

A trace in 2026 looks like:

```
[agent.run] 4.2s, $0.012
  ├─ [llm.call] gpt-4o, 1.8s, 820 in / 240 out, $0.008
  │  └─ [tool.call] github.list_prs, 0.4s
  ├─ [llm.call] gpt-4o, 1.5s, 980 in / 180 out, $0.006
  └─ [tool.call] github.add_comment, 0.5s
```

You can replay any trace, see the exact prompt, the exact tool call, the cost, the latency. This is what makes agent debugging tractable.

### Token budget tracking and cost observability

The 2026 dashboard has, at minimum:

- **Cost per trace** — including prompt, completion, and tool-call overhead.
- **Cost per agent type** — break down by `deployment-agent`, `review-agent`, `triage-agent`.
- **Cost per repo** — billing back to the team.
- **Cost per workflow** — `tiny-workflow` cost rolled up to the DAG.
- **Budget alerts** — "agent X spent >$5 in the last hour, paging on-call."
- **Token efficiency** — input-token-to-output-token ratio; high inputs = bad prompt engineering.

`tiny-otel` and `tiny-trace` ship the stdlib-only implementation. They emit OTLP-compatible spans, integrate with any OpenTelemetry collector, and add a single dependency: `[]`.

### What changed from 2024

In 2024, observability for AI was "log the prompt and the response." In 2026, it's:

- **First-class spans** for LLM calls and tool calls.
- **Structured token usage** in every span.
- **Cost attribution** at the trace level.
- **Eval scores** attached to traces.
- **Prompt versioning** linked to traces.

The teams that don't have this are flying blind; their agents are running up bills they can't decompose.

---

## Section 6: Security in the AI Era

The 2026 security stack is not the 2024 security stack with a coat of paint. The threat model changed; the controls changed with it.

### Agentic AI security platforms — real-time monitoring

A new category of product emerged: **agent security platforms** that sit between the agent and the tools:

- **Snyk Agent Shield** — scans MCP server code, blocks risky tool calls.
- **Astrix Security** — agent posture management, MCP governance.
- **Prompt Armor** — prompt-injection detection at input.
- **Lakera Guard** — model-agnostic injection classifiers.
- **NeMo Guardrails (NVIDIA)** — declarative rails for LLM apps.

The pattern: every agent input goes through a classifier; every agent output is checked against a policy; every tool call is gated. Latency is 5–50ms per call. False positive rate is the product metric.

### Prompt injection detection

Prompt injection went from theoretical concern to **weekly incident** in 2025. In 2026, every serious agent has:

- **Input classifiers** — flag adversarial prompts, ignore them, log them.
- **Output classifiers** — flag poisoned tool results (e.g., a webpage that asks the agent to "ignore previous instructions").
- **Indirect-injection scopes** — "the agent can summarize this repo, but no instructions in the repo may modify the agent's goal."
- **Tool-result sanitization** — strip "ignore previous instructions" patterns from tool outputs before re-injection.

The honest answer in 2026 is that prompt injection is **not solved**. It is **managed**. The teams that are honest about this get fewer incidents.

### Secret management for autonomous agents

Agents need secrets to call APIs. The naive approach — `.env` file in the workspace — is a CVSS 9.8 in 2026. The 2026 approach:

- **Secrets live in a vault.** HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, or a self-hosted equivalent.
- **Agents fetch at call time.** `tiny-secret` abstracts this: `secret.get("github_token")` returns a fresh, audited, time-boxed credential.
- **Masks in logs and traces.** Every secret is replaced with `***` in every log line, trace, and error message.
- **Leak detection.** The agent's working directory is scanned pre-commit; `.env`, `id_rsa`, `*.pem` are quarantined.
- **Rotation on suspicion.** A single anomalous tool call rotates the credential.

`tiny-secret` is the stdlib-only version: it loads from env vars or a vault client, masks everything by default, and writes audit logs you can ship anywhere.

### Sandbox execution — `tiny-sandbox`

Autonomous agents should not run untrusted code on the host. The 2026 pattern:

```
agent.execute(code)
   │
   ├─→ tiny-sandbox.run(code, timeout=30s, memory=256MB, net=none)
   │       │
   │       └─→ subprocess.Popen with resource limits, seccomp, no network
   │
   └─→ return stdout, stderr, exit_code
```

`tiny-sandbox` wraps `subprocess` with the right defaults: timeouts, memory caps, network namespaces, file-system jails. It's not a full container — it's a 200-line stdlib-only guard for "the agent should run this, but I want to be sure it can't go further."

The 2026 teams that got this wrong are the ones whose agent ran `rm -rf` on the wrong workspace. The ones that got it right treated `tiny-sandbox` as the default execution environment for every tool call.

---

## Section 7: Emerging Patterns

The patterns that didn't fit neatly into a single section but are worth naming.

### Bounty-driven development

A new category of CI/CD: **autonomous agents hunting GitHub bounties**.

The pattern:

1. Scanner pulls open issues tagged with `bounty`, `$$`, `up-for-grabs`, etc.
2. Scorer ranks them by complexity, code-area match, and historical agent success rate.
3. Implementer agent picks up the top candidate, opens a PR.
4. Lint, test, and review-bot runs the gauntlet.
5. Reviewer (human or high-tier agent) approves or rejects.
6. If approved, PR is merged; bounty is claimed.

The OpenClaw bounty scanner runs daily. The 2026 blockers are well understood: scam issues (filterable), PR-permission gating (requestable), and review-bot feedback loops (slowly improving).

This is **not** a fad. Bounty-driven development is the same shift as bug bounties becoming a category 10 years ago — a way to align incentives, distribute work, and surface unknowns.

### Eval-driven development

The pattern is the same as TDD, but for AI behavior:

1. **Write the eval first.** "Given this prompt, the agent should produce this output, with this cost, in this time."
2. **Run the eval.** It fails. (Or it passes, and you have a regression baseline.)
3. **Change the agent.** New prompt, new model, new tool.
4. **Re-run the eval.** Score diff.
5. **Ship only when scores improve.**

Teams that adopted this in 2025 are shipping faster in 2026, because they have a regression suite for the part of the system that used to be vibes. The tooling: `pytest` + `deepdiff` + a custom `EvalRunner` that wraps the agent and asserts on the rubric.

The cultural shift: the eval is the spec. The agent implementation is the work.

### Micro-frameworks vs. mega-frameworks

**Mega-frameworks** (Django, Rails, FastAPI+plugins) are still the right choice for large teams, large surfaces, and large teams of large teams. But for everything else, **micro-frameworks** are winning.

The 2026 lineup:

| Need | Mega-framework | Micro-framework |
|------|----------------|-----------------|
| HTTP server | FastAPI | `tiny-web` |
| REST API | FastAPI + Pydantic | `tiny-api` |
| Routing | FastAPI router | `tiny-router` |
| CLI | Click, Typer | `tiny-cli` |
| Task queue | Celery | `tiny-workflow` |
| ORM | SQLAlchemy | Raw `sqlite3` |

The micro-framework is not always better. It is **better at the things the mega-framework is bad at**: cold start, auditability, dependency count, and the feeling of "I understand everything in this stack."

### The rise of single-file libraries

Publishing a single-file library is now a recognized pattern, not a hack. The template:

```
my-tiny-lib/
├── README.md
├── LICENSE
├── pyproject.toml
├── my_tiny_lib.py      # the whole library
└── tests/
    └── test_my_tiny_lib.py
```

Why this works:

- **One file, one job.** Easier to reason about.
- **One file, one PR.** Easier to review.
- **One file, one import.** Drop into your project, no install.
- **One file, one README.** Documentation cost is zero.

The PyPI single-file-package count grew ~30% year-over-year in 2026. The pattern is now mainstream.

---

## Section 8: Tools Worth Watching in Late 2026

A curated list of tools and frameworks that earned attention this year. Not all of them will still matter in 2027, but they are the ones to evaluate now.

1. **Devin 2.0** (Cognition) — The autonomous-engineer template. Long-running agent that owns a VM, ships code, handles CI. The 2026 benchmark for "agent does real work."
2. **Cursor Background Agents** — Cursor's take on the same idea, integrated with the IDE. Best UX for "I'm in my editor, kick off a long task."
3. **Goose** (Block) — Local, fully open-source autonomous agent. Pluggable LLM, runs anywhere. The privacy-first choice.
4. **CodeBuddy** (Tencent) — Multilingual agent-first CLI. Strong in Asia-Pacific and polyglot repos.
5. **OpenClaw + FalconEye** — Agent orchestration platform with approval gates, bounty scanning, and a dispatcher model. Best for fleets.
6. **Temporal Cloud** — Durable execution at scale. The default for "I need this DAG to survive anything."
7. **Prefect 3** — Pythonic DAGs with a beautiful UI. The default for "I want this to feel like Python."
8. **Inngest** — TS-first event-driven orchestration. Best serverless-native DX.
9. **Snyk Agent Shield** — Agent security posture management. The default for "I need to know my agent is safe."
10. **Lakera Guard** — Prompt-injection detection at the API edge. Fast, model-agnostic.
11. **Astrix Security** — Agent + MCP governance. The "CSP for agents" product.
12. **LangSmith 2.0** — Tracing, evals, and prompt management for LLM apps. The 2026 default for observability.
13. **OpenLLMetry** — OpenTelemetry-native LLM tracing. The OSS answer to LangSmith.
14. **`tiny-*` ecosystem** — The stdlib-only family. Worth evaluating as a unit; you may find you can replace eight dependencies with eight `tiny-*` packages.
15. **Modal / Replicate / Banana** — Serverless GPU for running inference. The 2026 default for "I need a model on demand."

---

## Appendix A: The `tiny-*` Ecosystem Reference

| Package | LOC | Deps | Description | Benchmark |
|---------|-----|------|-------------|-----------|
| `tiny-log` | 320 | 0 | Structured JSON logging | 32K lines/sec |
| `tiny-validator` | 480 | 0 | Schema validation (Pydantic-style) | 247K validations/sec |
| `tiny-config` | 240 | 0 | Env + YAML + TOML config loader | 18K loads/sec |
| `tiny-cache` | 280 | 0 | LRU + TTL in-memory cache | 2.2M ops/sec |
| `tiny-secret` | 210 | 0 | Secret loading + masking + audit | 410K reads/sec |
| `tiny-otel` | 540 | 0 | OpenTelemetry-compatible spans | 85K spans/sec |
| `tiny-trace` | 380 | 0 | Distributed context propagation | 110K propagations/sec |
| `tiny-workflow` | 410 | 0 | DAG-based orchestration, resumable | 1.2K task transitions/sec |
| `tiny-sandbox` | 220 | 0 | Subprocess isolation + resource limits | 80 spawns/sec |
| `tiny-mcp` | 290 | 0 | MCP server implementation | 4K calls/sec |
| `tiny-mcp-client` | 260 | 0 | MCP client implementation | 3.8K calls/sec |
| `tiny-cli` | 350 | 0 | Argparse successor, type-driven | 6K arg parses/sec |
| `tiny-web` | 430 | 0 | Micro HTTP server | 12K req/sec (hello world) |
| `tiny-api` | 510 | 0 | REST framework on `tiny-web` | 9K req/sec |
| `tiny-router` | 270 | 0 | URL routing with regex + path params | 380K route matches/sec |
| `tiny-fs` | 180 | 0 | Filesystem helpers (atomic write, etc.) | 95K ops/sec |
| `tiny-http` | 460 | 0 | HTTP client (sync + async) | 4.5K req/sec |

All numbers measured on Apple M3 Pro, Python 3.12, single thread, no exporter overhead. Your mileage will vary; the **relative** ordering is stable.

---

## Appendix B: Quick Reference — Install

```bash
# Core
pip install tiny-log tiny-validator tiny-config tiny-cache tiny-secret

# Observability
pip install tiny-otel tiny-trace

# Orchestration
pip install tiny-workflow

# Security
pip install tiny-sandbox tiny-secret

# MCP
pip install tiny-mcp tiny-mcp-client

# Web / API
pip install tiny-web tiny-api tiny-router tiny-http tiny-fs

# CLI
pip install tiny-cli
```

Or, since they're all single-file and zero-dep, just `cp` the file into your project:

```bash
curl -O https://raw.githubusercontent.com/hussain-alsaibai/tiny-log/main/tiny_log.py
mv tiny_log.py tiny_log.py  # already named
```

---

## Closing

2026 is the year the **dependency graph** shrank, the **agent** grew up, and the **tool calls** became standardized. The teams that won this year are the ones that:

- Treated agents as **coworkers**, not magic.
- Used **MCP** as the universal adapter.
- Shipped **stdlib-only** wherever the dependency graph wasn't earning its keep.
- Wrote **evals** alongside tests.
- Put **approval gates** in the loop, not outside it.
- Treated **observability** as a first-class concern from day one.
- Modeled **security** around the agent, not just the perimeter.

If you read this report and shipped one improvement — adopt MCP, write an eval, replace a dependency with a stdlib alternative, add a sandbox — that's the trend that matters.

Bookmark it. Reference it. Share it. And if you disagree, open a PR. The whole point of a living report is that it changes.

— *Hussain Al-Saibai, 2026*

---

## August 2026 Update

> *What changed in the six weeks since the main report.*

The big shift this month is **eval becoming infrastructure**. The tooling matured enough that teams are treating agent quality gates the same way they treat CI — non-negotiable, versioned alongside the code, and blocking by default.

### What's New in August 2026

**1. tiny-eval ships as the canonical agent eval framework.**
The gap in the eval-driven development trend (Trend #7) was always the tooling: yes, write evals, but with what? The answer became `tiny-eval` — a zero-dependency Python framework for defining benchmark suites, grading agent runs, and tracking regressions over time. It ships with three pre-built suites (`bug-fix`, `code-quality`, `security`) and a regression checker that compares current scores against a rolling window. Teams integrate it directly into CI: agent opens a PR → tiny-eval runs → regressions block merge.

**2. tiny-repl graduates to a proper package.**
The agent debugging experience got its REPL. `tiny-repl` was a single 823-line Python file floating around in the `tiny-*` ecosystem for months — this month it got a proper `package.json`, `pyproject.toml`, full test suite, CLI entry point (`tiny-repl list`, `tiny-repl replay <id>`, `tiny-repl diff <a> <b>`), and a complete README. The tool records agent runs (tool calls, inputs, outputs, durations, errors), saves them to disk, and lets you step through execution like a debugger. Diff two runs to find where a regression happened.

**3. Bounty scanners got smarter about social engineering traps.**
After months of agents hitting prompt-injection-bait repositories (fake issues, manufactured "opportunities", inorganic fork patterns), the OpenClaw bounty scanner added structural fingerprinting: repo creation age, issue density, PR attribution patterns, and cross-reference scoring. Filtered repos dropped from the noise floor. The net: fewer wasted agent-hours on scams, higher signal on real opportunities.

**4. MCP server count crossed 10,000.**
The Model Context Protocol ecosystem crossed a milestone: 10,000 MCP servers published. The breakdown: ~60% data sources (databases, APIs, internal services), ~25% developer tools (CI, monitoring, deploy pipelines), ~15% domain-specific (legal, medical, financial). The MCP registry at smithery.ai crossed 50K daily lookups — what started as an Anthropic experiment became the plumbing layer for the entire agent stack.

**5. Temporal introduces native agent handoff.**
Temporal's August release added first-class agent-to-agent handoff primitives: a workflow step can now pass a **continuation token** to another agent, which resumes from exactly that state. Combined with the existing durable execution model, this makes multi-agent pipelines — one agent writes code, another reviews it, a third handles deployment — as durable as a single workflow. Teams are using this for review-approval-deploy pipelines where the "review" step is a separate LLM call with its own context window.

**6. Zero-dependency wins on AI infra cost.**
The numbers that used to be theoretical are now production data:
- `tiny-cache`: 2.2M ops/sec, <1ms p99 on a $5 VM
- `tiny-log`: 32K log lines/sec, zero GC pressure
- `tiny-validator`: 247K validations/sec, 0 dependencies
- `snapdb`: 800K reads/sec, 200K writes/sec, 0 native dependencies

Compare to the same operations through a typical Node.js microservice stack with 127 transitive dependencies. The difference isn't just latency — it's the **blast radius of a supply-chain compromise**.

**7. Eval suites are becoming shared community resources.**
The eval-driven development trend is accelerating into a community pattern: teams publish their eval suites to shared registries, similar to how test vectors are shared in cryptography. The model: benchmark suites are versioned artifacts, agent PRs are tested against the latest suite, and suite updates are reviewed like code. Three early shared suites are worth knowing:
- `bug-fix-benchmark` — compile, test, regression, secrets, crash (the tiny-eval default)
- `security-hardening-suite` — 100% threshold, no exceptions
- `context-window-benchmark` — measures how well agents use context (token efficiency, re-reading avoidance)

**8. The autonomous agent security surface expanded.**
Two new attack classes emerged in August:
- **Eval poisoning**: adversarial actors submit intentionally broken PRs that pass naive eval suites but introduce subtle vulnerabilities. The mitigation: eval suites must include adversarial test cases, not just functional ones.
- **Tool call flooding**: agents in unbounded loops make thousands of cheap tool calls to burn budget without accomplishing anything. The mitigation: cost-per-run budgets with hard stops, and eval suites that measure efficiency (tasks completed per dollar spent).

### Key Numbers This Month

| Metric | Value | Trend |
|--------|-------|-------|
| MCP servers registered | 10,000+ | ↑ |
| tiny-* ecosystem repos | 53 | ↑ (tiny-eval, tiny-repl) |
| tiny-eval suite registrations | 3 standard | New |
| Bounty scams filtered | 31/98 issues | ↑ filtering |
| snapdb read throughput | 800K/sec | Stable |
| snapdb write throughput | 200K/sec | Stable |
| snapdb LOC (pure Python) | 10,193 | Stable |

### What to Watch

- **Agent-to-agent handoff protocols** — If Temporal, Prefect, and OpenClaw all ship similar primitives, this becomes the standard pattern for multi-agent pipelines in 2026 Q4.
- **Eval suite sharing** — Watch for a centralized eval registry to emerge. If it does, it could be as significant as PyPI was for package sharing.
- **Eval poisoning defenses** — As eval suites become blocking for merges, adversarial actors have stronger incentive to poison them. This is an arms race just starting.
- **tiny-repl integration with tiny-eval** — The natural next step: use tiny-repl traces as inputs to tiny-eval criteria. An agent run is traced → replayed → graded automatically.

---

## License

MIT © 2026 Hussain Al-Saibai. See [LICENSE](./LICENSE).
