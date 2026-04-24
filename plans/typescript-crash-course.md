# Learning Plan: TypeScript Crash Course — Streaming Apps and AI Agents

**Start date:** 2026-04-24
**Target completion:** ~2026-06-08 (~6.5 weeks)
**Schedule:** 2 sessions/week, ~1.5 hrs each
**Status:** in-progress

> Approach: diagnostic-first (assume senior dev coming from C++/Python — fast through language fundamentals, slow through JS-specific event-loop and streaming idioms), build from primitives upward, finish with a working streaming prototype that serves both a web dashboard and a TUI from the same backend.

---

## Capstones by Phase

A phase isn't closed until its capstone artefact exists under `artefacts/typescript-crash-course/phase-N/`.

| Phase | Capstone |
|---|---|
| Phase 1 (Language + tooling) | `artefacts/.../phase-1/ts-patterns-cheat-sheet.md` — one-page sheet with 10 named TypeScript patterns, each with a 3-line C++/Python analogue. Usable as exam-morning-style reference. |
| Phase 2 (Async + streaming) | `artefacts/.../phase-2/streaming-primer.md` — runnable-snippet primer covering Promises, AbortController, Node Streams, Web Streams, async iterators, WebSockets, SSE. Every snippet under 30 lines, one concept each. |
| Phase 3 (Architecture) | `artefacts/.../phase-3/streaming-architecture-design.md` — one-page architecture diagram for the streaming trading app. Annotated with latency budgets, where backpressure lives, failure domains, and the message protocol. |
| Phase 4 (AI agents) | `artefacts/.../phase-4/mock-market-agent/` — CLI agent in TS that connects to a mock market-data MCP server, uses Anthropic SDK with tool-use, and streams summary output. Must be buildable and runnable locally. |
| Phase 5 (Prototype + deploy) | `artefacts/.../phase-5/prototype/` — working backend + web + TUI, deployed to a real host, with CI passing `tsc`/`vitest`/`biome`. Repo URL recorded in the artefact's README. |

---

## Phase 1: Language + tooling (Sessions 1–3)

Fast through the language for a senior dev, but explicit on the concepts that ambush TypeScript newcomers — structural typing pitfalls, `strictNullChecks`, `satisfies`, module-system pain, error-handling philosophy.

**Phase 1 capstone:** `artefacts/typescript-crash-course/phase-1/ts-patterns-cheat-sheet.md`

**Visual:** `docs/slides/typescript-crash-course/phase-1.md` — 6–10 slides on the type system essentials, built-in toolchain, and idiomatic TypeScript.

### Session 1: Type system fundamentals + lean tooling setup
**Objective:** Internalise TypeScript's type system as distinct from C++ templates or Python type hints, and get a runnable TS project going so future sessions have somewhere to practice.
- [ ] Install Node (20+), pnpm (or npm), tsx, Vitest. Verify `tsc --version`, `tsx --version`.
- [ ] Create minimal `tsconfig.json` with `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`. Run `tsc --noEmit` as a check.
- [ ] Primitive types: `string`, `number`, `boolean`, `bigint`, `null`, `undefined`, `symbol`, `never`, `void`, `unknown`, `any`
- [ ] `strictNullChecks` — how `null` and `undefined` are NOT assignable to a typed slot unless explicitly included in the type
- [ ] Union `|` and intersection `&` types. Narrowing via `typeof`, `instanceof`, `in`, custom type guards
- [ ] Discriminated unions — the idiomatic TS substitute for C++ `enum class` or Python `Literal`. Trading example: `type MarketMessage = {type: 'tick', price: number} | {type: 'fill', qty: number}`
- [ ] Structural typing and excess property checks — why `{a: 1}` passed to `{a: number, b: number}` sometimes works and sometimes errors
- [ ] **Branded types for trading** — `type Price = number & { __brand: 'Price' }` prevents accidentally passing a size where a price was expected at the type level
- [ ] Error handling philosophy — `throw` vs explicit `Result<T, E>` types (`neverthrow` library). When each wins
- [ ] `as const` — making literal types stick instead of widening to `string`
- [ ] Install Vitest, write one assertion test, run it via `vitest`. This is the build/test loop for the rest of the course.
**Key concepts:** primitives, narrowing, discriminated unions, structural typing, strictNullChecks, branded types, as const, Result types, Vitest baseline
**Resources:** TS Handbook "Everyday Types", Matt Pocock "Total TypeScript" essentials, Vitest quick-start

