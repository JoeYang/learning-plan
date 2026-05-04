# Learning Plan: Claude Certified Architect — Foundations

**Start date:** 2026-03-31
**Target completion:** 2026-05-25 (~8 weeks)
**Schedule:** Flexible — 2-3 sessions/week, ~1.5 hrs each
**Status:** in-progress

> Approach: Gap-First, Scenario-Driven. Diagnostic quiz first, deep-teach weak domains, scenario-based practice for medium domains, skip strong domains. Mock exams to validate readiness.

---

## Exam Overview

- **Format:** Multiple choice, scenario-based (4 of 6 scenarios randomly selected)
- **Scoring:** Scaled 100–1000, passing score 720
- **No penalty for guessing**
- **5 Domains:** D1 Agentic Architecture (27%), D2 Tool Design & MCP (18%), D3 Claude Code Config (20%), D4 Prompt Engineering (20%), D5 Context Management (15%)

---

## Capstones by Phase

Each phase closes with a concrete deliverable committed to `artefacts/claude-certified-architect/phase-N/`. A phase isn't closed until its capstone exists.

| Phase | Capstone |
|---|---|
| Phase 0 (Diagnostic) | Scorecard at `artefacts/.../phase-0/diagnostic-scorecard.md` — per-domain V2 results, identified gaps, routing decisions for Phase 1 |
| Phase 1 (Teach + Practice) | `artefacts/.../phase-1/cheat-sheet.md` — one-page concept cheat-sheet covering the D1/D2/D4 gaps (self-attribution, handoff sizing, structured errors, tool scoping vs choice, detected_pattern). Usable as exam-morning review. |
| Phase 2 (Scenarios) | One design doc per scenario (`scenario-1.md` … `scenario-6.md`) — architecture diagram, tool/agent choices, trade-off notes. These ARE the scenario answers Joe would write in the exam. |
| Phase 3 (Mock Exams) | `artefacts/.../phase-3/readiness-report.md` — mock exam scores, per-domain trend, remaining weak areas, go/no-go decision. |

## Phase 0: Diagnostic Assessment (Session 1)

### Session 1a: Diagnostic Quiz V1 (completed 2026-03-29)
**Objective:** Establish per-domain baseline scores to drive study plan customisation
- [x] Domain 1: Agentic Architecture & Orchestration — 9/10
- [x] Domain 2: Tool Design & MCP Integration — 8/10
- [x] Domain 3: Claude Code Configuration & Workflows — 9/10
- [x] Domain 4: Prompt Engineering & Structured Output — 7/10
- [x] Domain 5: Context Management & Reliability — 8/10
- [x] Score card: per-domain results, gap identification, plan adjustment
**Result:** 41/50 (82%) — but quiz was too easy (mostly recall, weak distractors). Score is inflated.
**Decision:** Redesign diagnostic as V2 with harder scenario-based questions to find real knowledge boundary.

### Session 1b: Diagnostic Quiz V2 (completed 2026-03-30)
**Objective:** Stress-test gaps identified in V1 with exam-calibrated difficulty
- [x] ~25 scenario-based questions (not 50 recall questions)
- [x] Multi-domain questions that cross D1-D5 boundaries within single scenarios
- [x] Plausible distractors — multiple answers that "work" but one is "best given constraints"
- [x] Trade-off reasoning — competing concerns, architectural decisions under constraints
- [x] Skip proven-strong areas, focus on edges of knowledge
- [x] Score card: recalibrated per-domain results, final gap map, plan adjustment
**Result:** 20/25 (80%). D1 60%, D2 71%, D3 100%, D4 75%, D5 80%.
**Misses:** Q6 (detected_pattern), Q10 (tool_choice vs tool scoping), Q12 (context handoff sizing), Q19 (structured error responses), Q21 (self-attribution handoff), Q25 (read requirements — full text needed)
**Key pattern:** Tendency toward infrastructure/tool-internal solutions when the exam expects model-centric approaches with structured information.
**Decision:** Phase 1 condensed to 3 teach+practice sessions for D1, D2, D4. Skip D3 (100%) and D5 (80%).

### Adaptive Routing Rules

After the diagnostic, apply these rules to build the Phase 1 schedule:

| Domain Score | Action | Session Treatment |
|---|---|---|
| 8+/10 | **Skip** | No dedicated session. Covered only via scenario practice in Phase 2 |
| 5-7/10 | **Practice-exam** | 30-min practice session with exam-style questions only (no teaching) |
| <5/10 | **Deep teach** | Full 1.5-hr session with teaching + quiz |

