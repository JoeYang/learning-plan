# Harness vs Custom Agent — Decision Framework

When to build on an existing harness (Claude Code + skills/MCP, OpenClaw) vs building a custom AI agent with your own infrastructure.

## What a Harness Gives You (Free)

- Agentic loop, tool execution, error recovery
- Context management, `/compact`, session persistence
- File read/write/edit, streaming, multi-turn state
- UI (CLI/IDE), permission system, model selection
- MCP support, hooks framework, cost tracking

**You customize via:** skills, commands, CLAUDE.md rules, `.claude/rules/`, MCP servers, hooks, agent definitions.

## What You Build Yourself (Custom Agent)

All of the above, plus: gateway, guardrails, eval pipeline, auth/rate limiting, monitoring, UI/UX, deployment, failover, scaling, rollback.

**Using:** Claude API / Agent SDK / LangGraph + your infra.

## Decision Framework

### 1. User Surface

| User | Where they work | Best fit |
|---|---|---|
| Your dev team | Terminal, IDE | Harness (skills, commands, MCP) |
| DevOps/SRE | Terminal, Slack, dashboards | Harness or thin wrapper |
| Internal non-devs | Web UI, Slack | Custom agent (needs UI) |
| Customers | Your product | Custom agent (must control UX) |
| Automated systems | API calls, CI/CD | Either — depends on volume |

### 2. Workflow Complexity

**Harness-friendly:**
- "Review this PR"
- "Analyze these logs"
- "Generate a report from this data"
- "Refactor this module"
- "Run this playbook"
- "Query our internal docs"

**Needs custom agent:**
- Multi-user collaborative editing
- Real-time streaming dashboard
- Embedded in another product's UI
- Custom approval workflow with non-developer stakeholders
- High-throughput batch processing (10K+ requests/hour)

The harness model is: **one user, one session, task-oriented, developer-adjacent**. If your use case fits that shape, use the harness.

### 3. Integration Depth

| Shallow (harness works) | Deep (custom agent needed) |
|---|---|
| Add tools via MCP | Custom agentic loop logic |
| Add rules via CLAUDE.md | Non-standard tool execution |
| Add workflows via skills | Custom context management |
| Hook into existing events | Custom UI rendering |
| | Embedded in another service |
| | Custom auth/multi-tenancy |

### 4. Volume and Latency

| Scenario | Fit |
|---|---|
| 10-100 uses/day by developers | Harness |
| 1,000+/day automated pipeline | Custom — need your own scaling, queuing, cost control |
| Sub-second latency required | Custom — harness has overhead from the full agentic loop |
| Batch processing overnight | Custom — use Batch API directly |

### 5. Control vs Speed

| Approach | Timeline | Coverage |
|---|---|---|
| Harness skill | 1-2 days | 90% of what you need |
| Harness + MCP servers + hooks | 1-2 weeks | 95% of what you need |
| Agent SDK (thin wrapper) | 2-4 weeks | Full control, some guardrails |
| Full custom (everything DIY) | 2-4 months | Full control, everything custom |

## Summary

**Use the harness when:**
- Users are developers
- Task is session-based (start → do work → done)
- CLI/IDE is an acceptable interface
- You can express the capability as tools (MCP) + instructions (skills/rules)
- Volume is <1,000/day
- You want to ship in days, not months

**Build custom when:**
- Users are NOT developers (need custom UI)
- It's embedded in another product
- You need multi-tenancy, custom auth, or fine-grained access control
- Volume is high (10K+/day) and you need your own scaling
- You need a non-standard agentic loop (custom routing, branching logic)
- Latency requirements are strict (sub-500ms)

**The middle ground:**
- Claude Code as a subprocess called from your service
- `claude -p "..." --output-format json` in a pipeline
- MCP servers that connect the harness to your internal systems

Most teams over-build. **80% of internal AI tooling can be a skill + a couple MCP servers**, shipped in a few days. The other 20% — customer-facing features, high-volume pipelines, embedded product integrations — genuinely need custom agents.
