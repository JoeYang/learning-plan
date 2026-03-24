# Learning Plan: Claude Certified Architect — Foundations

**Start date:** 2026-03-31
**Target completion:** 2026-05-25 (~8 weeks)
**Schedule:** Flexible — 2-3 sessions/week, ~1.5 hrs each
**Status:** not-started

> Approach: Gap-First, Scenario-Driven. Diagnostic quiz first, deep-teach weak domains, scenario-based practice for medium domains, skip strong domains. Mock exams to validate readiness.

---

## Exam Overview

- **Format:** Multiple choice, scenario-based (4 of 6 scenarios randomly selected)
- **Scoring:** Scaled 100–1000, passing score 720
- **No penalty for guessing**
- **5 Domains:** D1 Agentic Architecture (27%), D2 Tool Design & MCP (18%), D3 Claude Code Config (20%), D4 Prompt Engineering (20%), D5 Context Management (15%)

---

## Phase 0: Diagnostic Assessment (Session 1)

### Session 1: Full Diagnostic Quiz
**Objective:** Establish per-domain baseline scores to drive study plan customisation
- [ ] Domain 1: Agentic Architecture & Orchestration — 10 questions
- [ ] Domain 2: Tool Design & MCP Integration — 10 questions
- [ ] Domain 3: Claude Code Configuration & Workflows — 10 questions
- [ ] Domain 4: Prompt Engineering & Structured Output — 10 questions
- [ ] Domain 5: Context Management & Reliability — 10 questions
- [ ] Score card: per-domain results, gap identification, plan adjustment
**Key output:** Domains scoring 8+/10 → skip. 5-7/10 → practice-exam only. Below 5/10 → deep teach.
**Post-session:** Adjust Phase 1 sessions based on results.

---

## Phase 1: Deep Teach Weak Domains (Sessions 2–5)

*These sessions are provisionally planned based on likely gaps. The diagnostic quiz in Session 1 will confirm or reshuffle them.*

### Session 2: Agent SDK Internals — Agentic Loops & Lifecycle
**Objective:** Master the Agent SDK's internal mechanics at exam depth
- [ ] The agentic loop lifecycle: sending requests, inspecting `stop_reason` (`tool_use` vs `end_turn`), executing tools, returning results
- [ ] Model-driven decision-making vs pre-configured decision trees
- [ ] Adding tool results to conversation context for next-iteration reasoning
- [ ] Anti-patterns: parsing natural language for loop termination, arbitrary iteration caps, checking assistant text for completion
- [ ] `AgentDefinition` configuration: descriptions, system prompts, tool restrictions
- [ ] Hook patterns: `PostToolUse` for data normalisation, tool call interception for compliance
- [ ] Deterministic hooks vs probabilistic prompt instructions — when to use each
**Key concepts:** agentic loop, stop_reason, AgentDefinition, PostToolUse hooks, deterministic vs probabilistic enforcement
**Resources:** Claude Agent SDK docs, Anthropic agent patterns doc

### Session 3: Multi-Agent Orchestration & Session Management
**Objective:** Design coordinator-subagent systems and manage session state
- [ ] Hub-and-spoke architecture: coordinator manages all inter-subagent communication
- [ ] Subagent isolation: no inherited context, no shared memory between invocations
- [ ] Coordinator responsibilities: task decomposition, delegation, result aggregation, dynamic routing
- [ ] Context passing: including complete findings in subagent prompts, structured data formats for attribution
- [ ] Parallel subagent spawning: multiple `Task` tool calls in a single coordinator response
- [ ] `fork_session` for divergent exploration from a shared analysis baseline
- [ ] Named session resumption with `--resume <session-name>`
- [ ] When to resume vs start fresh with injected summaries
- [ ] Multi-step workflows: programmatic enforcement (hooks, prerequisite gates) vs prompt-based guidance
- [ ] Structured handoff protocols for human escalation
**Key concepts:** hub-and-spoke, subagent isolation, fork_session, session resumption, enforcement vs guidance
**Resources:** Claude Agent SDK docs, CppCon "Multi-Agent Systems" patterns

### Session 4: Context Management & Reliability
**Objective:** Master context window management — the domain where failures cascade everywhere
- [ ] Token budgeting: allocating context across system prompt, conversation history, tool results, and response
- [ ] `/compact` strategy: when to compact, focus instructions, what survives compaction
- [ ] Context injection hooks: `SessionStart` with compact matcher, `PreCompact`/`PostCompact`
- [ ] Long-document strategies: chunking, summarisation, map-reduce patterns
- [ ] Multi-turn conversation management: when to truncate, summarise, or start fresh
- [ ] Multi-agent context handoff: what to pass between agents, structured vs raw
- [ ] Stale tool results: why resuming with old tool results is unreliable
- [ ] Context window exhaustion prevention during multi-phase tasks
**Key concepts:** token budgeting, compact strategy, context injection, long-document chunking, context handoff
**Resources:** Anthropic docs — context management, Claude Code docs

