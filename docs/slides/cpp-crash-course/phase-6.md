# Reading Real Code

The capstone: open a real open-source C++ protocol handler and read it top to bottom — naming, for every non-obvious line, which of the 14 sessions taught you that pattern.

> **The theme:** the whole course was reverse-engineering. You learned each pattern in isolation so that when you meet it *in the wild* — undocumented, terse, optimised — you read it as intent, not noise. This phase proves that. No new concepts; only synthesis.

---

<!-- class: is-section -->

# Part one — how to read hot-path code

A method, so you don't just scroll past the hard parts.

---

## The problem with reading optimised C++

Hot-path code is written to be *fast*, not *obvious*. It is dense with `reinterpret_cast`, `alignas`, template machinery, and memory-order arguments — and it almost never comments *why*. Read it linearly and you stall on the first `static_cast<Derived*>(this)` and lose the thread.

The method that works:

1. **Find the data first.** What are the structs? How are they laid out? (Phase 1.)
2. **Find ownership.** Who allocates, who frees, what's RAII? (Phase 2.)
3. **Find the dispatch.** How does a message reach the right handler — virtual, CRTP, tag, `if constexpr`? (Phase 3.)
4. **Find the containers.** What holds order/book state, and why that choice? (Phase 4.)
5. **Find the threading boundary.** Where does data cross cores, and how is it synchronised? (Phase 5.)

Read in that order and the code resolves into intent.

---

## The pattern checklist — parsing & compile-time (1–4)

For the capstone you must find, quote, and explain each of these in the chosen codebase:

| # | Pattern | Taught in | The tell-tale sign |
|---|---|---|---|
| 1 | Zero-copy parse via `reinterpret_cast` | S3 | `reinterpret_cast<const Msg*>(buf)` |
| 2 | Packed struct + `static_assert` size guard | S2, S10 | `#pragma pack` / `static_assert(sizeof(...)==N)` |
| 3 | CRTP or template dispatch | S7, S8 | `class X : public Base<X>` |
| 4 | `constexpr` protocol constants | S10 | `constexpr` tags, sizes, table sizes |

---

## The pattern checklist — runtime & structure (5–8)

| # | Pattern | Taught in | The tell-tale sign |
|---|---|---|---|
| 5 | `std::atomic` with memory ordering | S13 | `.load(acquire)` / `.store(v, release)` |
| 6 | SPSC / ring buffer for inter-thread messaging | S14 | `alignas(64)` head/tail, modulo wrap |
| 7 | Smart pointer / RAII resource management | S5, S6 | `unique_ptr`, lock_guard, dtor cleanup |
| 8 | STL container for order/book state | S4, S11 | `std::map` book, `unordered_map` order state |

For each: a two-sentence *what + why*. Patterns you can't explain get flagged for follow-up, not skipped.

---

## What an annotation looks like — the bar

One worked example, at the standard the capstone expects. From rigtorp's member block:

```cpp
alignas(kCacheLineSize) size_t readIdxCache_ = 0;   // SPSCQueue.h
```

**What:** a producer-local, *non-atomic* stale copy of the consumer's index. The full-check consults it first; only when it claims the queue is full does the producer refresh it with an acquire-load of the real `readIdx_`.

**Why:** it keeps the common-path push entirely inside cache lines the producer already owns — the consumer's line is pulled only on apparent-full. Trusting a stale value is safe because `readIdx_` is monotonic: staleness can only *under*-estimate free space, so the error direction is a harmless extra check, never an overwrite. One cheap conditional buys the removal of a guaranteed cross-core line transfer per push.

That's the bar: *what* names the mechanism, *why* names the trade-off — in your words, not the author's.

---

<!-- class: is-section -->

# Part two — where to read

Three good targets, in increasing size.

---

## Choosing a codebase

