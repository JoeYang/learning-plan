# Topic: TypeScript Crash Course — Streaming Apps and AI Agents

## Why I Want to Learn This
First TS-native project. I'm experienced in Python and low-latency C++ trading infrastructure but have never written TypeScript as my primary language. I want a fast but thorough crash course that covers the language, its toolchain, and the two things I actually want to build with it:
1. **A streaming-based app for trading** — either web dashboard or TUI (or both) that consumes a live feed via WebSockets and renders in real time.
2. **AI agents** — TypeScript has become the default language for the Claude/OpenAI agent ecosystem (Anthropic SDK, Vercel AI SDK, MCP SDK). Understanding the TS-agent stack is adjacent to my Claude Certified Architect work.

## Current Knowledge Level
None on TypeScript itself. Comfortable with JavaScript at a copy-paste level, no React. Deep experience with static type systems from C++ (templates, concepts, strict typing) and Python (gradual typing with mypy). Event-loop / async concepts from Python asyncio; need to map those to the JS event loop.

## Goal
Be able to:
1. Read and write idiomatic TypeScript at the level a senior open-source contributor would accept in PR review
2. Build, test, and deploy a TypeScript application end-to-end using current (2026) toolchain
3. Design and implement a streaming trading app with a shared backend feeding both a web dashboard (React) and a TUI (Ink)
4. Reach for the right ecosystem library for a given problem without having to re-research each time
5. Build and consume AI agents using Anthropic SDK + MCP SDK, understanding why TypeScript is the default language for this domain

## Capstone: what artefact proves mastery?
Whole-course capstone: `artefacts/typescript-crash-course/phase-5/prototype/` — working prototype where one streaming backend (WebSocket server) feeds both a React web dashboard and an Ink TUI, deployed to a real host (Fly, Railway, or equivalent), with CI passing on `tsc`, `vitest`, and `biome`. Plus one AI-agent artefact in Phase 4 — a CLI agent that queries a mock market-data MCP server and streams summaries.

One capstone per phase, listed in the plan's "Capstones by Phase" table.

## Resources
- **TypeScript handbook** (official, 2024 edition) — the canonical reference
- **Matt Pocock "Total TypeScript"** blog posts and free tutorials — modern TS idioms
- **Josh Goldberg "Learning TypeScript"** (O'Reilly) — systematic coverage
- **Anthony Fu's blog** — tooling and modern TS patterns (Vite, Vue/React ecosystem)
- **Node.js docs** — event loop, streams, worker threads
- **MDN Web Docs** — Web Streams API, WebSockets, EventSource
- **Anthropic TypeScript SDK docs** + MCP spec (`modelcontextprotocol.io`)
- **Vercel AI SDK docs** (`ai` package)
- **Ink documentation** (`github.com/vadimdemedes/ink`) — React for terminals
- **WebSocket book/docs**: `ws` library, Fastify WebSocket plugin

## Time Estimate
~13 sessions, ~1.5 hrs each, at 2 sessions/week ≈ 6.5 weeks

## Priority
medium — complementary to claude-certified-architect work, useful for future AI-agent side projects and streaming trading tooling