### Session 2: Generics, utility types, and type-level operators
**Objective:** Understand how to express reusable type-safe patterns — the core skill for API design and library usage.
- [ ] Generic functions and types — `function identity<T>(x: T): T`, `type Box<T> = { value: T }`
- [ ] Constraints — `<T extends string>`, `<T extends Record<string, unknown>>`
- [ ] Utility types: `Partial`, `Required`, `Readonly`, `Pick<T, K>`, `Omit<T, K>`, `Record<K, V>`, `Exclude`, `Extract`, `ReturnType`, `Parameters`, `Awaited`
- [ ] Mapped types — `type Nullable<T> = { [K in keyof T]: T[K] | null }`
- [ ] Conditional types — `type NonNullable<T> = T extends null | undefined ? never : T`
- [ ] `typeof` operator — deriving a type from a runtime value
- [ ] `keyof` operator — getting the keys of a type as a union
- [ ] `satisfies` — the modern TS idiom for "type-check this value against a constraint but preserve the narrower inferred type"
- [ ] `readonly` for arrays, tuples, and object properties
- [ ] Declaration files — `.d.ts` basics, how to consume untyped npm packages
- [ ] Exercise: re-implement `Pick` and `Omit` from scratch. Extend with `Simplify<T>` for prettier intellisense
**Key concepts:** generics, utility types, mapped/conditional types, satisfies, typeof/keyof, declaration files
**Resources:** TS Handbook "Generics" + "Utility Types", Matt Pocock on `satisfies`

### Session 3: Full toolchain — build, test, lint, module system
**Objective:** Know the current-generation TS toolchain end-to-end. Understand the ESM-vs-CJS trap that ambushes every newcomer.
- [ ] `tsconfig.json` deep dive — `target`, `module`, `moduleResolution`, `lib`, `esModuleInterop`, `forceConsistentCasingInFileNames`, `isolatedModules`
- [ ] Build tools landscape:
  - **tsc** — the official compiler, slow but authoritative
  - **esbuild** — transpile-only, fast, drops type errors
  - **Vite** — dev server + esbuild for transpile + Rollup for production bundle
  - **tsup** — zero-config library bundler on top of esbuild
  - **swc** — Rust-based alternative to esbuild, used by Next.js
- [ ] When to use each: monorepo libs → tsup, apps → Vite, one-off scripts → tsx
- [ ] Module system pain:
  - ESM vs CJS — `"type": "module"` in package.json
  - Why Node requires `.js` extensions in ESM imports even when writing `.ts` (and how TS handles this with `"allowImportingTsExtensions"` or bundler mode)
  - `tsx` vs `ts-node` — `tsx` is the modern default (esbuild-based, handles both)
- [ ] Testing: Vitest — globals, `describe`/`it`/`expect`, mocking, coverage. Contrast with Jest (legacy) and node:test (stdlib)
- [ ] Linting: **Biome** (fast, Rust-based, opinionated) vs **ESLint** (extensible but slow). When each wins
- [ ] Package managers: npm (default) vs pnpm (disk-efficient, strict peer deps) vs bun (fast, all-in-one, experimental for production)
- [ ] CI skeleton — GitHub Actions workflow running `typecheck`, `test`, `lint` on push
- [ ] Notes: the toolchain you pick becomes the grammar of your project. Pick once per project, commit, move on.
**Key concepts:** tsconfig, esbuild vs tsc vs Vite vs tsup, ESM/CJS interop, tsx, Vitest, Biome, pnpm
**Resources:** TS Handbook "Project Configuration", Vitest docs, Biome docs, Matt Pocock "Don't use `ts-node`"

