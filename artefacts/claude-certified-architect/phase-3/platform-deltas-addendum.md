# Readiness-Report Addendum — Platform Deltas Since Course Start

> **Status:** standalone addendum, captured 2026-06-22. **Merge this section into `readiness-report.md` when Phase 3 closes** (the readiness report does not exist yet — Sessions 12–15 are still pending). Full domain-by-domain detail lives in `../phase-1/platform-deltas.md`.

## Why this matters for go/no-go

The course was calibrated to the exam guide at start (2026-03-31). The exam guide is unchanged, but the Claude platform it tests moved. Mock scores earned before these updates may **overstate D4 readiness** and slightly understate D1/D5 coverage. Re-test the affected items before the go/no-go call.

## Pre-exam checklist (do before Mock 2 / booking)

- [ ] **D4 — Structured Output (20%):** internalise the decision tree — *structured outputs* (`output_config.format`) vs *strict tool use* (`strict: true`) vs *tool_use-for-schema* (legacy). The old "force a tool call to get JSON" is now a distractor. `output_format` param is deprecated.
- [ ] **D5 — Context (15%):** add **compaction** and **context editing** as named primitives for "preserving long-context"; know editing-prunes vs compaction-summarizes vs memory-persists.
- [ ] **D1 — Agentic (27%):** awareness-level recognition of **Managed Agents**, **programmatic tool calling**, and **tool search** as orchestration options (hub-and-spoke / self-attribution core is unchanged).
- [ ] **D2 — Tool Design (18%):** prescriptive ("call this when…") tool descriptions; `tool_choice` now also has `{type:"none"}` and `disable_parallel_tool_use`.
- [ ] **Verify exam format against the official guide PDF.** Public community guides now describe **60 questions / 120 minutes**; the plan's Mock Exams use 40 questions / ~60 min. If confirmed, re-size Mock 1/2 to 60q/120min so exam-pressure calibration is accurate.

## Impact on the readiness decision

- Treat D4 as **not yet re-validated** until a structured-outputs vs strict-tool-use item is included in Mock 2.
- D1/D5 core teaching remains sound; the new primitives are additive recognition, not a rewrite.
- No change to the 720/1000 pass mark or the 5-domain weighting.
