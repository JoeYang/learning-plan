# Learning Plan: TypeScript Crash Course — FDE Prototyping Stack

**Start date:** ~2026-08-17 (Wave 2 of the FDE path; reshaped 2026-07-18, originally created 2026-04-24)
**Target completion:** ~2026-09-11 (~2 weeks at path cadence)
**Schedule:** 4 sessions/week, ~1.5 hrs each (FDE-path cadence)
**Status:** not-started

> Approach: senior dev coming from C++/Python — fast through language fundamentals, deliberate on the JS-specific event-loop and React idioms, then straight to shipping. The bar is "functional demo UI that streams LLM output, deployed to a public URL" — not front-end craft. Everything trimmed from the original 13-session plan (Ink TUI, deep streams, ecosystem survey, MCP-in-TS) either moved to fde-production-ai-systems or was cut on independent-review advice.

---

## Capstones by Phase

A phase isn't closed until its capstone artefact exists under `artefacts/typescript-crash-course/phase-N/`.

| Phase | Capstone |
|---|---|
| Phase 1 (Language + tooling) | `artefacts/.../phase-1/ts-patterns-cheat-sheet.md` — one-page sheet with 10 named TypeScript patterns, each with a 3-line C++/Python analogue. |
| Phase 2 (React + streaming LLM UI) | `artefacts/.../phase-2/streaming-chat/` — local React app that streams Claude responses token-by-token with typed messages, abortable requests, and connection-state UI. |
| Phase 3 (Ship the demo) | `artefacts/.../phase-3/demo/` — deployed finance AI demo (earnings-call Q&A), live URL in README, CI green on `tsc`/`vitest`/`biome`. **FDE portfolio piece #2.** |

---

## Phase 1: Language + tooling (Sessions 1–3)

Fast through the language for a senior dev, but explicit on the concepts that ambush TypeScript newcomers — structural typing pitfalls, `strictNullChecks`, `satisfies`, module-system pain.

**Phase 1 capstone:** `artefacts/typescript-crash-course/phase-1/ts-patterns-cheat-sheet.md`

**Visual:** `docs/slides/typescript-crash-course/phase-1.md` — 6–10 slides on the type system essentials and toolchain.

### Session 1: Type system fundamentals + lean tooling setup
**Objective:** Internalise TypeScript's type system as distinct from C++ templates or Python type hints, and get a runnable TS project going.
- [ ] Install Node (20+), pnpm, tsx, Vitest. Verify `tsc --version`, `tsx --version`
- [ ] Minimal `tsconfig.json` with `strict: true`, `noUncheckedIndexedAccess: true`. Run `tsc --noEmit` as the check loop
- [ ] Primitives incl. `never`, `void`, `unknown`, `any` — and why `unknown` beats `any`
- [ ] `strictNullChecks` — `null`/`undefined` are not assignable unless declared
- [ ] Union `|` and intersection `&`; narrowing via `typeof`, `instanceof`, `in`, custom type guards
- [ ] Discriminated unions — the idiomatic TS substitute for `enum class`/`Literal`. Example: `type ApiEvent = {type:'delta', text:string} | {type:'done', usage:Usage}`
- [ ] Structural typing and excess property checks — why `{a:1}` sometimes passes and sometimes errors
- [ ] Error handling philosophy — `throw` vs explicit `Result<T,E>`; when each wins
- [ ] `as const` — making literal types stick
- [ ] Write one Vitest assertion test and run it — the build/test loop for the rest of the course
**Key concepts:** primitives, narrowing, discriminated unions, structural typing, strictNullChecks, as const, Vitest baseline
**Resources:** TS Handbook "Everyday Types", Matt Pocock "Total TypeScript" essentials, Vitest quick-start

### Session 2: Generics, utility types, and type-level operators
**Objective:** Express reusable type-safe patterns — the core skill for using SDKs and typing API payloads.
- [ ] Generic functions and types; constraints (`<T extends Record<string, unknown>>`)
- [ ] Utility types: `Partial`, `Pick`, `Omit`, `Record`, `ReturnType`, `Awaited`
- [ ] Mapped types and conditional types — read them fluently, write simple ones
- [ ] `typeof` and `keyof` — deriving types from runtime values
- [ ] `satisfies` — type-check a value against a constraint while preserving inference
- [ ] `readonly` arrays, tuples, and properties
- [ ] Declaration files — consuming untyped npm packages
- [ ] Zod — runtime schemas as source of truth, `z.infer<>` for the static type; validate an LLM API response shape
- [ ] Exercise: type an Anthropic messages-API request/response pair by hand, then replace with SDK types and diff your understanding
**Key concepts:** generics, utility types, satisfies, typeof/keyof, Zod + z.infer
**Resources:** TS Handbook "Generics" + "Utility Types", Matt Pocock on `satisfies`, Zod docs