---

## Phase 2: Async and streaming primitives (Sessions 4–5)

Map existing Python asyncio muscle memory onto the JS event loop, then go deep on streams, backpressure, and WebSockets — the primitives every streaming trading app uses.

**Phase 2 capstone:** `artefacts/typescript-crash-course/phase-2/streaming-primer.md`

**Visual:** `docs/slides/typescript-crash-course/phase-2.md` — 6–10 slides on the event loop, Promise semantics, stream APIs, and WebSocket patterns.

### Session 4: Async fundamentals — event loop, Promises, cancellation
**Objective:** Understand the JS event loop as a specific runtime model (not "Python asyncio but different") — and use `AbortController` for proper cancellation.
- [ ] The event loop: call stack, task queue (macrotasks), microtask queue, animation frames. Node's `setImmediate` / `process.nextTick`
- [ ] Promises — `new Promise((resolve, reject) => ...)`, chain with `.then`/`.catch`/`.finally`
- [ ] Promise static methods — `Promise.all`, `Promise.allSettled`, `Promise.race`, `Promise.any`. When each fits
- [ ] `async`/`await` as syntactic sugar over Promises
- [ ] Error handling in async: `try`/`catch` around `await`, unhandled rejection warnings, the `Promise.all` short-circuit trap
- [ ] `AbortController` + `AbortSignal` — the modern cancellation primitive (supported by `fetch`, most SDKs, WebSocket wrappers)
- [ ] Timeouts: `AbortSignal.timeout(ms)`, `Promise.race([op, timeoutPromise])`
- [ ] Backpressure in Promise chains — why `Promise.all([...massive])` is an OOM in disguise and what to do instead (`p-limit`, `p-queue`)
- [ ] Exercise: write a `retry(fn, opts)` helper with exponential backoff, jitter, and AbortSignal support
**Key concepts:** event loop, microtasks vs macrotasks, Promise, async/await, AbortController, timeouts, backpressure in Promise chains
**Resources:** MDN "Concurrency model and Event Loop", Node.js docs "Event Loop", `p-limit` docs

### Session 5: Streaming primitives — Node Streams, Web Streams, WebSockets, SSE
**Objective:** Know the four standard streaming APIs and when each fits. Implement reconnection + backpressure correctly.
- [ ] Node Streams (`stream` module): `Readable`, `Writable`, `Transform`, `Duplex`. The legacy API.
- [ ] Web Streams API (`ReadableStream`, `WritableStream`, `TransformStream`) — modern, cross-platform, backpressure built in
- [ ] Async iterators — `for await (const chunk of stream)`, `Symbol.asyncIterator`. The idiomatic consumer pattern
- [ ] Backpressure mechanics:
  - **Pull-based** (Web Streams) — consumer signals readiness
  - **Push-based** (event emitters) — producer fires and hopes
  - Why push-based without backpressure loses messages under load
- [ ] WebSockets: `ws` library (Node server + client), reconnection strategies, heartbeats (`ping`/`pong`), message framing (JSON vs binary with `msgpack` or Protocol Buffers)
- [ ] SSE (Server-Sent Events): `EventSource` (browser), server-side implementation, when SSE beats WebSockets (one-way server → client, auto-reconnect, HTTP/2 friendly)
- [ ] When to use each: lots of messages per second → WebSocket binary; server → client only with medium frequency → SSE; one-shot large payloads → Web Streams over HTTP
- [ ] Exercise: implement a WebSocket client with reconnect + exponential backoff + heartbeat, wrapping it in an `AsyncIterable` consumers can `for await` over
**Key concepts:** Node Streams, Web Streams, async iterators, backpressure, WebSockets, SSE, reconnection, heartbeats, message framing
**Resources:** MDN "Streams API", Node.js "Stream", `ws` library docs, HTML Living Standard SSE section

