# Platform Deltas Since Course Start (2026-03-31)

> **Why this exists.** The exam guide (5 domains, weights, 720/1000 pass) is unchanged since launch (2026-03-12). But the *Claude platform the exam tests* moved between course start and 2026-06-22. A few Phase-1/Phase-2 teach blocks now teach the legacy approach. This file is the exam-current correction, framed by domain. Fold into `cheat-sheet.md` when that capstone is built; it is also the source for the Phase-3 readiness-report addendum.
>
> Source of truth: current Claude-platform reference (cached 2026-05-26). Verify against the official exam guide PDF before exam day.

---

## 1. Structured Output — the new decision tree (D4, 20%) — HIGHEST PRIORITY

**What the course teaches (Session 9):** *"JSON schemas via `tool_use` for guaranteed schema compliance"* / *"tool_use for API-level schema enforcement."*

**What changed:** `tool_use`-for-schema is now the **legacy** path. Anthropic shipped first-class **Structured Outputs**. The exam-current "best given constraints" answer distinguishes three tools:

| You want to constrain… | Use | Mechanism |
|---|---|---|
| The model's **text response** to valid JSON | **Structured Outputs** | `output_config: {format: {type: "json_schema", schema: …}}` |
| A **tool's arguments** to a valid schema | **Strict tool use** | `strict: true` on the tool definition + `additionalProperties: false` |
| Schema compliance **+ debuggability of *why*** | Keep `detected_pattern` / diagnostic fields | Complementary — Session 4 still valid |

- **SDK helper:** `client.messages.parse()` (Pydantic / Zod) validates the response automatically — returns `parsed_output`.
- **Deprecated:** the top-level `output_format` parameter on `messages.create()` → use `output_config.format`.
- **Model support:** Opus 4.8, Sonnet 4.6, Haiku 4.5 (legacy Opus 4.5/4.1 also).
- **Caveats (likely distractors):** incompatible with citations (400); a refusal or `max_tokens` cutoff can still break the schema; a new schema has one-time compile latency, then a 24h cache.

**Exam framing:** a scenario that says "guarantee the API returns parseable JSON" → **structured outputs**, not "force a tool call." A scenario about "guarantee the *tool* receives valid args" → **strict tool use**. The old "use a tool to force the shape" is now a distractor that *works* but isn't best.

---

## 2. Context Management — named primitives (D5, 15%)

**What the course teaches:** handoff sizing + structured summaries (still correct).

**What's new — two named primitives that map directly to D5 "preserving long-context":**

- **Compaction** (beta `compact-2026-01-12`): server-side summarization of earlier history as the conversation approaches the context window. Returns a `compaction` block you **must append back** (`response.content`, not just the text) or you lose the state. *Within-session.*
- **Context editing**: prunes stale tool results / thinking blocks by a configurable threshold. **Removes**, doesn't summarize. *Within-session.*
- **Memory tool**: file-based (`/memories`) persistence **across sessions**.

**Choosing (exam trade-off):** context editing *prunes* stale turns → compaction *summarizes* near the limit → memory *persists* across sessions. A scenario "conversation is about to exceed the context window" now has a named answer (compaction), not just "summarize the handoff."

---

## 3. Agentic Architecture — expanded surface (D1, 27%)

**Still core and unchanged:** hub-and-spoke generalisation, self-attribution at source, "coordinator reasons, doesn't gather," quality-based exit over iteration cap. Sessions 2/3/7 hold up.

**New options an architect is now expected to recognize:**

- **Managed Agents:** Anthropic runs the agent loop *and* hosts a per-session container for tool execution; persisted, **versioned** Agent config → **Sessions** reference it by ID. Use when you want a server-managed stateful agent with hosted tools. Contrast: **Claude API + tool use** = you host the loop/compute. (Mandatory flow: create Agent once → Session every run; `model`/`system`/`tools` live on the Agent, never the Session.)
- **Programmatic tool calling (PTC):** Claude composes multiple tool calls into a script run in the code-execution container; intermediate results stay in the script and **don't hit the context window** — only the final output returns. Use for many sequential calls or large intermediate results.
- **Tool search:** discover tools from a large library without loading every schema upfront; schemas are **appended** (preserves prompt cache).

**Exam framing:** "many sequential tool calls, large throwaway intermediate data" → PTC. "Hundreds of tools, few relevant per request" → tool search. "Server-managed, versioned, stateful agent with hosted workspace" → Managed Agents.

---

## 4. Tool Design refinements (D2, 18%)

- **Prescriptive tool descriptions.** Newer Opus models reach for tools more conservatively; stating *when* to call ("Call this when the user asks about current prices or recent events") — not just what it does — measurably raises should-call rate. Likely scenario distractor: a generic description that "works" vs. a trigger-conditioned one that's better.
- **`tool_choice` additions** beyond your auto/any/forced: `{type: "none"}` (cannot call) and `disable_parallel_tool_use: true` (at most one tool per turn).

---

## 5. Footnote — thinking & effort (cross-cutting)

If any quiz references a "thinking budget": `budget_tokens` is deprecated/removed on current models. The current controls are **adaptive thinking** (`thinking: {type: "adaptive"}`) + the **effort** parameter (`output_config: {effort: "low|medium|high|max"}`). Unlikely to be exam-load-bearing, but don't let an old "set the thinking budget" answer look correct.
