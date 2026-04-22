# Mock Exam 1 — Answer Key

**Do not read before taking `mock-exam-1.md`.**

Distribution audit (pre-grade):
- **Correct-answer position:** A=10, B=10, C=10, D=10 (balanced)
- **Longest option correct:** 11 / 40 (27.5%, under the 30% bar)
- **Subtly-wrong questions** (4): Q5, Q19, Q28, plus Q32 as the enum-hallucination trap

---

## Answer key

| # | Answer | Primary domain | Rationale (one line) |
|---|---|---|---|
| 1 | A | D2 | Scoping = config-time access; `tool_choice` = per-request invocation. Different mechanisms. |
| 2 | B | D2 | Programmatic prerequisites enforce invariants; prompts are hope, not enforcement. |
| 3 | D | D5 | Transient failures with `retry_after` retry inside the tool; surface only on exhaustion. |
| 4 | C | D1 | Honour the two-factor policy for deletion; refunds can run autonomously under the $500 line. |
| 5 | A | D5 | System-prompt instruction is **not** enforcement — PII containment needs boundary redaction. |
| 6 | B | D1 | Over-$500 policy says escalate; structured summary lets the human decide. Splitting the amount evades the policy. |
| 7 | C | D2 | Enriched outputs beat multiple round-trips when fields change the agent's action. |
| 8 | C | D4 | Structured fields + narrative + record links — neither full transcript nor pure prose. |
| 9 | D | D5 | Isolate when shared tools could produce duplicate side-effects in the reviewer's session. |
| 10 | A | D4 | `detected_pattern` says WHY the classification fired; debuggable; `confidence` just says how sure. |
| 11 | D | D1 | Coordinator reasons over findings — it doesn't collect, it decides. |
| 12 | D | D1 | Narrow query → narrow subagent set. "All five" is the more-≠-better trap. |
| 13 | A | D1 | Subagents self-attribute via `{source, finding, evidence, confidence}`; coordinator doesn't track origin externally. |
| 14 | B | D1 | Summary by default; raw only when downstream must reason over details. |
| 15 | C | D1 | Exit on quality threshold, not iteration count. Fixed caps are arbitrary. |
| 16 | B | D2 | Least privilege + scoping as hard boundary — the exam's recurring architectural principle. |
| 17 | C | D1 | Targeted narrower query to the relevant subagent. Don't re-run everyone. |
| 18 | B | D1 | Cite conflicting findings with sources; let a human adjudicate rather than fabricate resolution. |
| 19 | D | D2 | Scoping is enforcement, not a suggestion — user requests cannot override configured scope. (INCORRECT statement.) |
| 20 | A | D1 | Coverage with citations and explicit gaps. Call count, wall-clock, and cost don't measure quality. |
| 21 | A | D3 | Grep with `output_mode: "files_with_matches"` — content search returning paths. Glob matches names, not content. |
| 22 | D | D3 | Edit expresses change as find-and-replace; minimal diff, no accidental over-writes. |
| 23 | D | D3 | Bash with the pytest command; MCP wrapper is over-engineered for one command. |
| 24 | B | D2 | Least privilege — only the scopes the agent actually uses. Full admin is insecure, gh-via-Bash is messy. |
| 25 | C | D5 | The reviewing session shares context with the generator and anchors on the same reasoning — isolation restores independence. |
| 26 | A | D4 | Enum + few-shot anchoring prevents category drift. Free-text and raw numerics both drift without anchors. |
| 27 | D | D3 | `-p <prompt> --output-format json --json-schema <schema>` is the canonical CI output pattern. |
| 28 | B | D4 | Field-level validation is still needed — `tool_choice` prevents tool-name hallucination, not argument hallucination. (INCORRECT statement.) |
| 29 | C | D3 | `files_with_matches` is the explicit file-paths-only mode. `filenames_only` is not a real option. |
| 30 | A | D2 | Per-invocation scoped MCP; one agent, many configurations. Matches least privilege across repos. |
| 31 | B | D4 | `tool_use` input schema + forced `tool_choice` is API-level JSON Schema enforcement; prompts are not. |
| 32 | C | D4 | "other" + detail field — prevents the enum-hallucination trap where the model silently picks the nearest valid value. |
| 33 | A | D4 | Downstream-blocking = required; otherwise optional. Blanket "all required" obscures real extraction failures. |
| 34 | B | D4 | Schema = format; business rule = meaning. Separate passes prevent the model from forcing a silent resolution. |
| 35 | D | D4 | Normalisation rules belong in the tool parameter description with target format + examples. |
| 36 | C | D5 | Triage before retry — retriable iff the model made a parse mistake on data the source contains. |
| 37 | A | D4 | System prompt or tool description — examples travel with the agent, not the individual request. |
| 38 | C | D4 | Force the specific extraction tool; downstream has no use for free-form prose. |
| 39 | B | D4 | `detected_pattern` exposes the textual cue that triggered a classification — targeted debugging, not wholesale reruns. |
| 40 | D | D4 | Required with no default — absence surfaces as extraction failure the downstream can route to human review. |

---

## Per-domain question counts

| Domain | Questions | Weight in real exam |
|---|---|---|
| D1 Agentic Architecture | Q4, Q6, Q11, Q12, Q13, Q14, Q15, Q17, Q18, Q20 (10) | 27% |
| D2 Tool Design & MCP | Q1, Q2, Q7, Q16, Q19, Q24, Q30 (7) | 18% |
| D3 Claude Code Config | Q21, Q22, Q23, Q27, Q29 (5) | 20% |
| D4 Prompt Engineering & Structured Output | Q8, Q10, Q26, Q28, Q31, Q32, Q33, Q34, Q35, Q37, Q38, Q39, Q40 (13) | 20% |
| D5 Context Management & Reliability | Q3, Q5, Q9, Q25, Q36 (5) | 15% |

**Blueprint notes:** D4 is over-represented (13 vs ~8 target) because Scenario 6 is entirely structured-extraction territory. D3 is slightly under (5 vs ~8) — real exam will include more Claude Code config questions that Mock 1 doesn't stress. Keep this in mind when interpreting the per-domain score.

---

## Grading guide

- **32+ / 40 (80%+):** Ready for real exam.
- **28-31 / 40 (70-77%):** Close. One more mock + targeted remediation.
- **< 28 / 40:** Re-teach weak task statements before Mock 2.

Per-scenario reporting:
- Scenario 1 (Q1-10) — customer support / orchestration
- Scenario 3 (Q11-20) — multi-agent research
- Scenario 4 (Q21-30) — developer productivity / Agent SDK
- Scenario 6 (Q31-40) — structured data extraction
