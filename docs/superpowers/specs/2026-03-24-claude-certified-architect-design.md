# Design: Claude Certified Architect — Foundations Study Plan

**Date:** 2026-03-24
**Status:** Approved
**Goal:** Pass the Claude Certified Architect — Foundations exam (720+/1000)

---

## Overview

A gap-first, scenario-driven study plan that uses a diagnostic quiz to customise the learning path. Deep-teach weak domains, practice-exam medium domains, skip strong domains. Mock exams validate readiness.

## Exam Details

- **Format:** Multiple choice, scenario-based. 4 of 6 scenarios randomly selected per exam.
- **Scoring:** Scaled 100-1000, passing score 720 (~72%)
- **No penalty for guessing**
- **Domains:**
  - D1: Agentic Architecture & Orchestration (27%)
  - D2: Tool Design & MCP Integration (18%)
  - D3: Claude Code Configuration & Workflows (20%)
  - D4: Prompt Engineering & Structured Output (20%)
  - D5: Context Management & Reliability (15%)

## Exam Scenarios

1. Customer Support Resolution Agent (D1, D2, D5)
2. Code Generation with Claude Code (D3, D5)
3. Multi-Agent Research System (D1, D2, D5)
4. Developer Productivity with Claude (D2, D3, D1)
5. Claude Code for Continuous Integration (D3, D4)
6. Structured Data Extraction (D4, D5)

## Approach: Gap-First, Scenario-Driven

```
Session 1: Diagnostic (50 questions, 10 per domain)
    |
    +-- Score 8+/10 --> SKIP (practice only if time permits)
    +-- Score 5-7/10 --> PRACTICE-EXAM (scenario questions)
    +-- Score <5/10  --> DEEP TEACH + practice
    |
    v
Phase 1: Deep teach weak domains (Sessions 2-5, adaptive)
    |
    v
Phase 2: Scenario-based practice (Sessions 6-10)
    |
    v
Phase 3: Mock exams (Sessions 11-13)
    |
    +-- Score 80%+ --> Ready, take exam
    +-- Score <80% --> Add remediation sessions
    |
    v
Phase 4: Final review (Sessions 14-16, optional)
```

## Plan Structure

| Phase | Sessions | Content | Format |
|-------|----------|---------|--------|
| 0: Diagnostic | 1 | 50-question diagnostic across all domains | Quiz only |
| 1: Deep Teach | 2-5 | Weak domains (adaptive based on diagnostic) | Teach + quiz |
| 2: Scenario Practice | 6-10 | All 6 exam scenarios with exam-style questions | Scenario + quiz |
| 3: Mock Exams | 11-13 | Full exam simulations, timed, with review | Mock exam |
| 4: Final Review | 14-16 | Remediation, speed drills, exam strategy | Review (optional) |

## Candidate's Prior Knowledge

- Completed: Claude Code Mastery (12 sessions)
- In progress: Building AI Applications (17/24 — prompt engineering, RAG, agents, MCP, Agent SDK)
- Has built: MCP servers, custom agents/teams/hooks, custom skills
- Estimated strengths: D3 (Claude Code Config) — likely strong. D1 (Agentic) — medium-high.
- Estimated gaps: D5 (Context Management), D4 (Batch API, multi-pass review), D1 (SDK internals)

## Adaptive Routing (Post-Diagnostic)

Phase 1 sessions are not fixed — they are selected based on diagnostic scores:
- **8+/10:** Skip domain entirely (covered via scenario practice in Phase 2)
- **5-7/10:** 30-min practice-exam session only
- **<5/10:** Full 1.5-hr deep-teach session

All 5 domains have contingency sessions available if the diagnostic reveals weakness:
- D1 → Sessions 2-3 (Agent SDK + Multi-Agent)
- D2 → Dedicated session: Tool Design & MCP Deep Dive (added if needed)
- D3 → Dedicated session: Claude Code Config Deep Dive (added if needed)
- D4 → Session 5 (Batch API, Validation Loops)
- D5 → Session 4 (Context Management)

If all domains score 8+/10, Phase 1 is skipped entirely.

## Session Design Principles

- **Diagnostic drives everything** — Phase 1 reshuffled based on quiz results
- **Modular** — each session self-contained, no multi-session dependencies
- **Exam-format aligned** — all practice uses scenario-based multiple choice
- **Adaptive compression** — strong domains become practice-exam only (~30 min)
- **Target: 80%+ on mocks** for safety margin above 720 pass mark

## Schedule

- **Start:** 2026-03-31
- **End:** 2026-05-25 (8 weeks)
- **Pace:** 2-3 sessions/week, ~1.5 hrs each, flexible
- **Total sessions:** 13-16 (depending on mock results)

## Files Created

- `topics/claude-certified-architect.md` — topic definition
- `plans/claude-certified-architect.md` — day-by-day study plan
- `PROGRESS.md` — updated with new row in Active Topics

## Decision Log

| Decision | Chosen | Alternatives Considered | Why |
|----------|--------|------------------------|-----|
| Study approach | Gap-first, scenario-driven | Domain-sequential, scenario-first | Respects prior knowledge, matches exam format, gets to mocks quickly |
| Assessment method | Full diagnostic quiz upfront | Per-domain mini-quiz, self-assessment, hybrid | Provides hard data across all domains in one session |
| Session format | Mix: teach weak, practice-exam strong | Uniform teach+quiz, practice-exam heavy, hands-on labs | Maximises time efficiency given existing knowledge |
| Schedule | Flexible 2-3/week | Fixed 2/week, pause other topics, fixed 3/week | Accommodates 4 other active topics |