| Codebase | Size | What it exercises best | Why pick it |
|---|---|---|---|
| **rigtorp/SPSCQueue** | Tiny (one header) | Phase 5 in full: atomics, acquire/release, `alignas(64)`, cached indices | Start here — small enough to read in one sitting and every line earns its place |
| **NASDAQ ITCH parser** | Small–medium | Phases 1–3: packed structs, `reinterpret_cast`, `static_assert`, dispatch | Best for the binary-parsing patterns; many open-source versions on GitHub |
| **SoupBinTCP impl** | Medium | Session/framing layer + RAII + buffering | The transport beneath ITCH — connection lifecycle and resource management |

Recommended path: **read rigtorp/SPSCQueue first** (it's the reference for Phase 5 and the course's running example), then an ITCH parser for the parsing patterns. Between the two you'll hit all eight checklist items.

---

## Read with your gaps in hand

The quiz record knows where you're weak, and the read-through walks straight past the lines that re-test each gap. **Produce each answer from memory before reading on** — produced beats read.

| Recorded gap | Where you'll meet it | The check |
|---|---|---|
| The ABA fix (missed 2×) | rigtorp has **no CAS anywhere** | Why doesn't it need one? Write the fix if it did |
| `alignas`: collateral vs inherent | the four `alignas` members | Which invalidations go, which remain, what attacks the rest? |
| Head edge publishes *ownership* | the `readIdx_` store in `pop()` | One sentence: what does this release publish? |
| Payload-first, publish-second | slot write before `writeIdx_` store | Confirm the order; what breaks if relaxed? |

Answers go straight into the walkthrough as the pattern 5–6 annotations.

---

## What "done" looks like — the deliverable

The capstone artefact is a **written annotated walkthrough** of the codebase (the Phase 6 capstone in the plan; lives in the session log or `artefacts/cpp-crash-course/phase-6/`):

- Each of the 8 patterns: the quoted line(s), the file/location, and your two-sentence *what + why*.
- A short "still don't understand" list — honest gaps flagged for follow-up. This list is a feature, not a failure; it's the input to your next learning loop.
- One paragraph of synthesis: *what does reading this end-to-end tell you about how the author traded off readability for latency?*

If you can produce that document, you can read production hot-path C++. That's the whole point of the course.

---

## The 90-minute plan

One session, timeboxed — the "still don't understand" list is the pressure-release valve when a box overruns:

```
  0–30    rigtorp/SPSCQueue, every line — patterns 5, 6 + all four gap-checks
 30–70    ITCH parser — patterns 1, 2, 3, 4, 7, 8
 70–90    writeup: annotations → synthesis paragraph → still-don't-understand list
```

Optional but recommended pre-step (~40 min, before the session): implement the stubbed `spsc_queue.hpp` capstone and run the bench. Then rigtorp reads as a *comparison against your own decisions* instead of a first encounter — and one of the three open capstone debts (P3 templates, P4 buffer bench, P5 SPSC) is already cleared before the course closes.

---

<!-- class: is-dark -->

# Course takeaways

What the 15 sessions add up to:

1. **Memory is the substrate.** Layout, alignment, and where the bytes live (stack/heap/cache line) drive every other decision.
2. **The compiler is a runtime you can program** — templates, CRTP, `constexpr`, `if constexpr` move work from the hot path to build time at zero runtime cost.
3. **Container choice is a latency decision**, judged on cache behaviour and worst case, not average-case big-O.
4. **Correctness across cores is about visibility**, not just mutual exclusion — acquire/release publishes data, false sharing silently destroys throughput.
5. **You can now read it.** The patterns are finite; you've met them all. Production code is just these patterns, composed.

---

## Glossary

- **Zero-copy parse** — interpreting received bytes in place via a cast, with no copy into a separate struct.
- **ITCH** — NASDAQ's binary market-data protocol; fixed-layout messages, the canonical parsing exercise.
- **SoupBinTCP** — the framing/session transport that carries ITCH over TCP.
- **Synthesis** — the capstone skill: recognising a learned pattern inside unfamiliar, uncommented real code.