### Session 3: Toolchain + async fundamentals
**Objective:** Know the current TS toolchain end-to-end and map asyncio muscle memory onto the JS event loop.
- [ ] `tsconfig.json` essentials: `target`, `module`, `moduleResolution`, `isolatedModules`
- [ ] Build tools in one pass: tsc (authoritative), Vite (apps), tsx (scripts) — pick per job, move on
- [ ] ESM vs CJS — `"type": "module"`, the `.js`-extension-in-imports trap
- [ ] The event loop: call stack, macrotasks, microtasks — contrast with asyncio's model
- [ ] Promises, `async`/`await`, `Promise.all`/`allSettled`/`race`, the `Promise.all` short-circuit trap
- [ ] `AbortController` + `AbortSignal` — the cancellation primitive every streaming UI needs; `AbortSignal.timeout(ms)`
- [ ] Unhandled rejections and error handling around `await`
- [ ] Linting/formatting with Biome; CI skeleton (GitHub Actions: typecheck, test, lint)
- [ ] Exercise: `retry(fn, opts)` helper with exponential backoff, jitter, and AbortSignal support
- [ ] Write the phase capstone cheat sheet
**Key concepts:** tsconfig, Vite, tsx, ESM/CJS, event loop, Promise semantics, AbortController, Biome, CI skeleton
**Resources:** TS Handbook "Project Configuration", MDN "Event Loop", Matt Pocock "Don't use ts-node", Biome docs

---

## Phase 2: React + streaming LLM UI (Sessions 4–6)

Just enough React to build a functional demo UI, then the one UI pattern FDE demos live on: streaming LLM output with sane connection state.

**Phase 2 capstone:** `artefacts/typescript-crash-course/phase-2/streaming-chat/`

**Visual:** `docs/slides/typescript-crash-course/phase-2.md` — 6–10 slides on React mental model + streaming patterns.

### Session 4: React essentials
**Objective:** Learn the React mental model well enough to build and debug a small app — and stop there.
- [ ] JSX — `className`, `{expr}` interpolation, fragments
- [ ] Function components, props, children; component composition
- [ ] Hooks: `useState`, `useEffect`, `useRef`; rules of hooks
- [ ] `useEffect` pitfalls — infinite loops, missing deps, cleanup functions
- [ ] Reconciliation mental model — React diffs against the previous render; keys on lists
- [ ] Controlled inputs — the form pattern for a chat box
- [ ] Scaffold with `npm create vite@latest` (react-ts template); dev-server loop
- [ ] State management: vanilla `useState` is fine for a demo — know Zustand exists, don't use it yet
- [ ] Exercise: build a static chat UI (message list + input + send) with typed `Message[]` state
**Key concepts:** JSX, components, hooks, useEffect cleanup, keys, controlled inputs, Vite react-ts
**Resources:** react.dev "Learn React" (Describing the UI + Adding Interactivity), Vite getting-started

### Session 5: Streaming LLM output — SSE, fetch streams, token deltas
**Objective:** Render tokens as they arrive, cancel cleanly, and survive disconnects — the demo-critical pattern.
- [ ] How LLM APIs stream: SSE frames, `content_block_delta` events in the Anthropic API
- [ ] `fetch` + `ReadableStream` — reading a streaming response with `getReader()` and async iteration
- [ ] `@anthropic-ai/sdk` streaming — `client.messages.stream()`, event handlers vs async iteration
- [ ] Vercel AI SDK (`ai` package): `streamText` on the server, `useChat` on the client — what it abstracts and when to drop below it
- [ ] Backend proxy route — why the API key lives server-side, never in the browser (a demo that leaks a key is a failed security review)
- [ ] Rendering deltas — append to state per chunk; avoid re-render-per-token jank (batching, `flushSync` caveats)
- [ ] Abort on unmount / stop button — wire `AbortController` through the fetch and the SDK stream
- [ ] Connection-state UI — idle / streaming / error / done; retry affordance
- [ ] Exercise: build the streaming chat against the Anthropic API via a minimal Node proxy; type every message shape with Zod
**Key concepts:** SSE, ReadableStream, messages.stream, streamText/useChat, server-side key proxy, abortable streams, delta rendering
**Resources:** Anthropic TS SDK streaming docs, Vercel AI SDK docs, MDN "Using readable streams"

