# Phase 4 Capstone — Buffer Container Benchmark

**Goal (from the plan):** a small benchmark comparing `std::vector` vs `std::array` vs a C array for a **fixed-size protocol message buffer**, plus a short written reflection — and include the `-O2` `perf stat` output.

This proves the Phase 4 claim in practice: for a compile-time-known buffer, `std::array` / C array store bytes **inline** (no heap, no indirection) while `std::vector` puts its data on the **heap** behind a pointer — and that difference is measurable, not theoretical.

## What you implement

`buffer_bench.cpp` has the timing harness done for you. Three functions are stubbed with `// TODO` — fill each so it:

1. Constructs a 48-byte message buffer of the given kind.
2. Writes a known payload into it (simulating a parse filling the frame).
3. Reads one field back out (so the optimiser can't delete the work).
4. Repeats for `ITERS` iterations; the harness times it.

Keep the *workload identical* across all three — only the container type changes. That's what makes the comparison fair.

## Build & run

```bash
g++ -std=c++17 -O2 -Wall -Wextra buffer_bench.cpp -o buffer_bench
./buffer_bench

# Capture the perf stat output the capstone requires:
perf stat -r 5 ./buffer_bench 2>&1 | tee perf-stat.txt
```

(On a box without `perf`, `/usr/bin/time -v` or the printed cycle counts are an acceptable fallback — note which you used.)

## The reflection note (the real deliverable)

Write `REFLECTION.md` answering:

1. **Which was fastest, and by how much?** Paste the numbers.
2. **Why?** Tie it back to *where the bytes live* — heap vs inline, allocation cost, cache locality, pointer indirection.
3. **Did `vector` with `reserve()` close the gap?** (Try it.) What did it fix, and what did it *not* fix?
4. **When would you still reach for `vector`** for a buffer, despite the cost?
5. **One sentence on what `perf stat` showed** — cache misses, instructions, or cycles that explain the ranking.

The benchmark proves recall; the reflection proves you understand *why*. The phase isn't closed until both `perf-stat.txt` and `REFLECTION.md` exist.
