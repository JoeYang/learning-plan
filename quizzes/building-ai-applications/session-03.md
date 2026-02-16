# Quiz: Session 3 — Model Context Protocol (MCP)

**Instructions:** Choose the best answer(s) for each question. Answers at the bottom.

---

### Q1. What problem does MCP solve that raw tool use (Session 2) doesn't?

A) MCP makes LLMs faster at calling tools
B) MCP standardises tool definitions so any client can discover and use any server — write once, use everywhere
C) MCP allows the LLM to execute tools directly without your code
D) MCP replaces the need for API keys

---

### Q2. What are the three core primitives of MCP?

A) Request, Response, Error
B) Tools, Resources, Prompts
C) Input, Output, Schema
D) Client, Server, Transport

---

### Q3. How does defining a tool in MCP (FastMCP) compare to Session 2's manual approach?

A) MCP requires more code — you must write both the function and the JSON schema
B) MCP generates the JSON schema automatically from Python type hints and docstrings
C) MCP tools are slower because of the protocol overhead
D) There is no difference — you still write the same JSON schema

---

### Q4. What is the difference between an MCP Tool and an MCP Resource?

A) Tools are free, resources cost money
B) Tools are functions the LLM can call with arguments; resources are data identified by URI that the LLM can read
C) Tools are for reading data, resources are for writing data
D) There is no practical difference

---

### Q5. In the `.mcp.json` config, the transport is `stdio`. What does this mean?

A) The server runs as a remote HTTP service
B) Claude Code launches the server as a subprocess and communicates via stdin/stdout
C) The server uses WebSockets for bidirectional communication
D) The server reads from a file on disk

---

### Q6. Your trading-db MCP server has a `run_sql` tool that only allows SELECT statements. Why is this restriction important?

A) INSERT/UPDATE/DELETE are slower and would cause timeouts
B) It prevents the LLM from accidentally modifying or deleting data — LLMs should have read-only access to production data
C) SQLite doesn't support write operations through MCP
D) The restriction is unnecessary — LLMs are careful with data

---

### Q7. You have two MCP servers: `trading-ops` (system metrics) and `trading-db` (database queries). Claude Code can use tools from BOTH in a single conversation. Why is this powerful?

A) It's not — you should combine everything into one server
B) Composability — independent servers can be developed, tested, and deployed separately, but combined at query time
C) Two servers are always faster than one
D) It's required by the MCP specification

---

### Q8. MCP Prompts (like `investigate_client`) are:

A) System prompts that override the LLM's instructions
B) Reusable, parameterised prompt templates that guide the LLM through a specific workflow
C) Mandatory instructions the LLM must follow exactly
D) Cached responses that skip the LLM entirely

---

### Q9. You want to give Claude Code access to your company's ServiceNow instance. What's the best approach?

A) Hardcode ServiceNow API calls into every prompt
B) Build (or use an existing) MCP server that wraps the ServiceNow API, then add it to .mcp.json
C) Copy all ServiceNow data into a local file and use the read_file tool
D) Fine-tune a model on ServiceNow data

---

### Q10. You built a trading-ops MCP server with simulated data. To make it production-ready, you'd replace the simulated data with real API calls (e.g., to Datadog, Splunk). What else would you need to add?

A) Nothing — just swap the data source and it's production-ready
B) Authentication, error handling, rate limiting, and input validation to prevent injection
C) A web UI for the MCP server
D) A separate MCP server for each API

---

## Answer Key

**Q1: B** — MCP's value is standardisation. In Session 2, tools were hardcoded in your app. With MCP, any MCP-compatible client (Claude Code, Claude Desktop, your own apps) can discover and use any MCP server. Build the server once, use it from anywhere.

**Q2: B** — Tools (functions the LLM can call), Resources (data identified by URI the LLM can read), and Prompts (reusable prompt templates for guided workflows).

**Q3: B** — With FastMCP, you write a Python function with type hints and a docstring. The SDK generates the JSON schema automatically. In Session 2, you wrote the schema by hand — more verbose, more error-prone.

**Q4: B** — Tools take arguments and perform actions (like querying with filters). Resources are static or semi-static data identified by a URI (like `config://thresholds` or `runbook://fix-reconnection`). The LLM reads resources for context and calls tools for dynamic queries.

**Q5: B** — stdio transport means Claude Code starts the MCP server as a child process and communicates via stdin/stdout pipes. Simple, local, no network configuration needed. The alternative is SSE (HTTP) for remote servers.

**Q6: B** — LLMs can hallucinate or misinterpret intent. A SELECT-only restriction ensures the worst case is a bad query, not deleted data. In production, always give AI read-only access to data stores unless you have explicit human approval for writes.

**Q7: B** — Composability is MCP's killer feature. Each server is an independent, testable unit with a single responsibility. At query time, Claude Code combines tools from multiple servers seamlessly. You can add/remove servers without changing any code.

**Q8: B** — MCP Prompts are templates with parameters (like `investigate_client(client_id="HEDGE_FUND_A")`). They guide the LLM through a structured workflow — which tools to call, in what order, and what to report. They're suggestions, not hard constraints.

**Q9: B** — Build an MCP server that wraps the ServiceNow API. This gives Claude Code (and any other MCP client) access to ServiceNow through standardised tools. Community implementations already exist (michaelbuckner/servicenow-mcp).

**Q10: B** — Swapping data is step one, but production requires: authentication (API keys, tokens), error handling (timeouts, retries, graceful degradation), rate limiting (don't DDoS your monitoring system), and input validation (prevent SQL injection in run_sql, validate parameters). Security is non-negotiable for production tools.