### Session 6: Hardening the demo UI + auth basics
**Objective:** Make the streaming app demo-grade: it recovers, it validates, and it has just enough auth.
- [ ] Error boundaries and fallback UI — a demo that white-screens in front of a customer is a lost deal
- [ ] Zod-validate every inbound payload at the proxy boundary; never trust the wire
- [ ] Loading/empty/error states for every async surface
- [ ] Reconnect/retry on stream failure with backoff (reuse Session 3's `retry`)
- [ ] Auth basics for demos: a shared-secret gate or magic-link stub — enough to say "it's not open to the internet", full SSO comes in fde-aws-deployment
- [ ] Environment config — `.env` for dev, Zod-validated env parsing on startup, no hardcoded secrets
- [ ] Tests: Vitest + React Testing Library on the chat hook with a mocked stream
- [ ] Assemble the phase capstone: `streaming-chat/` runs locally end-to-end
**Key concepts:** error boundaries, boundary validation, retry/backoff, demo auth gate, env validation, hook testing
**Resources:** react.dev error boundaries, `@testing-library/react`, Zod env-parsing pattern

---

## Phase 3: Ship the finance demo (Sessions 7–8)

Build the actual portfolio piece and put it on the internet.

**Phase 3 capstone:** `artefacts/typescript-crash-course/phase-3/demo/` — **FDE portfolio piece #2**

**Visual:** `docs/slides/typescript-crash-course/phase-3.md` — 6–10 slides on the demo architecture and deploy path.

### Session 7: Build the earnings-call Q&A demo
**Objective:** Assemble the full demo: public earnings-call transcripts in, streamed grounded answers out.
- [ ] Pick 3–5 public earnings-call transcripts (e.g. SEC/IR pages) as the corpus; script the fetch + clean
- [ ] Minimal retrieval: chunk transcripts, embed, top-k similarity via a simple in-process store — deliberately naive; fde-production-ai-systems does it properly
- [ ] Backend route: question → retrieve context → Claude with context-stuffed prompt → stream answer
- [ ] Citations UI — show which transcript/chunk grounded the answer (hallucination defence is a demo talking point)
- [ ] Reuse the Phase 2 streaming chat as the front-end; add a corpus picker
- [ ] Latency framing — measure and display time-to-first-token; know the number before a customer asks
- [ ] Type the whole pipeline end-to-end: one Zod schema module shared by server and client
- [ ] Demo script dry-run — 3-minute walkthrough: problem, question, streamed grounded answer, citation (feeds fde-consulting-craft demo drills)
**Key concepts:** transcript corpus, naive RAG, context-stuffed prompting, citations, time-to-first-token, shared schema module
**Resources:** Anthropic docs on RAG prompting, SEC EDGAR / company IR pages, Phase 2 artefact

### Session 8: Deploy + CI — the production lap
**Objective:** From "runs on my laptop" to a public URL with CI, in one session.
- [ ] Build strategy: `vite build` for the front-end, `tsup`/`tsc` for the server
- [ ] `package.json` fields that matter: `exports`, `engines`, scripts discipline
- [ ] Host the backend on Fly.io or Railway (persistent process, predictable pricing); front-end static on the same host or Cloudflare Pages
- [ ] Environment config on the platform — API key as platform secret, Zod-validated at boot
- [ ] GitHub Actions CI: typecheck, test, lint, build on push; deploy on main
- [ ] Smoke test the deployed URL; check streaming works through the host's proxy (buffering gotchas)
- [ ] Record the URL + a 60-second Loom-style walkthrough in the artefact README
- [ ] Course retro note in the artefact: what to re-learn before the AWS redeploy in fde-aws-deployment
**Key concepts:** vite build, tsup, Fly.io/Railway, platform secrets, GitHub Actions deploy, streaming-through-proxy gotchas
**Resources:** Fly.io Node docs, tsup docs, GitHub Actions docs

---

## Closing the loop

- **Feeds fde-production-ai-systems (Track 3):** the naive retrieval in Session 7 is intentionally the "before" picture; Track 3 Phase 1 rebuilds it properly, and the demo becomes the surface its RAG/agent system lands behind.
- **Feeds fde-aws-deployment (Track 4):** this demo is the workload that gets redeployed into the enterprise AWS pattern (VPC, Bedrock, SSO) as the flagship capstone.
- **Feeds fde-consulting-craft (Track 5):** Session 7's demo script dry-run is raw material for the demo-craft drills.
- **Cut from the original plan** (in git history if wanted later): Ink TUI, deep Node/Web streams and backpressure, ecosystem survey, MCP-in-TS build sessions, dual web+TUI capstone.
