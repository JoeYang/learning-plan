# Topic: TypeScript Crash Course — FDE Prototyping Stack

> **Reshaped 2026-07-18** as Track 2 of the FDE learning path (was: "Streaming Apps and AI Agents", 13 sessions, never started). Trimmed to 8 sessions after independent review: FDE hiring tests demo-shipping speed, not front-end craft. Cut: Ink TUI, deep Node/Web streams, ecosystem survey, MCP-in-TS build sessions (concepts covered in claude-certified-architect; rebuilt hands-on in fde-production-ai-systems Phase 3). The original 13-session plan is preserved in git history if the streaming/TUI ambitions return.

## Why I Want to Learn This
TS/React is the de-facto FDE demo stack — a credible customer-facing prototype in days, not weeks. I'm experienced in Python and low-latency C++ but have never written TypeScript as a primary language, and "Python-only" reads as notebook engineer in FDE loops. This course exists to make me fast at the thing FDEs do constantly: stand up a working, streaming AI demo UI in front of a customer.

## Current Knowledge Level
None on TypeScript itself. Comfortable with JavaScript at a copy-paste level, no React. Deep experience with static type systems from C++ (templates, concepts) and Python (mypy). Event-loop/async concepts from Python asyncio; need to map those to the JS event loop.

## Goal
Be able to:
1. Read and write idiomatic TypeScript at a level a senior open-source contributor would accept in PR review
2. Build a functional React UI that streams LLM output token-by-token — without reaching for a tutorial
3. Ship: build, CI, and deploy a full-stack TS app to a public URL in a single session
4. Stop there — front-end depth beyond a working demo UI is deliberately out of scope

## Capstone: what artefact proves mastery?
Whole-course capstone: `artefacts/typescript-crash-course/phase-3/demo/` — a **deployed, public finance AI demo** (earnings-call Q&A over public transcripts, streaming answers), live URL recorded in the artefact README, CI green on `tsc`/`vitest`/`biome`. This is FDE portfolio piece #2 — the one opened in interviews. Per-phase capstones listed in the plan.

## Resources
- **TypeScript handbook** (official) — canonical reference
- **Matt Pocock "Total TypeScript"** — modern TS idioms
- **React docs** (react.dev) — the new docs, function components + hooks
- **Vite** getting-started; **Vitest**, **Biome** docs
- **Anthropic TypeScript SDK docs** — streaming `content_block_delta` handling
- **Vercel AI SDK docs** (`ai` package) — `streamText`, `useChat`
- MDN — fetch streams, Server-Sent Events

## Time Estimate
8 sessions, ~1.5 hrs each, at 4 sessions/week (FDE-path cadence) ≈ 2 weeks. Scheduled ~2026-08-17 → ~2026-09-11 (Wave 2 of the FDE path).

## Priority
high — gating prerequisite for fde-production-ai-systems (the demo this course ships is the surface that course's RAG/agent system lands behind)