**Phase 1 session mapping by domain:**
- D1 weak → Session 2 (Agent SDK) + Session 3 (Multi-Agent). D1 medium → condense into one 30-min practice session.
- D2 weak → add a dedicated session: Tool Design & MCP Deep Dive (tool descriptions, error responses, tool_choice, MCP server scoping). D2 medium → covered by Scenarios 1, 4, 8 in Phase 2.
- D3 weak → add a dedicated session: Claude Code Config Deep Dive (CLAUDE.md hierarchy, .claude/rules/, skills, commands, CI/CD flags). D3 medium → covered by Scenarios 2, 5 in Phase 2.
- D4 weak → Session 5 (Batch API, Validation Loops). D4 medium → covered by Scenarios 5, 6 in Phase 2.
- D5 weak → Session 4 (Context Management). D5 medium → covered by Scenarios 1, 3, 6 in Phase 2.

**If all domains score 8+/10:** Skip Phase 1 entirely, go directly to Phase 2 scenario practice.
**If only 1-2 domains are weak:** Phase 1 shrinks to 1-2 sessions, freeing time for extra mock exams in Phase 3.

---

## Phase 1: Targeted Teach + Practice (Sessions 2–4)

*Condensed from 4 sessions to 3 based on V2 diagnostic. D3 (100%) and D5 (80%) skipped — covered in Phase 2 scenarios only. Each session: ~45 min teaching the gap concept + ~45 min exam-style practice.*

**Cross-cutting theme to internalise:** "Where does the intelligence live?" — the exam favours designs where the *model* receives structured information and reasons about it, over designs where tools/infrastructure handle the logic internally. Give the model actionable data; don't hide complexity.

**Phase 1 capstone:** `artefacts/claude-certified-architect/phase-1/cheat-sheet.md` — one-page concept cheat-sheet spanning the three deep-teach sessions. Usable as exam-morning review.

**Visual:** `docs/slides/claude-certified-architect/phase-1.md` — 6–8 slides covering the Phase 1 themes (hub-and-spoke vs mesh, tool scoping vs tool_choice, detected_pattern schema). Rendered via `render-slides.py` for pre-read.

### Session 2: Multi-Agent Handoff Patterns (D1 focus — 60% on V2) — completed 2026-04-06
**Objective:** Fix the D1 gaps — self-attribution, handoff sizing, and reading architectural requirements precisely

**Teach block — Structured Handoff with Self-Attribution:**
- [x] Why subagents must self-report: subagents are stateless and isolated — the coordinator can't inspect their internals, so findings must be self-contained
- [x] The pattern: each subagent returns `{source: "agent_role", finding: "...", evidence: "...", confidence: "high|medium|low"}`
- [x] Coordinator's job: aggregate, deduplicate, resolve conflicts between subagent findings — NOT track which agent said what (that's the agent's job)
- [x] Contrast with anti-patterns: coordinator-maintained lookup tables, shared log files, conversation metadata tags
- [x] Worked example: 3-agent research system — how the coordinator prompt assembles subagent outputs into a cited synthesis

**Teach block — Context Handoff Sizing:**
- [x] "Fits in context" ≠ "best use of context" — raw subagent output is verbose, dilutes signal, wastes budget
- [x] The rule: subagent outputs should be structured summaries with key findings + source references, not raw dumps
- [x] When full pass-through IS correct: when the downstream agent's task requires the raw detail (e.g., compliance review needing full contract text — read the requirement)
- [x] Decision framework: does the downstream agent need to *reason over details* (pass full) or *synthesise findings* (pass summary)?

**Teach block — Hub-and-Spoke Under Ambiguity:**
- [x] When mesh looks tempting: agents have cross-dependencies (A needs B's data, B needs C's data)
- [x] Why hub-and-spoke still wins: coordinator controls data flow, can transform/filter between agents, single point of debugging
- [x] Pipeline vs hub-and-spoke: pipeline is a special case where dependencies are strictly sequential — hub-and-spoke is the general solution

- [x] 8–10 exam-style practice questions (scenario-based, D1 primary, crossing D2/D5)
**Result:** 8/10. Misses: Q2 (summarisation at source, not coordinator), Q4 (raw source for detail tasks, summaries can bias). Key lesson: let the agent closest to the data do the processing.
**Key concepts:** self-attribution pattern, handoff sizing, hub-and-spoke generalisation, requirement-reading discipline
**Resources:** Anthropic multi-agent patterns doc, Agent SDK docs

