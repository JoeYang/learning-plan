#pragma once
// Phase 5 capstone — SPSC ring buffer. YOUR implementation (or a rigtorp fork
// with your own annotations — if you fork, annotate every memory order and
// every alignas with WHY, in your words).
//
// Spec (plans/cpp-crash-course.md, Phase 5 capstone line):
//   - single producer, single consumer; fixed capacity; no allocation after construction
//   - push/pop never block; return false on full/empty
//   - indices are ever-growing counters; slot = index & (N - 1)
//     (document in README why this beats wrapped indices — your quiz Q7 answer)
//   - cheapest correct memory order on every atomic access (the (a)-(f) recipe)
//   - alignas(64) layout separated by WRITING THREAD (your quiz Q8 principle)
//
// Checklist while implementing:
//   [ ] tail pairing (release store / acquire load) — moves data forward
//   [ ] head pairing (release store / acquire load) — moves slot ownership back
//   [ ] full check:  t - head >= N   |   empty check:  tail == h
//   [ ] stretch goal: rigtorp-style index caches (readIdxCache_/writeIdxCache_,
//       each on its own line) — then compare bench p50 with and without
//
// Build check: g++ -std=c++17 -Wall -Wextra -O2 -pthread bench.cpp -o bench

#include <atomic>
#include <array>
#include <cstddef>

template <typename T, std::size_t N>
class SpscQueue {
  static_assert(N != 0 && (N & (N - 1)) == 0, "N must be a power of two");

public:
  bool push(const T& v) {
    // TODO(joe): implement — producer thread only
    (void)v;
    return false;
  }

  bool pop(T& out) {
    // TODO(joe): implement — consumer thread only
    (void)out;
    return false;
  }

private:
  // TODO(joe): storage + indices (+ optional caches) with a deliberate
  // alignas layout. Decide member order consciously and defend it in README.
  std::array<T, N> buf_{};
};
