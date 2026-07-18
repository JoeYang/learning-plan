# Quiz: Session 14 — Lock-Free Patterns: SPSC Queues & CAS

**Date:** 2026-07-18
**Score:** 7 / 10 *(gate met; taken after a full Apply walkthrough including the interactive CAS/ABA visual)*

**Instructions:** 7 multiple-choice + 3 short-answer. Answers at the bottom.

---

### Q1. Why can an SPSC queue use plain load/store on its indices, while an MPSC queue is forced into a CAS loop for its tail?

A) SPSC queues are bounded by a fixed capacity, so the indices cannot race past each other beyond one lap of the ring
B) In SPSC every atomic index has exactly one writer thread, so no other writer can interleave between its load and its store
C) SPSC stores are cheaper because the consumer never needs to read the producer's tail index on its own hot path
D) The compiler detects the single-consumer pattern and promotes the atomics to plain variables with fence instructions

---

### Q2. Producer: `buf_[t % N] = v; tail_.store(t+1, X);` — consumer: spin on `tail_.load(Y)`, then read `buf_[h % N]`. Cheapest CORRECT X/Y?

A) X = release, Y = acquire — the store publishes the payload write, the load subscribes to it, forming the happens-before edge
B) X = relaxed, Y = relaxed — atomicity suffices here because tail_ has exactly one writer thread and one reader thread
C) X = seq_cst, Y = seq_cst — publication across two threads requires both sides to agree on the single global order
D) X = release, Y = relaxed — the release half alone creates the edge, so the consumer side can load at the cheapest order

---

### Q3. Which statement about `alignas(64)` on the SPSC queue's two indices is FALSE?

A) It puts head_ and tail_ on separate cache lines, so a write to one no longer invalidates the other core's copy of the other
B) Removing it cannot make the queue incorrect — false sharing degrades throughput and latency but never correctness
C) It exists because cache coherence protocols track ownership at whole-line granularity, never at variable granularity
D) It makes reading the other side's index free, since after alignment each core holds an exclusive copy of every line it reads

---

### Q4. `expected = 5; ok = tail_.compare_exchange_strong(expected, 6);` runs while tail_ holds 6. State immediately after?

A) ok == false, tail_ still holds 6, and expected has been overwritten with 6 — ready for an immediate retry with fresh knowledge
B) ok == false, tail_ still holds 6, and expected still holds 5 — the caller must reload the atomic manually before retrying
C) ok == false, but tail_ was advanced to 6 by this call as a side effect, since strong CAS always completes one update
D) ok == true, because compare_exchange_strong — unlike the weak form — retries internally until the exchange goes through

---

### Q5. A CAS-based stack suffers ABA when a node's address is freed and recycled during a stall. Which change actually eliminates the problem?

A) Re-read the head and verify top->next a second time immediately after the CAS reports success, undoing it on mismatch
B) Replace compare_exchange_weak with compare_exchange_strong so the comparison cannot succeed spuriously during a stall
C) Widen the CAS to a pointer paired with a monotonically increasing generation counter, so recycled bits still fail the compare
D) Upgrade every load and CAS in the pop path to seq_cst so the global total order exposes the intervening modifications

---

### Q6. rigtorp's producer full-check consults plain `readIdxCache_` first and acquire-loads `readIdx_` only when the cache says full. Why is trusting the possibly-stale cache safe, and what does it buy?

A) Stale values only underestimate free space since readIdx_ never decreases, so the worst case is a needless refresh — and the common path stops pulling the consumer's cache line
B) The cache is refreshed under acquire ordering on every push, so it can never actually be stale by more than one pop when the producer reads it
C) Stale values only overestimate free space, which is safe because the subsequent placement-new fails cleanly when it reaches a slot that is still occupied
D) The compiler is free to elide the plain read entirely, so the cache is a formality that documents intent rather than changing generated code

---

### Q7. Designing the index scheme for a new MPMC queue (producers AND consumers CAS-claim positions). Which design is right, and why?

A) Wrapped indices with one wasted slot — taking the modulo of ever-growing counters would put a hardware division on the hot path
B) Wrapped indices with seq_cst on every operation — the single global order exposes any lap that happens during a producer stall
C) Monotonic ever-growing counters — a CAS compare can then treat "same value" as "nothing happened", which wrapped values stop guaranteeing after one lap
D) Either scheme works when capacity is a power of two — bit-masking makes the wrapped and monotonic representations behave identically