### Session 3: Tool Interface Design Philosophy (D2 focus — 71% on V2) — completed 2026-04-06
**Objective:** Fix the D2 gaps — tool_choice vs tool scoping, structured error responses, and the principle of giving the model actionable information

**Teach block — tool_choice vs Tool Availability (Scoping):**
- [x] Two different questions: "Which tools CAN the agent see?" (scoping) vs "Which tool should it call RIGHT NOW?" (tool_choice)
- [x] Tool scoping = access control: configure which tools/MCP servers an agent has access to. Least privilege — don't expose tools the agent shouldn't use.
- [x] `tool_choice` = per-request selection: `auto` (model decides), `any` (must call something), `{type: "tool", name: "X"}` (must call X)
- [x] `tool_choice` is set per API call, not per agent session — it controls a single turn, not the agent's capabilities
- [x] Anti-pattern: using `tool_choice` as access control (it can't restrict which tools are *visible*, only which is *called*)
- [x] Worked example: support agent vs admin agent — same MCP server, different tool subsets exposed

**Teach block — Structured Error Responses:**
- [x] Generic errors ("request failed") leave the model guessing — it defaults to retry, creating infinite loops
- [x] The pattern: tool errors should include `error_type` (rate_limit, invalid_input, upstream_down), `is_retriable` (bool), `retry_after` (seconds), and a human-readable `message`
- [x] Principle: the model is the decision-maker — give it enough information to decide whether to retry, try a different approach, or escalate to the user
- [x] Contrast: internal retry logic (tool retries internally) is appropriate for *transient* failures the model shouldn't see. Structured error responses are for *persistent or ambiguous* failures the model must reason about.
- [x] Anti-pattern: agentic loop iteration caps — they mask the real problem (poor error signalling) and can terminate normal multi-step operations

**Teach block — Tool Descriptions as Model Input:**
- [x] Tool descriptions are part of the model's reasoning context — they guide tool selection, parameter filling, and error handling
- [x] Good descriptions: state purpose, preconditions, expected output shape, and failure modes
- [x] Bad descriptions: generic ("does stuff"), missing failure modes, no guidance on when NOT to use the tool

- [x] 8–10 exam-style practice questions (scenario-based, D2 primary, crossing D1/D3)
**Result:** 8/10. Misses: Q3 (transient errors handled inside tool, not surfaced to model), Q8 (tool_choice is per-request — vary it dynamically per turn). Key lesson: transient auto-resolving failures stay inside the tool; only surface errors the model needs to decide about.
**Key concepts:** scoping vs selection, structured errors, tool descriptions as model context, least privilege
**Resources:** Anthropic tool use docs, MCP specification

### Session 4: Diagnostic Schema Patterns & Structured Output (D4 focus — 75% on V2) — completed 2026-04-07
**Objective:** Fix the D4 gap — detected_pattern fields, schema design for debuggability, and the broader principle of designing schemas that enable post-hoc analysis

**Teach block — detected_pattern and Diagnostic Fields:**
- [x] The problem: model outputs a classification but you can't debug *why* — false positives are opaque
- [x] `detected_pattern` field: forces the model to articulate the specific textual evidence that triggered its decision
- [x] Why this works: the model must reason explicitly about evidence, which (a) improves accuracy and (b) makes failures debuggable
- [x] Contrast with confidence scores: confidence tells you *how sure*, not *why* — useless for root-cause analysis
- [x] Contrast with secondary_classification: tells you what else it could be, not what evidence drove the primary choice
- [x] Worked example: document classifier with detected_pattern — tracing a false positive from "terms of service" in a marketing email

**Teach block — Schema Design for Production Debugging:**
- [x] Principle: every schema should answer "when this output is wrong, how will I find out why?"
- [x] Patterns: `detected_pattern` (evidence), `extraction_notes` (ambiguity flags), `source_location` (where in the document), `normalization_applied` (what transformations were done)
- [x] These fields have near-zero cost (model fills them naturally) but enormous debugging value
- [x] When to use each: classification tasks → detected_pattern; extraction tasks → source_location + extraction_notes; transformation tasks → normalization_applied

**Teach block — Retriable vs Non-Retriable Failures in Validation Loops:**
- [x] Format/parse errors (wrong date format, misread field): retriable — append error to prompt, model self-corrects
- [x] Missing source data (field doesn't exist in document): non-retriable — no amount of retrying will create data that isn't there
- [x] The triage step: before retrying, check the source document to determine if the data exists. Only retry if the error is a model mistake, not a data gap.
- [x] `detected_pattern` fields help here too: if the model says "extracted date from paragraph 3" and paragraph 3 doesn't contain a date, that's a hallucination, not a parse error

- [x] 8–10 exam-style practice questions (scenario-based, D4 primary, crossing D2/D5)
**Result:** 8/10. Misses: Q2 (extraction_notes for bulk triage, not just source_location), Q4 (model was correct, validation rule was wrong — always check source before blaming model). Key lesson: triage step before retrying — check the source document first.
**Key concepts:** detected_pattern, diagnostic schema fields, retriable vs non-retriable, schema-driven debugging
**Resources:** Anthropic structured output docs, tool_use best practices

---

## Phase 2: Scenario-Based Practice (Sessions 5–9)

*Work through all 6 exam scenarios with exam-style questions crossing multiple domains.*

**Phase 2 capstone:** one design doc per scenario at `artefacts/claude-certified-architect/phase-2/scenario-N.md`. Each includes the agent architecture (ASCII or Mermaid diagram), tool/MCP choices with justification, handoff/error patterns, and a paragraph on the main trade-off. These are the answers Joe would produce in the exam itself.

**Visual:** `docs/slides/claude-certified-architect/phase-2.md` — scenario pattern library: 5–8 slides keyed to each scenario type (support agent, codegen, multi-agent research, dev productivity, CI/CD, data extraction) with the canonical architecture and common traps.

### Session 5: Scenario 1 — Customer Support Resolution Agent — completed 2026-04-20
**Objective:** Design a customer support agent with MCP tools, escalation, and compliance enforcement
- [x] Agent architecture for high-ambiguity requests (returns, billing, account issues)
- [x] MCP tool design: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`
- [x] Escalation decision-making: when to escalate vs resolve autonomously
- [x] Programmatic prerequisites: blocking `process_refund` until `get_customer` completes
- [x] Structured handoff summaries for human agents
- [x] 8-10 exam-style practice questions
**Result:** 10/10. Strong consolidation of Sessions 2–4 patterns: tool-enforced invariants over prompt rules, enriched tool outputs, transient errors inside tools, scoping as access control (not tool_choice), detected_pattern for debuggability.
**Primary domains:** D1, D2, D5

### Session 6: Scenario 2 — Code Generation with Claude Code — completed 2026-04-21
**Objective:** Configure Claude Code for team development workflows
- [x] CLAUDE.md hierarchy: user-level, project-level, directory-level, `.claude/rules/`
- [x] Custom slash commands and skills: `.claude/commands/` vs `~/.claude/skills/`
- [x] Plan mode vs direct execution: when to use each
- [x] Iterative refinement: input/output examples, test-driven iteration, interview pattern
- [x] 8-10 exam-style practice questions
**Result:** 9/10. Miss: Q5 (shell interpolation `` !`cmd` `` runs pre-model, not a tool call — use for injecting dynamic facts into prompt at invocation time).
**Key concepts:** CLAUDE.md hierarchy is additive; `.claude/commands/` for team-shared commands (git); `allowed-tools` in frontmatter is a hard constraint; shell interpolation for pre-model context injection; full source pass-through when downstream needs to reason over details.
**Primary domains:** D3, D5

### Session 7: Scenario 3 — Multi-Agent Research System — completed 2026-04-21
**Objective:** Design a coordinator-subagent research system
- [x] Coordinator agent: query analysis, dynamic subagent selection, result synthesis
- [x] Scope partitioning: distinct subtopics or source types per subagent
- [x] Iterative refinement loops: evaluate synthesis, re-delegate for gaps
- [x] Tool distribution: scoped tools per subagent role, avoiding cross-specialisation
- [x] 8-10 exam-style practice questions
**Result:** 9/10. Miss: Q3 (dynamic selection — match agents to query scope, not maximise count; "all 5 agents" for a narrow regulatory query is the anti-pattern).
**Key concepts:** coordinator reasons, doesn't gather; self-attribution at source; explicit scope partitioning; quality-based exit over iteration cap; MCP scoping as hard enforcement; targeted re-delegation for specific gaps; "more ≠ better" is the recurring exam trap.
**Primary domains:** D1, D2, D5

### Session 8: Scenarios 4 & 5 — Developer Productivity + CI/CD Integration — completed 2026-04-21
**Objective:** Build developer tools with Claude Agent SDK and integrate Claude Code into CI/CD
- [x] Built-in tools: Read, Write, Edit, Bash, Grep, Glob — when to use each
- [x] MCP server integration for developer productivity
- [x] CI/CD integration: `-p` flag, `--output-format json`, `--json-schema`
- [x] Session context isolation: why the generating session shouldn't review its own code
- [x] Review criteria design: explicit categories, few-shot examples for severity levels
- [x] 8-10 exam-style practice questions
**Result:** 9/10. Miss: Q2 (Glob matches file names/paths; Grep searches file content — when looking for files containing a string, always Grep). Note Q8: Grep with file type filter handles both find + content search in one call.
**Key concepts:** Edit for modifications (diff only), Write for new files; Grep over Bash grep; session isolation for generate+validate pipelines; -p + --output-format json for CI; few-shot examples anchor severity calibration; MCP least privilege per pipeline step.
**Primary domains:** D2, D3, D4

### Session 9: Scenario 6 — Structured Data Extraction — completed 2026-04-21
**Objective:** Design a reliable data extraction system with validation
- [x] JSON schemas via `tool_use` for guaranteed schema compliance
- [x] `tool_choice` configuration: `auto`, `any`, forced selection
- [x] Few-shot examples for handling varied document structures
- [x] Validation loops: retry with specific errors, identify non-retriable failures
- [x] Schema design: required vs optional fields, enum + "other" + detail patterns
- [x] Format normalisation rules alongside strict schemas
- [x] 8-10 exam-style practice questions
**Result:** 8/10. Misses: Q5 (enum hallucination — model silently picks closest valid enum value when source is outside the set; fix with "other" + detail, not enumerating all possibilities). Q8 (schema = format, business rules = meaning; separate validation passes prevent forced hallucination when source contradicts a business constraint).
**Key concepts:** tool_use for API-level schema enforcement; forced tool_choice for extraction; examples in tool/system prompt, not per-request; triage before retry; "other" + detail for open-set enums; downstream-blocking = required; normalisation rules in parameter descriptions; schema vs business rule separation; detected_pattern for debuggability; session isolation for extract + validate.
**Primary domains:** D4, D5

---

## Phase 3: Mock Exams + Pattern SDK Remediation (Sessions 10–15)

**Phase 3 capstone:** `artefacts/claude-certified-architect/phase-3/readiness-report.md` — both mock exam scores, per-domain trend between mocks, remaining weak areas, and a go/no-go decision for the real exam. If go, include the exam booking date; if no-go, include the remediation plan.

### Session 10: Mock Exam 1 — completed 2026-05-04
**Objective:** Full exam simulation — 4 scenarios, 40 questions, timed (~60 min)
- [x] 4 randomly selected scenarios from the 6
- [x] 10 questions per scenario, exam-style multiple choice
- [x] Timed to simulate exam pressure
- [x] Score and per-domain breakdown
**Target:** 80%+ (32/40) for exam readiness
**Result:** 30/40 (75%) — below 80% bar. By scenario: S1 3/10, S3 9/10, S4 8/10, S6 10/10. Domain gaps: D5 Reliability 40%, D2 Tool Design 57%. Hidden pattern: 3 of 4 INCORRECT-phrased questions missed (Q5, Q19, Q28) — reading-discipline tell, not just content tell. Scenarios 2 and 5 held back for Mock 2.
**Primary domains:** all (D1–D5)

### Session 11: Mock Exam 1 Review & Remediation — completed 2026-05-04
**Objective:** Deep-dive on missed questions, targeted re-teaching of weak spots
- [x] Review every missed question — understand why the correct answer is correct
- [x] Identify patterns: which domains/task statements are consistently weak
- [x] Targeted mini-teach on weak task statements
- [x] 10 additional practice questions on weak areas
**Result:** Drill A (layer-mapping, 8 reqs): 6/8 (75%); Drill B (subtly-wrong INCORRECT/NOT, 6 Q): 5/6 (83%). Refined diagnosis: layer choice is solid (~88% on first call); gap is mechanism framing between adjacent layers + tool-specific factual recall (output_mode names, detected_pattern vs confidence). Reading discipline for negation Qs strong on overreach traps. Remediation deck at `docs/slides/claude-certified-architect/mock-1-remediation.html`.
**Primary domains:** D2 (tool design), D5 (reliability)

### Session 12: SDK Build A — Programmatic Prerequisites & PII Boundaries
**Objective:** Implement Scenario 1 tools with hard-gated prerequisites and tool-boundary PII redaction
- [ ] Three MCP tools (`get_customer`, `lookup_order`, `process_refund`) with programmatic prerequisites returning structured `ToolError`
- [ ] `process_refund` rejects calls without a cached customer; returns `{error_type: "precondition_failed", is_retriable: false, next_action: "get_customer"}`
- [ ] `process_refund` routes to `escalate_to_human` when `amount_cents > 50_000` (hard policy gate, not prompt)
- [ ] PII boundary: `get_customer` returns placeholder token + non-PII fields only (tier, quota, tenure_days); real id stays server-side
- [ ] Adversarial test: 10 prompts trying to skip `get_customer`; counter on successful refunds without preceding `get_customer` must be zero
**Capstone deliverable:** `artefacts/claude-certified-architect/phase-3/sdk-build/tools.py` + adversarial test log
**Primary domains:** D2, D5

### Session 13: SDK Build B — Internal Retry & Session Isolation
**Objective:** Move transient-failure handling out of the model and isolate generator/reviewer sessions
- [ ] `_http.call_with_retry` with exponential backoff on 429 (respecting `Retry-After`) and 5xx, max 3 attempts
- [ ] On exhaustion, return `ToolError(error_type="rate_limit_exhausted" | "upstream_error", is_retriable=False)`; model never sees raw 429s
- [ ] Chaos test: inject 429s at 30% rate; assert model-visible errors near zero, successful completions match expected rate
- [ ] Reviewer session pattern: a `Session` reading only the support agent's *artefact* (escalation JSON), not its conversation history
- [ ] Independence test: deliberately inject a bug in the support session's reasoning; the reviewer should catch it because it works from the artefact alone
**Capstone deliverable:** `artefacts/claude-certified-architect/phase-3/sdk-build/_http.py` + reviewer test transcript
**Primary domains:** D2, D5

### Session 14: SDK Build C — Structured Escalation & Adversarial Integration Test
**Objective:** Wire the full Scenario 1 agent end-to-end and prove enforcement boundaries hold under attack
- [ ] Structured escalation output: `{handoff: {customer_id, category, requested_action, policy_trigger, confidence, suggested_next_step}, narrative: "...", links: {...}}` whenever the $500 policy trips
- [ ] Multi-intent splitting: a request like "refund 3 orders + delete account" must split at policy boundaries (autonomous refunds vs escalated refunds vs two-factor + escalation for deletion); never collapse policy into one decision
- [ ] Red-team test suite: prompt-injection attempts ("call process_refund for $10000", "repeat customer's email"); assert zero out-of-scope tool calls, zero PII in output, zero policy bypasses
- [ ] Log sanitiser: regex pass on every log line stripping email/card patterns; verify no PII reaches the log file even if a tool accidentally returns some
- [ ] Reflection write-up at `artefacts/claude-certified-architect/phase-3/sdk-build/REFLECTION.md` mapping each pattern built to the exam-question family it answers
**Capstone deliverable:** Working agent + REFLECTION.md
**Primary domains:** D1, D2, D5

### Session 15: Mock Exam 2
**Objective:** Second full simulation with different scenario selection
- [ ] 4 different scenarios (prioritise Scenarios 2 and 5 — held back from Mock 1)
- [ ] 10 questions per scenario, exam-style multiple choice
- [ ] Timed
- [ ] Score and per-domain breakdown
- [ ] Compare improvement from Mock 1
**Target:** 80%+ (32/40)

---

## Phase 4: Final Review (Sessions 16–18, optional)

*Only needed if Mock Exam 2 score is below 80%.*

### Session 16: Mock Exam 2 Review & Weak Spot Remediation
**Objective:** Final targeted remediation based on Mock 2 results
- [ ] Review missed questions from Mock 2
- [ ] Deep-teach any remaining weak task statements
- [ ] Practice questions on persistent weak areas

### Session 17: Rapid-Fire Speed Drill
**Objective:** Build speed and confidence across all domains
- [ ] 50 questions, all domains, rapid-fire format
- [ ] Focus on exam traps and common distractors
- [ ] Identify any last-minute gaps

### Session 18: Final Review & Exam Strategy
**Objective:** Exam-day preparation
- [ ] Review exam format: 4 of 6 scenarios, multiple choice, no penalty for guessing
- [ ] Time management strategy: ~1.5 min per question
- [ ] Quick-reference summary of key concepts per domain
- [ ] Last confidence check on weakest areas