---

## Phase 3: Streaming-app architecture (Sessions 6–7)

Ecosystem survey, then end-to-end architecture for the capstone prototype.

**Phase 3 capstone:** `artefacts/typescript-crash-course/phase-3/streaming-architecture-design.md`

**Visual:** `docs/slides/typescript-crash-course/phase-3.md` — 6–10 slides on the ecosystem and the streaming architecture.

### Session 6: Ecosystem for streaming apps
**Objective:** Know which library to reach for, for which problem. Avoid the paralysis of "twelve options for each job."
- [ ] HTTP servers — **Fastify** (fast, schema-first, plugin architecture) vs Express (legacy, slow, ubiquitous) vs Hono (edge-ready, smaller). Fastify is the Node default in 2026.
- [ ] WebSockets — `ws` (low-level, universal), `@fastify/websocket` (plugin for Fastify), `socket.io` (Engine.IO, higher-level but heavier)
- [ ] Reactive streams — **RxJS** (full reactive programming), lighter alternatives (`mostjs`, native async iterators). When RxJS is warranted: complex event-flow topologies, observables over multiple streams
- [ ] Validation — **Zod** (TS-first runtime schemas), Valibot (lighter, modular), ArkType. Zod is dominant.
- [ ] Logging — **Pino** (fast JSON logging, structured), winston (legacy). Pino for anything production.
- [ ] Decimal arithmetic — **decimal.js** (general-purpose), dinero.js (money-specific). Native `number` is not safe for prices.
- [ ] Dates — **date-fns** (functional, tree-shakable), Luxon (OO, Moment successor), native `Temporal` (staged, not yet shipped everywhere). Prefer date-fns in 2026.
- [ ] Process runners — **tsx** (the standard for running `.ts` directly), pm2 (process manager for production), forever (legacy)
- [ ] Testing HTTP — `supertest`, Fastify's inject
- [ ] Notes: build a one-page "for X problem reach for Y" decision table with your own reasoning
**Key concepts:** Fastify, ws, RxJS, Zod, Pino, decimal.js, date-fns, tsx, library selection
**Resources:** Fastify docs, Zod docs, Pino docs, Matt Pocock "Total TypeScript" on the Zod/TS workflow

### Session 7: Architecture design — streaming trading app
**Objective:** Design the full system end-to-end before writing any code. Capstone deliverable.
- [ ] Requirements: backend consumes a market feed (mock or real), fans out to N clients (web + TUI), handles backpressure, reconnects gracefully, survives a single client disconnect
- [ ] Data flow topology — single producer + pub/sub + N consumers vs broadcast every message vs per-client filtering
- [ ] Backpressure strategy — per-connection send queue with high-water mark, drop-oldest vs drop-newest under pressure, explicit slow-client handling
- [ ] Message protocol design — discriminated union of message types, versioning, binary vs JSON, whether to use Protocol Buffers or msgpack
- [ ] Shared types between server and client — monorepo with a `shared/` package, or duplicated definitions synced from a single source. Zod schemas as source of truth generating TS types AND runtime validation
- [ ] Concurrency model — single-threaded Node default, when to use `worker_threads`, when `child_process`, when to just shard across processes
- [ ] Failure domains — what happens if the upstream feed dies, if a client disconnects, if the WS server crashes? Degradation plan for each
- [ ] Observability — metrics (latency per message, queue depths, reconnect counts), logging (structured JSON via Pino), tracing (OpenTelemetry basics)
- [ ] Latency budget — "client renders update within 50ms of feed receiving it" as a target; account for: feed → WS server (5ms), WS server → client (5–20ms), client render (10–20ms)
- [ ] Exercise: write the architecture design doc. One-page diagram. Model on `docs/slides/trading-landscape/phase-1/ecosystem-map.md` format.
**Key concepts:** pub/sub, backpressure strategy, message protocol, shared types, Zod as source of truth, worker threads, failure domains, latency budgets
**Resources:** Martin Kleppmann "Designing Data-Intensive Applications" streams chapter, Node.js worker_threads docs