---

### Q8 (short answer). rigtorp gives all four index members `alignas(kCacheLineSize)` — including the two plain, non-atomic caches. Why do the caches need their own lines, and what is the general principle?

**Rubric:** (1) the caches are hot, core-local state read/written by their owning core on every operation; (2) sharing a line with a foreign-written member (e.g. readIdxCache_ with consumer-written readIdx_) means the foreign store invalidates the line and the owner's access to its own private variable starts missing in L1 — false sharing through the back door; (3) principle: group/separate members by **writing thread**, not by atomic-vs-plain.

---

### Q9 (short answer). The consumer's pop ends `out = buf_[h % N]; head_.store(h+1, release);`. A colleague relaxes the store, arguing head_ has one writer and the producer only uses it for a full check. What concrete failure does this enable? Name the pairing and what it publishes.

**Rubric:** (1) this store is the consumer→producer **ownership-return** edge (pairs with the producer's acquire-load of head_) — it publishes "my read of the slot is complete", not data; (2) relaxed allows the store to become visible before the payload read completes; (3) the producer's acquire-load then sees the freed slot and **overwrites it while the consumer's read is in flight** → torn read, no lock to save you.

---

### Q10 (short answer). The desk wants the battle-tested MPMC queue on a structurally SPSC feed→strategy path, "so we never have to touch it if a second feed thread appears." Make the case for SPSC: (a) machinery MPMC forces, (b) what single-writer buys, (c) rebut the future-proofing argument.

**Rubric:** (1) MPMC machinery: CAS/RMW loops on both ends, ABA-safe scheme (tagged/versioned indices), per-slot sequence numbers (Vyukov) to detect ownership; (2) single-writer dividend: plain load/store with relaxed/acquire/release, no CAS, no retry, no contention, index-cache optimizations; (3) rebuttal: daily tail-latency tax for a hypothetical topology; the swap later is localized and mechanical behind the same push/pop contract — don't optimize for a change that may never come at the expense of the workload you have.

---

## Answers & result (2026-07-18)

| Q | Correct | Joe | Result |
|---|---|---|---|
| 1 | B | B | ✓ |
| 2 | A | A | ✓ |
| 3 | D | A | ✗ — alignment removes *collateral* invalidations; legitimate reads of the other index still transfer its line (that inherent cost is what the index caches attack) |
| 4 | A | A | ✓ |
| 5 | C | A | ✗ — picked "re-check after CAS", the fix explicitly debunked in Apply (check lands after the commit; dereferences freed memory; invariant must hold *inside* the atomic step) |
| 6 | A | A | ✓ |
| 7 | C | C | ✓ |
| 8 | rubric 2/3 | — | ◐ half — invalidation mechanism perfect (incl. owner's private variable missing in L1); general separate-by-writing-thread principle unstated |
| 9 | rubric 2/3 | — | ◐ half — reorder caught and pairing named; missed the producer-overwrites-mid-read agent and mislabelled the edge as data-publishing (it publishes ownership) |
| 10 | rubric 3/3 | — | ✓ full — named Vyukov per-slot sequence numbers unprompted; "optimizing for a change that may never come at the expense of the workload you actually have" |

**Weak areas for the Phase 5 retrieval check:** the ABA fix — widen the compare (generation counter), never check-after (missed twice in one day: Apply Q5b and quiz Q5); what alignas does vs doesn't buy (collateral vs inherent line transfers, Q3); the head edge publishes *ownership*, not data (Q9).

**Confirmed closed:** memory-order selection by the visibility axis — the S13 repeated gap — went 6/6 in Apply and 3/3 across quiz Q1/Q2/Q6.

**Note:** Session 14 closes Phase 5 **only when the capstone exists**: working SPSC queue (own or annotated rigtorp fork) + latency-histogram benchmark across two cores in `artefacts/cpp-crash-course/phase-5/`. Apply also produced an interactive CAS/ABA explainer (3 tabs: live ring, CAS race, ABA walk) pending save to `docs/interactive/cpp-crash-course/cas-aba.html`.
