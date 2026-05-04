# TypeScript Phase 1 — Language and tooling

Sessions 1–3: the type system, the idioms that trip up senior devs, and the toolchain you'll live in.

> **The theme:** TypeScript is not C++ templates, not Python type hints, not Java generics. It's a *structural* type system layered over a dynamic language, with an elaborate ecosystem of tools that you have to configure once and never think about again. Phase 1 is the fast path to productive.

---

## The problem Phase 1 solves

You already know static types from C++ and gradual types from Python + mypy. But TypeScript has its own idioms that ambush newcomers — and because you're already fluent in *some* typed language, you'll reach for the wrong mental model.

Specifically:

- **Structural typing**, not nominal. Types match by shape, not name.
- **Every variable can be `null` or `undefined`** unless you opt out. `strictNullChecks` is on; treat it like `--Wall -Werror`.
- **Discriminated unions** replace C++ `enum class` and Python `Literal`/`Union` for "one of several variants" modelling.
- **Branded types** are the workaround for structural typing's biggest weakness — mixing up a `Price` and a `Size` at the call site.
- **The toolchain is fragmented** (tsc, esbuild, Vite, tsup, Biome, Vitest, pnpm) and picking wrong costs you days.

Phase 1 closes those five gaps.

---

## Structural typing — the conceptual shift

C++ and Python care about *declared type identity*. TypeScript cares about *shape*.

```ts
type Point = { x: number; y: number };

function distance(p: Point): number {
  return Math.hypot(p.x, p.y);
}

// Not declared as Point — but has the right shape.
const anonymous = { x: 3, y: 4, label: "origin" };

distance(anonymous);  // ✓ compiles and runs
```

What this gains:
- No `implements` ceremony to be "compatible"
- Refactoring-friendly — rename a type, all structurally-compatible callers still work

What this costs:
- A `UserID` (string) and a `SessionToken` (string) are the **same type** to the compiler. You CAN pass one where the other is expected — disaster for trading code where a `Price` and a `Size` are both `number`.
- **Branded types** fix this. Slide 5.

---

## Discriminated unions — the idiomatic "enum class"

Modelling "this value is one of several variants, each with its own payload" in TypeScript:

```ts
type MarketMessage =
  | { type: "tick";  symbol: string; price: number; size: number }
  | { type: "trade"; symbol: string; price: number; qty: number; side: "buy" | "sell" }
  | { type: "halt";  symbol: string; reason: string };

function handle(m: MarketMessage) {
  switch (m.type) {
    case "tick":  return m.price;        // narrowed to tick
    case "trade": return m.qty;          // narrowed to trade
    case "halt":  return m.reason;       // narrowed to halt
  }
}
```

Key properties:
- The **discriminant** (`type` field here) is a literal-string union — `"tick" | "trade" | "halt"`
- Narrowing via `switch` or `if (m.type === "tick")` refines `m` to the matching variant
- Add a new variant and forget to handle it → TS flags the `switch` as non-exhaustive (with `noImplicitReturns`)

This is the TS analogue of a Rust `enum`, a C++ `std::variant` + `std::visit`, or a Python sealed `Union`. Reach for it every time you have "one of N shapes."

---

## Branded types — when structural typing bites

Structural typing's weakness: every `number` is interchangeable with every other `number`. For trading, that's a footgun.

```ts
// Naked numbers — the compiler can't stop you.
function placeOrder(symbol: string, price: number, size: number) { }
placeOrder("AAPL", 100, 0.01);          // normal
placeOrder("AAPL", 0.01, 100);          // BUG — price and size swapped, compiler shrugs
```

**The branded type pattern:**

```ts
type Price = number & { readonly __brand: "Price" };
type Size  = number & { readonly __brand: "Size"  };

// Constructors that do the "branding" — only place that casts.
const asPrice = (n: number) => n as Price;
const asSize  = (n: number) => n as Size;

function placeOrder(symbol: string, price: Price, size: Size) { }

placeOrder("AAPL", asPrice(100), asSize(0.01));   // ✓
placeOrder("AAPL", asSize(100), asPrice(0.01));   // ✗ type error — caught at compile time
```

The intersection `number & { __brand }` is a purely compile-time fiction — at runtime it's still a number. No wrapping, no overhead. Use for every domain-specific number (`Price`, `Size`, `QuoteId`, `Timestamp`) you care about keeping straight.

---

## Strict mode is not one flag — it's a spectrum

`"strict": true` turns on a family of checks. Individually known as:

| Flag | What it catches |
|---|---|
| `strictNullChecks` | `null` and `undefined` are not assignable to non-nullable slots |
| `strictFunctionTypes` | Stricter variance on function parameters |
| `strictBindCallApply` | Type-checks `.bind()`, `.call()`, `.apply()` |
| `strictPropertyInitialization` | Class fields must be initialised or marked optional |
| `noImplicitAny` | Implicit `any` is an error (always turn on) |
| `noImplicitThis` | `this` in a function needs a known type |
| `alwaysStrict` | Emits `"use strict"` and parses in strict mode |