---

## Phase 4: TypeScript for AI agents (Sessions 8–9)

Why TS is the default language for building AI agents, and the two SDKs that matter: Anthropic SDK + Vercel AI SDK (S8), and MCP SDK (S9).

**Phase 4 capstone:** `artefacts/typescript-crash-course/phase-4/mock-market-agent/`

**Visual:** `docs/slides/typescript-crash-course/phase-4.md` — 6–10 slides on why TS wins for agents, the SDK landscape, and the MCP protocol.

### Session 8: Anthropic SDK, Vercel AI SDK, and the "why TS for agents" answer
**Objective:** Understand why TS dominates agent development and build a simple tool-use agent end-to-end.
- [ ] The crisp answer to "why TS for AI agents":
  - Zod schemas → JSON Schema → tool definitions that can't be misspelled
  - AsyncIterables map naturally to streaming token deltas
  - SDK typings mean tool_use responses are type-safe all the way through
  - Shared types between the agent, the tool implementations, and any MCP servers
- [ ] `@anthropic-ai/sdk` — installing, creating a client, the `messages.create` call
- [ ] Streaming token deltas — `stream: true` + the `content_block_delta` events
- [ ] Tool use — declaring tools with JSON Schema, handling `tool_use` content blocks, returning `tool_result`
- [ ] Zod for tool schemas — `zodToJsonSchema()` to derive the SDK-ready schema, type-safe tool arguments
- [ ] The agent loop pattern — `while (lastMessage.stop_reason === 'tool_use') { … }`
- [ ] Prompt caching — `cache_control: { type: 'ephemeral' }` on system prompts, why it matters for iterative agents
- [ ] Vercel AI SDK (`ai` package) — the abstraction over multiple providers. `generateText`, `streamText`, `generateObject` (typed output via Zod), agent loops
- [ ] When to use Vercel AI SDK vs `@anthropic-ai/sdk` directly: SDK for provider-agnostic, Anthropic SDK for Anthropic-specific features (prompt caching, computer use, MCP tool-use server-side)
- [ ] Exercise: write a 100-line CLI agent using Anthropic SDK that accepts a question, calls a mock "weather" tool with Zod-validated args, and streams the answer
**Key concepts:** Anthropic SDK, Vercel AI SDK, Zod → JSON Schema, tool_use, agent loop, streaming deltas, prompt caching
**Resources:** `@anthropic-ai/sdk` docs, Vercel AI SDK docs, Zod docs on `zodToJsonSchema`

### Session 9: MCP SDK — building and consuming an MCP server
**Objective:** Understand MCP (Model Context Protocol) server+client structure and build one end-to-end.
- [ ] MCP protocol overview — transports (stdio, SSE, streamable HTTP), the three primitive types (tools, resources, prompts)
- [ ] `@modelcontextprotocol/sdk` for TypeScript — server and client APIs
- [ ] Building an MCP server: declare tools with Zod schemas, handle requests, respond with results
- [ ] Running an MCP server: stdio for local (Claude Code, Claude Desktop), HTTP for networked
- [ ] Consuming an MCP server from an agent: Anthropic SDK's `mcp_servers` parameter (server-side tool-use), or Vercel AI SDK's MCP client tools (client-side tool-use)
- [ ] Resource types — read-only data exposed by the server (file contents, database rows, remote state)
- [ ] Prompt types — parameterised prompt templates the server provides to clients
- [ ] Debugging MCP — the `@modelcontextprotocol/inspector` tool, logging in stdio context (stderr only!), common pitfalls
- [ ] Exercise: build `mock-market-agent` — MCP server exposing a `lookup_price` tool that returns deterministic mock prices; CLI agent consumes it via Anthropic SDK and summarises. This is the Phase 4 capstone.
**Key concepts:** MCP transports, tools/resources/prompts, `@modelcontextprotocol/sdk`, stdio vs HTTP, agent-side MCP consumption, inspector
**Resources:** MCP spec (`modelcontextprotocol.io`), `@modelcontextprotocol/sdk` docs, Anthropic's MCP guide

