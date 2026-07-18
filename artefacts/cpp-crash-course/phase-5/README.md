# Phase 5 capstone — SPSC queue + cross-core latency histogram

**Status: ⚠ OPEN — queue not yet implemented.** Session 14 was marked done 2026-07-18 by explicit capstone-gate override ("exact snippet from slides"); the gap stands with Phases 3 and 4 and lands on Session 15.

## Deliverable

1. `spsc_queue.hpp` — working SPSC ring buffer (own implementation or annotated rigtorp fork). Skeleton has the spec and checklist; `push`/`pop` are stubbed.
2. `bench.cpp` — complete harness (do not need to modify): pins producer to core 0 and consumer to core 1, paces sends to measure handoff latency, prints percentiles + histogram over 1M samples.
3. This README's **Reflection** section filled in after the run.

## Build & run

```
g++ -std=c++17 -Wall -Wextra -O2 -pthread bench.cpp -o bench && ./bench
```

## Reflection (fill in after the bench runs)

- Measured p50 / p99 / max, and whether the numbers moved with the index-cache stretch goal:
- Why ever-growing counters instead of wrapped indices (quiz Q7 in your words):
- The member layout chosen and the writing-thread principle behind it (quiz Q8):
- What the head pairing publishes and what breaks if it's relaxed (quiz Q9):