And beyond `strict`, two non-strict checks every serious codebase turns on:

| Flag | What it catches |
|---|---|
| `noUncheckedIndexedAccess` | `arr[i]` returns `T \| undefined` — catches off-by-one |
| `exactOptionalPropertyTypes` | `{x?: number}` means "may omit," not "may be `undefined`" |

Default tsconfig for any new project:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "isolatedModules": true
  }
}
```

Turn these on once. Any codebase without them has latent bugs.

---

## Generics, utility types, and `satisfies`

Generics in TS are closer to Java than C++ — bounded, not duck-typed at compile time.

```ts
function first<T>(xs: T[]): T | undefined {
  return xs[0];
}

// Constrained generic — T must have an `id` field.
function byId<T extends { id: string }>(xs: T[], id: string): T | undefined {
  return xs.find(x => x.id === id);
}
```

The utility type library does most of the heavy lifting:

| Utility | Does |
|---|---|
| `Partial<T>` | All fields optional |
| `Required<T>` | All fields required (inverse of `Partial`) |
| `Pick<T, K>` | Keep only fields in `K` |
| `Omit<T, K>` | Drop fields in `K` |
| `Record<K, V>` | Object with keys `K` mapping to values `V` |
| `ReturnType<F>` | Return type of function `F` |
| `Parameters<F>` | Parameter tuple of function `F` |
| `Awaited<P>` | Resolve a Promise type chain |
| `Readonly<T>` | All fields readonly |

And the modern idiom that every new-to-TS senior misses — **`satisfies`**:

```ts
// Problem: I want `config` to conform to a shape, but keep narrower literal types.
const config = {
  host: "localhost",
  port: 8080,
  protocol: "ws",
} satisfies { host: string; port: number; protocol: "ws" | "wss" };

config.protocol;  // inferred as "ws", NOT "ws" | "wss"
```

Use `satisfies` when you want *validation* without *widening*. It landed in TS 4.9 and is now load-bearing in modern idiom.

---

## The ESM / CJS module pain — the biggest toolchain trap

Node has two module systems. They don't interoperate cleanly. TS sits in the middle.

**CommonJS (CJS)** — Node's original. `require()` and `module.exports`. Still the default in legacy tooling.

**ESM (ECMAScript Modules)** — the standard. `import` and `export`. Requires `"type": "module"` in `package.json`.

The traps:

1. **File extensions in imports.** In ESM-mode Node, you MUST write `.js` extensions even for `.ts` source:
   ```ts
   import { foo } from "./bar.js";  // ✓  (even though file is bar.ts)
   import { foo } from "./bar";     // ✗  (ESM Node rejects this)
   ```
   This is because TS emits `.js` files, and the resolver matches the compiled output.
2. **`require()` of ESM is async.** You have to use `await import()` to load an ESM package from CJS code.
3. **`__dirname` and `__filename` don't exist in ESM.** Replace with `import.meta.url` + `fileURLToPath()`.
4. **Running TS directly.** `ts-node` is legacy. Use **`tsx`** (esbuild-based, handles both, zero config). Run a `.ts` file with `tsx path/to/file.ts`.

**Default for new projects in 2026:** ESM (`"type": "module"`), `tsx` for direct runs, `tsup` or Vite for bundling.

---

## The toolchain — what to pick and why

Every job has one modern default and one legacy option. Pick the modern one.

| Job | Modern default | Legacy |
|---|---|---|
| Run a `.ts` file | `tsx foo.ts` | `ts-node` |
| Type-check only | `tsc --noEmit` | (same) |
| Bundle a library | `tsup` (esbuild-based) | `rollup` with plugins |
| Bundle an app | **Vite** (esbuild + Rollup) | webpack |
| Test runner | **Vitest** (Vite-native, fast) | Jest |
| Linter + formatter | **Biome** (Rust, one tool) | ESLint + Prettier |
| Package manager | **pnpm** (disk-efficient, strict) | npm, yarn |
| Monorepo orchestrator | **Turbo** (cached parallel builds) | Lerna, Nx |

CI skeleton that validates everything:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm typecheck   # tsc --noEmit
      - run: pnpm test        # vitest run
      - run: pnpm lint        # biome check
```

One commit and you have typecheck + test + lint on every PR. This is the baseline every TS project should start with.

---

## Phase 1 in one line

**TypeScript = structural typing + discriminated unions + strict-mode null safety + a converging toolchain (Vite/tsup/Vitest/Biome/pnpm).** Once you've internalised the shape-based type system, the discriminant pattern for variants, branded types for domain distinctions, and the ESM-by-default toolchain, the rest of the language is Java-ish plus idioms.

**Capstone:** `artefacts/typescript-crash-course/phase-1/ts-patterns-cheat-sheet.md` — one-page sheet, 10 named patterns, with a 3-line C++/Python analogue per pattern. Usable as a quick reference when you're mid-build.

Next phase: async and streaming primitives — where the JS event loop meets WebSockets and backpressure.