---

## Phase 5: Build the prototype + deploy (Sessions 10–13)

Design is complete; now build it, ship it, and deploy it.

**Phase 5 capstone (whole course):** `artefacts/typescript-crash-course/phase-5/prototype/` — working backend + web + TUI, deployed.

**Visual:** `docs/slides/typescript-crash-course/phase-5.md` — 6–10 slides on the build steps, React primer, Ink, and deployment patterns.

### Session 10: Streaming backend
**Objective:** Build the WebSocket server + mock feed + message protocol + shared types.
- [ ] Scaffold a pnpm monorepo: `packages/backend`, `packages/web`, `packages/tui`, `packages/shared`
- [ ] Shared types package — Zod schemas for every message type in the protocol. Export TS types via `z.infer<...>`.
- [ ] Mock feed — a small module that emits synthetic market data at a configurable rate (updates/sec, symbols, tick size)
- [ ] WebSocket server using `ws` — accept connections, maintain a per-connection send queue, broadcast mock-feed messages
- [ ] Backpressure — enforce the design from Phase 3: per-connection high-water mark, drop-oldest on overflow, log slow clients
- [ ] Structured logging with Pino — one line per connection event, one line per N messages (not per message — that's a log flood)
- [ ] Tests — Vitest unit tests for the mock feed, integration test that connects two clients and verifies both receive the same sequence
- [ ] Run the backend locally; verify two `wscat` clients both see the feed
**Key concepts:** pnpm monorepo, shared types via Zod, `ws` server, per-connection send queue, Pino, integration testing WebSocket
**Resources:** pnpm docs on workspaces, `ws` library docs, Pino docs

### Session 11: React primer + web dashboard
**Objective:** Learn just enough React to build the dashboard, then build it.
- [ ] **React primer (first half):**
  - JSX syntax — HTML-in-JS, `className` not `class`, `{expr}` interpolation
  - Components — function components, props, children
  - Hooks — `useState`, `useEffect`, `useRef`, `useMemo`, `useCallback`
  - Rules of hooks — top-level only, same order every render
  - `useEffect` pitfalls — infinite loops, missing dependencies, cleanup functions
  - Reconciliation mental model — React diffs the virtual DOM against the previous render
  - State management escape hatch — Zustand (simple, TS-friendly) vs Signals (via `@preact/signals-react`, more reactive) vs vanilla `useState` (fine for this prototype)
- [ ] **Web dashboard build (second half):**
  - `npm create vite@latest` with the `react-ts` template
  - Component structure — `App`, `LiveFeed`, `SymbolRow`
  - WebSocket client hook — `useWebSocket(url)` that returns `{status, messages}`, uses `useEffect` for connection lifecycle, `useRef` for the WS instance
  - Render live prices — one row per symbol, flash green/red on tick direction
  - Handle disconnects — status indicator in the header, reconnect on network recovery
- [ ] Tests — React Testing Library + Vitest, test the `useWebSocket` hook with a mock WS
- [ ] Run locally; verify the dashboard connects to the backend and renders updates
**Key concepts:** JSX, components, hooks, useEffect, Vite + React TS template, WS client hook, connection state
**Resources:** React beta docs (the "new" docs), Vite getting-started, `@testing-library/react`

### Session 12: TUI with Ink
**Objective:** Build the same feed in a terminal UI using Ink (React for terminals).
- [ ] Ink primer — same React model, different renderer. Components render to Yoga (flexbox) and the terminal
- [ ] `<Box>`, `<Text>`, `<Newline>`, `<Static>` — the primitives
- [ ] Input handling — `useInput()` for keystrokes, `useApp()` for lifecycle
- [ ] Building the TUI:
  - Same WS client hook (share it from `packages/shared` or `packages/tui`)
  - Render a table of symbols + live prices using `<Box flexDirection="row">`
  - Keybinding: `q` to quit, `r` to reset, arrow keys to navigate rows
  - Use `useState` to track selected symbol; show detail pane below
- [ ] Ink-specific quirks — terminal colour via `<Text color="green">`, no absolute positioning, no overlap. Flexbox only.
- [ ] Debugging Ink — console.log can't be used (breaks rendering); use `@inkjs/ui` log component or write to a file
- [ ] Tests — Ink Testing Library, simulate input, assert on rendered frame output
- [ ] Run locally; verify the TUI connects and renders alongside the web dashboard from the same backend
**Key concepts:** Ink, <Box>/<Text>, useInput, flexbox in terminal, Ink Testing Library, shared WS client across UIs
**Resources:** Ink docs, `@inkjs/ui`, Ink Testing Library

### Session 13: Packaging and deploy — the production lap
**Objective:** Take the prototype from "runs on my laptop" to "runs on the internet with CI."
- [ ] Build strategy — per-package build scripts. Backend: `tsc --build` or `tsup` for a single JS bundle. Web: `vite build`. TUI: `tsup` producing a CLI binary with a shebang.
- [ ] Monorepo build orchestration — `turbo` (Vercel) or just pnpm scripts. Turbo for cached parallel builds.
- [ ] `package.json` fields that matter for shipping: `main`, `module`, `exports`, `bin`, `files`, `engines`
- [ ] Dockerising the backend:
  - Multi-stage build: `node:20-alpine` builder + distroless runtime
  - `pnpm fetch && pnpm install --offline` for reproducible installs
  - `HEALTHCHECK` for WS server liveness
- [ ] GitHub Actions CI: jobs for `typecheck`, `test`, `lint`, `build`, optional `docker-build-and-push`
- [ ] Hosting the backend — Fly.io (good for persistent WS connections, cheap, predictable pricing), Railway (similar, simpler UI), Render (also fine). **Not** Vercel / serverless — they kill persistent connections and charge per invocation. Cloudflare Durable Objects is an alternative if you want edge WS.
- [ ] Hosting the web dashboard — static host (Vercel, Netlify, Cloudflare Pages). Point WS URL at the backend host.
- [ ] Distributing the TUI — `npm publish` with a `bin` entry so users run `npx your-tui`. Or standalone binary via `bun build --compile` or `pkg`
- [ ] Environment config — `dotenv` for dev, platform env vars for prod, validate with Zod on startup
- [ ] Deploy the prototype; record the URL in the capstone's README. Confirm CI is green.
**Key concepts:** tsup, Turbo, multi-stage Docker, distroless, GitHub Actions CI, Fly.io, static hosting, npm publish with bin, env validation
**Resources:** Turbo docs, Fly.io Node docs, Docker best practices for Node, `tsup` docs

---

## Closing the loop

The course is deliberately cross-linked with your other active work:

- **Phase 4** (AI agents) is the TypeScript-side complement to `claude-certified-architect` — the exam covers agent architecture and MCP at the concept level; this phase builds one.
- **Phase 5** (prototype + deploy) is the skills base for any side project that needs a live web or TUI on top of a streaming backend — applicable to the stock-picker project you've been building in Python, where the TS front-end could be a natural extension.
- **Trading context throughout** — every exercise uses trading-adjacent examples (prices, ticks, orders, book depth) so the skills stick in the domain you actually care about.

The whole-course capstone — a deployed prototype — is both the TypeScript proof and a reusable starting template for any future streaming-app project.
