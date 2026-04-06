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

### Session 4: Diagnostic Schema Patterns & Structured Output (D4 focus — 75% on V2)
**Objective:** Fix the D4 gap — detected_pattern fields, schema design for debuggability, and the broader principle of designing schemas that enable post-hoc analysis

**Teach block — detected_pattern and Diagnostic Fields:**
- [ ] The problem: model outputs a classification but you can't debug *why* — false positives are opaque
- [ ] `detected_pattern` field: forces the model to articulate the specific textual evidence that triggered its decision
- [ ] Why this works: the model must reason explicitly about evidence, which (a) improves accuracy and (b) makes failures debuggable
- [ ] Contrast with confidence scores: confidence tells you *how sure*, not *why* — useless for root-cause analysis
- [ ] Contrast with secondary_classification: tells you what else it could be, not what evidence drove the primary choice
- [ ] Worked example: document classifier with detected_pattern — tracing a false positive from "terms of service" in a marketing email

**Teach block — Schema Design for Production Debugging:**
- [ ] Principle: every schema should answer "when this output is wrong, how will I find out why?"
- [ ] Patterns: `detected_pattern` (evidence), `extraction_notes` (ambiguity flags), `source_location` (where in the document), `normalization_applied` (what transformations were done)
- [ ] These fields have near-zero cost (model fills them naturally) but enormous debugging value
- [ ] When to use each: classification tasks → detected_pattern; extraction tasks → source_location + extraction_notes; transformation tasks → normalization_applied

**Teach block — Retriable vs Non-Retriable Failures in Validation Loops:**
- [ ] Format/parse errors (wrong date format, misread field): retriable — append error to prompt, model self-corrects
- [ ] Missing source data (field doesn't exist in document): non-retriable — no amount of retrying will create data that isn't there
- [ ] The triage step: before retrying, check the source document to determine if the data exists. Only retry if the error is a model mistake, not a data gap.
- [ ] `detected_pattern` fields help here too: if the model says "extracted date from paragraph 3" and paragraph 3 doesn't contain a date, that's a hallucination, not a parse error

- [ ] 8–10 exam-style practice questions (scenario-based, D4 primary, crossing D2/D5)
**Key concepts:** detected_pattern, diagnostic schema fields, retriable vs non-retriable, schema-driven debugging
**Resources:** Anthropic structured output docs, tool_use best practices

---

## Phase 2: Scenario-Based Practice (Sessions 5–9)

*Work through all 6 exam scenarios with exam-style questions crossing multiple domains.*

### Session 5: Scenario 1 — Customer Support Resolution Agent
**Objective:** Design a customer support agent with MCP tools, escalation, and compliance enforcement
- [ ] Agent architecture for high-ambiguity requests (returns, billing, account issues)
- [ ] MCP tool design: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`
- [ ] Escalation decision-making: when to escalate vs resolve autonomously
- [ ] Programmatic prerequisites: blocking `process_refund` until `get_customer` completes
- [ ] Structured handoff summaries for human agents
- [ ] 8-10 exam-style practice questions
**Primary domains:** D1, D2, D5

### Session 6: Scenario 2 — Code Generation with Claude Code
**Objective:** Configure Claude Code for team development workflows
- [ ] CLAUDE.md hierarchy: user-level, project-level, directory-level, `.claude/rules/`
- [ ] Custom slash commands and skills: `.claude/commands/` vs `~/.claude/skills/`
- [ ] Plan mode vs direct execution: when to use each
- [ ] Iterative refinement: input/output examples, test-driven iteration, interview pattern
- [ ] 8-10 exam-style practice questions
**Primary domains:** D3, D5

### Session 7: Scenario 3 — Multi-Agent Research System
**Objective:** Design a coordinator-subagent research system
- [ ] Coordinator agent: query analysis, dynamic subagent selection, result synthesis
- [ ] Scope partitioning: distinct subtopics or source types per subagent
- [ ] Iterative refinement loops: evaluate synthesis, re-delegate for gaps
- [ ] Tool distribution: scoped tools per subagent role, avoiding cross-specialisation
- [ ] 8-10 exam-style practice questions
**Primary domains:** D1, D2, D5

### Session 8: Scenarios 4 & 5 — Developer Productivity + CI/CD Integration
**Objective:** Build developer tools with Claude Agent SDK and integrate Claude Code into CI/CD
- [ ] Built-in tools: Read, Write, Edit, Bash, Grep, Glob — when to use each
- [ ] MCP server integration for developer productivity
- [ ] CI/CD integration: `-p` flag, `--output-format json`, `--json-schema`
- [ ] Session context isolation: why the generating session shouldn't review its own code
- [ ] Review criteria design: explicit categories, few-shot examples for severity levels
- [ ] 8-10 exam-style practice questions
**Primary domains:** D2, D3, D4

### Session 9: Scenario 6 — Structured Data Extraction
**Objective:** Design a reliable data extraction system with validation
- [ ] JSON schemas via `tool_use` for guaranteed schema compliance
- [ ] `tool_choice` configuration: `auto`, `any`, forced selection
- [ ] Few-shot examples for handling varied document structures
- [ ] Validation loops: retry with specific errors, identify non-retriable failures
- [ ] Schema design: required vs optional fields, enum + "other" + detail patterns
- [ ] Format normalisation rules alongside strict schemas
- [ ] 8-10 exam-style practice questions
**Primary domains:** D4, D5

---

## Phase 3: Mock Exams (Sessions 10–12)

### Session 10: Mock Exam 1
**Objective:** Full exam simulation — 4 scenarios, 40 questions, timed (~60 min)
- [ ] 4 randomly selected scenarios from the 6
- [ ] 10 questions per scenario, exam-style multiple choice
- [ ] Timed to simulate exam pressure
- [ ] Score and per-domain breakdown
**Target:** 80%+ (32/40) for exam readiness

### Session 11: Mock Exam 1 Review & Remediation
**Objective:** Deep-dive on missed questions, targeted re-teaching of weak spots
- [ ] Review every missed question — understand why the correct answer is correct
- [ ] Identify patterns: which domains/task statements are consistently weak
- [ ] Targeted mini-teach on weak task statements
- [ ] 10 additional practice questions on weak areas

### Session 12: Mock Exam 2
**Objective:** Second full simulation with different scenario selection
- [ ] 4 different scenarios (prioritise ones not seen in Mock 1)
- [ ] 10 questions per scenario, exam-style multiple choice
- [ ] Timed
- [ ] Score and per-domain breakdown
- [ ] Compare improvement from Mock 1
**Target:** 80%+ (32/40)

---

## Phase 4: Final Review (Sessions 13–15, optional)

*Only needed if Mock Exam scores are below 80%.*

### Session 13: Mock Exam 2 Review & Weak Spot Remediation
**Objective:** Final targeted remediation based on Mock 2 results
- [ ] Review missed questions from Mock 2
- [ ] Deep-teach any remaining weak task statements
- [ ] Practice questions on persistent weak areas

### Session 14: Rapid-Fire Speed Drill
**Objective:** Build speed and confidence across all domains
- [ ] 50 questions, all domains, rapid-fire format
- [ ] Focus on exam traps and common distractors
- [ ] Identify any last-minute gaps

### Session 15: Final Review & Exam Strategy
**Objective:** Exam-day preparation
- [ ] Review exam format: 4 of 6 scenarios, multiple choice, no penalty for guessing
- [ ] Time management strategy: ~1.5 min per question
- [ ] Quick-reference summary of key concepts per domain
- [ ] Last confidence check on weakest areas
