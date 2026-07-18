# Quiz: Session 13 — std::thread & std::atomic Basics

**Date:** 2026-07-16
**Score:** 7 / 10 *(cold quiz — taken before the Session 13 Apply step; gate met exactly)*

**Instructions:** 7 multiple-choice + 3 short-answer. Answers at the bottom.

---

### Q1. Four threading scenarios. Exactly one is a data race (and therefore undefined behaviour) — which?

A) Two threads concurrently read a lookup table built before either thread started; nobody writes
B) Thread 1 writes only `arr[0]` while thread 2 writes only `arr[1]` — same array, disjoint elements, no sync
C) Thread 1 stores to a `std::atomic<bool>` with `memory_order_relaxed` while thread 2 loads it relaxed
D) Thread 1 sets a plain `bool ready = true` while thread 2 spins in a loop reading it until true

---

### Q2. A `std::mutex`-guarded handoff is correct but rejected for a path with a tens-of-nanoseconds budget. What is the actual cost mechanism that disqualifies it?

A) Under contention the lock can drop into a kernel futex syscall and involve the OS scheduler — microseconds, with unbounded jitter if the holder is descheduled
B) Each lock/unlock executes a syscall on every acquisition, so even an uncontended critical section costs a microsecond
C) Every mutex operation issues full memory fences that serialize the CPU pipeline at a fixed ~100 ns per lock
D) Mutex objects live on the heap behind a pointer, so each acquisition is a dependent load and cache miss

---

### Q3. Twelve workers each increment a shared `std::atomic<uint64_t>` counter; a monitor reads it once after all workers have joined. Cheapest *correct* memory order for the increments?

A) seq_cst — many writers need the single global total order
B) acquire — each increment must observe every prior increment first
C) relaxed — only atomicity is needed; nothing else is ordered against the counter and join() synchronises the final read
D) release — each increment publishes the worker's progress to the monitor

---

### Q4. `msg` is plain data; `ready` is `std::atomic<bool>`. Three handoffs are correct (whatever their speed); one lets the consumer process garbage. Which?

A) Producer: `msg = parse(packet); ready.store(true, release);` — consumer: acquire-load loop, then `process(msg)`
B) Producer: `ready.store(true, release); msg = parse(packet);` — consumer: acquire-load loop, then `process(msg)`
C) Producer: `msg = parse(packet); ready.store(true);` (seq_cst) — consumer: default-load loop, then `process(msg)`
D) Both sides take the same `std::lock_guard` around their access to `msg` and the flag

---

### Q5. A colleague declares the handoff flag `volatile bool ready;` — "the compiler won't optimise it away, so it's thread-safe." Why is volatile the wrong tool?

A) volatile constrains the compiler only (no caching/eliding) but gives no atomicity and no CPU-reordering or cross-core visibility guarantees
B) volatile forces a full cache-line flush on every access — correct for threading but too slow for a hot-path flag
C) volatile works for a single machine word but silently loses its guarantees on wider types
D) compound volatile operations were deprecated in C++20, so modern toolchains reject cross-thread volatile flags

---

### Q6. You declare `std::atomic<Quote> quote;` for a 24-byte struct. It compiles and runs. What actually happened, and what's the right guard?

A) The compiler decomposes it into three 8-byte lock-free atomics kept consistent
B) std::atomic over the hardware width is undefined behaviour that appears to work
C) Loads/stores stay lock-free but may tear across cache lines; guard with `alignas(64)`
D) It silently falls back to an internal mutex; catch at build time with `static_assert(std::atomic<Quote>::is_always_lock_free)`

---

### Q7. You replaced a mutex handoff with atomics; the suite passes 100 runs. Given the failure mode is a data race, the *strongest* pre-ship verification?

A) Soak the tests overnight on a loaded machine until any interleaving bug surfaces
B) Build with `-fsanitize=thread` and exercise producer/consumer — TSan reports races from the memory model even on runs with correct output
C) Run under valgrind memcheck — racing reads/writes appear as memory errors
D) Add debug asserts on shared-value invariants so torn reads trip an abort

---

### Q8 (short answer). `ready` is now `std::atomic<bool>` — "no torn reads, handoff fixed." The message is still plain data written just before the flag. What does the atomic flag alone guarantee / not guarantee, and what does acquire/release pairing add?

**Rubric:** (1) atomic = no torn read/write on the flag itself; (2) it does NOT order other writes — consumer can see `ready == true` with `msg` still stale; (3) release-store + acquire-load on the *same* atomic creates a happens-before edge: all producer writes before the release are **visible** after the acquire — a visibility guarantee, not atomicity of the payload.

---

### Q9 (short answer). Assign the cheapest correct order (relaxed / acquire / release / seq_cst) with justification: (a) per-thread heartbeat counter summed after join(); (b) consumer's load of a ready flag; (c) producer's store of that flag; (d) a cold-path config flag you don't want to reason carefully about.

**Rubric:** (a) relaxed — atomicity only, join() gives the happens-before; (b) acquire — subscribe side of the pairing; (c) release — publish side; (d) seq_cst — cost irrelevant on cold path, buy the strongest guarantee and stop reasoning.

---

### Q10 (short answer). "Use a mutex first, optimize later." Two situations where a mutex is genuinely right even in a trading system, and the failure mode you accept by jumping straight to lock-free?

**Rubric:** (1) cold path / no strict latency budget (also: uncontended locks are ~20 ns user-space CAS); (2) multi-variable invariants that don't fit a single atomic; (3) failure mode: mis-ordered atomics are silent UB — heisenbugs that pass tests and corrupt state under production interleavings, complexity paid without measured contention to justify it.

---

## Answers & result (2026-07-16)

| Q | Correct | Joe | Result |
|---|---|---|---|
| 1 | D | D | ✓ |
| 2 | A | A | ✓ |
| 3 | C | A | ✗ — priced by "how busy is the code" instead of "what must be visible alongside the atomic"; relaxed suffices when nothing else is ordered against it |
| 4 | B | D | ✗ — mutex version is slow-but-correct; B publishes the flag *before* writing the payload (payload first, publish second) |
| 5 | A | A | ✓ |
| 6 | D | D | ✓ |
| 7 | B | B | ✓ |
| 8 | rubric 2/3 | — | ◐ half — atomicity-vs-ordering line drawn correctly; said pairing "makes the data atomic" — it creates happens-before *visibility*, payload stays plain |
| 9 | rubric 2/4 parts | — | ◐ half — (b)/(c) publish-subscribe pair solid; (a) seq_cst→relaxed and (d) relaxed→seq_cst inverted, same axis error as Q3 |
| 10 | rubric 3/3 | — | ✓ full — cold path + uncontended + complexity-without-benefit; sharpened with silent-UB framing and the multi-variable-invariant case |

**Weak areas for the retrieval check:** choosing memory orders by the visibility axis (Q3, Q9a/d — repeated miss, the one genuine gap); payload-first/publish-second program order (Q4); happens-before gives *visibility*, not payload atomicity (Q8 precision).

**Note:** gate met at exactly 7/10 on a cold quiz. The publish/subscribe pairing itself (release/acquire on the same atomic) is clearly absorbed — the open gap is *selecting* orderings for cases that aren't the canonical pair.