### Session 5: Batch API, Validation Loops & Multi-Pass Review
**Objective:** Master production patterns for structured output and large-scale processing
- [ ] Message Batches API: 50% cost savings, 24-hour window, no latency SLA, `custom_id` for correlation
- [ ] When to use batch vs synchronous: blocking workflows (sync) vs overnight analysis (batch)
- [ ] Batch failure handling: resubmitting only failed documents, chunking oversized docs
- [ ] Retry-with-error-feedback: appending validation errors to prompt for self-correction
- [ ] When retries will vs won't work: format errors (retriable) vs missing source data (not retriable)
- [ ] Self-review limitations: same session can't effectively review its own output
- [ ] Independent review instances: separate Claude instance without generator's reasoning context
- [ ] Multi-pass review: per-file local analysis + cross-file integration pass
- [ ] Semantic validation vs syntax validation: tool_use eliminates syntax errors, not semantic errors
- [ ] `detected_pattern` fields for false-positive analysis
**Key concepts:** Batch API, custom_id, retry-with-feedback, self-review limitations, multi-pass review
**Resources:** Anthropic API docs — Message Batches, Claude Code review patterns

---

## Phase 2: Scenario-Based Practice (Sessions 6–10)

*Work through all 6 exam scenarios with exam-style questions crossing multiple domains.*

### Session 6: Scenario 1 — Customer Support Resolution Agent
**Objective:** Design a customer support agent with MCP tools, escalation, and compliance enforcement
- [ ] Agent architecture for high-ambiguity requests (returns, billing, account issues)
- [ ] MCP tool design: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`
- [ ] Escalation decision-making: when to escalate vs resolve autonomously
- [ ] Programmatic prerequisites: blocking `process_refund` until `get_customer` completes
- [ ] Structured handoff summaries for human agents
- [ ] 8-10 exam-style practice questions
**Primary domains:** D1, D2, D5

### Session 7: Scenario 2 — Code Generation with Claude Code
**Objective:** Configure Claude Code for team development workflows
- [ ] CLAUDE.md hierarchy: user-level, project-level, directory-level, `.claude/rules/`
- [ ] Custom slash commands and skills: `.claude/commands/` vs `~/.claude/skills/`
- [ ] Plan mode vs direct execution: when to use each
- [ ] Iterative refinement: input/output examples, test-driven iteration, interview pattern
- [ ] 8-10 exam-style practice questions
**Primary domains:** D3, D5

### Session 8: Scenario 3 — Multi-Agent Research System
**Objective:** Design a coordinator-subagent research system
- [ ] Coordinator agent: query analysis, dynamic subagent selection, result synthesis
- [ ] Scope partitioning: distinct subtopics or source types per subagent
- [ ] Iterative refinement loops: evaluate synthesis, re-delegate for gaps
- [ ] Tool distribution: scoped tools per subagent role, avoiding cross-specialisation
- [ ] 8-10 exam-style practice questions
**Primary domains:** D1, D2, D5

### Session 9: Scenarios 4 & 5 — Developer Productivity + CI/CD Integration
**Objective:** Build developer tools with Claude Agent SDK and integrate Claude Code into CI/CD
- [ ] Built-in tools: Read, Write, Edit, Bash, Grep, Glob — when to use each
- [ ] MCP server integration for developer productivity
- [ ] CI/CD integration: `-p` flag, `--output-format json`, `--json-schema`
- [ ] Session context isolation: why the generating session shouldn't review its own code
- [ ] Review criteria design: explicit categories, few-shot examples for severity levels
- [ ] 8-10 exam-style practice questions
**Primary domains:** D2, D3, D4

### Session 10: Scenario 6 — Structured Data Extraction
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

## Phase 3: Mock Exams (Sessions 11–13)

### Session 11: Mock Exam 1
**Objective:** Full exam simulation — 4 scenarios, 40 questions, timed (~60 min)
- [ ] 4 randomly selected scenarios from the 6
- [ ] 10 questions per scenario, exam-style multiple choice
- [ ] Timed to simulate exam pressure
- [ ] Score and per-domain breakdown
**Target:** 80%+ (32/40) for exam readiness

### Session 12: Mock Exam 1 Review & Remediation
**Objective:** Deep-dive on missed questions, targeted re-teaching of weak spots
- [ ] Review every missed question — understand why the correct answer is correct
- [ ] Identify patterns: which domains/task statements are consistently weak
- [ ] Targeted mini-teach on weak task statements
- [ ] 10 additional practice questions on weak areas

### Session 13: Mock Exam 2
**Objective:** Second full simulation with different scenario selection
- [ ] 4 different scenarios (prioritise ones not seen in Mock 1)
- [ ] 10 questions per scenario, exam-style multiple choice
- [ ] Timed
- [ ] Score and per-domain breakdown
- [ ] Compare improvement from Mock 1
**Target:** 80%+ (32/40)

---

## Phase 4: Final Review (Sessions 14–16, optional)

*Only needed if Mock Exam scores are below 80%.*

### Session 14: Mock Exam 2 Review & Weak Spot Remediation
**Objective:** Final targeted remediation based on Mock 2 results
- [ ] Review missed questions from Mock 2
- [ ] Deep-teach any remaining weak task statements
- [ ] Practice questions on persistent weak areas

### Session 15: Rapid-Fire Speed Drill
**Objective:** Build speed and confidence across all domains
- [ ] 50 questions, all domains, rapid-fire format
- [ ] Focus on exam traps and common distractors
- [ ] Identify any last-minute gaps

### Session 16: Final Review & Exam Strategy
**Objective:** Exam-day preparation
- [ ] Review exam format: 4 of 6 scenarios, multiple choice, no penalty for guessing
- [ ] Time management strategy: ~1.5 min per question
- [ ] Quick-reference summary of key concepts per domain
- [ ] Last confidence check on weakest areas
