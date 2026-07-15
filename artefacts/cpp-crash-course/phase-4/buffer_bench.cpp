// Phase 4 capstone — buffer container benchmark.
// vector vs array vs C array for a fixed-size (48-byte) protocol message buffer.
//
// The timing harness is done. Fill the three TODO functions so each does the
// SAME work (construct buffer -> write payload -> read one field back), differing
// only in the container type. Then build at -O2 and run under `perf stat`.
//
//   g++ -std=c++17 -O2 -Wall -Wextra buffer_bench.cpp -o buffer_bench
//   perf stat -r 5 ./buffer_bench
//
// See README.md for the full task and the reflection questions.

#include <cstdint>
#include <cstdio>
#include <array>
#include <vector>
#include <chrono>

constexpr std::size_t MSG_SIZE = 48;
constexpr std::size_t ITERS    = 20'000'000;

// A trivial "parse": fill the buffer from a seed, return one field so the
// compiler cannot optimise the whole loop body away. Keep this logic identical
// across all three variants — only the container type should differ.
//
// Suggested contract for each function:
//   - declare the 48-byte buffer of the relevant kind
//   - for i in [0, MSG_SIZE): buf[i] = (uint8_t)(seed + i)
//   - return buf[MSG_SIZE - 1]  (the field read-back)

// --- variant 1: raw C array ------------------------------------------------
static inline uint8_t bench_c_array(uint8_t seed) {
    // TODO: uint8_t buf[MSG_SIZE]; fill it; return the last byte.
    (void)seed;
    return 0;
}

// --- variant 2: std::array<uint8_t, MSG_SIZE> ------------------------------
static inline uint8_t bench_std_array(uint8_t seed) {
    // TODO: std::array<uint8_t, MSG_SIZE> buf; fill it; return buf[MSG_SIZE-1].
    (void)seed;
    return 0;
}

// --- variant 3: std::vector<uint8_t> ---------------------------------------
// First write it the naive way (default-constructed, then push_back or resize).
// Then, for question 3 in the reflection, try a reserved/resized version and
// compare.
static inline uint8_t bench_std_vector(uint8_t seed) {
    // TODO: std::vector<uint8_t> buf; fill it to MSG_SIZE bytes; return last byte.
    (void)seed;
    return 0;
}

// --- harness ---------------------------------------------------------------
template <typename Fn>
static void run(const char* name, Fn&& fn) {
    using clock = std::chrono::steady_clock;
    uint64_t sink = 0;                       // accumulate so nothing is elided
    auto t0 = clock::now();
    for (std::size_t i = 0; i < ITERS; ++i)
        sink += fn(static_cast<uint8_t>(i));
    auto t1 = clock::now();
    double ns = std::chrono::duration<double, std::nano>(t1 - t0).count();
    std::printf("%-12s  %8.2f ns/op   (checksum %llu)\n",
                name, ns / ITERS, static_cast<unsigned long long>(sink));
}

int main() {
    std::printf("buffer bench — %zu-byte message, %zu iterations\n\n",
                MSG_SIZE, ITERS);
    run("c_array",    bench_c_array);
    run("std_array",  bench_std_array);
    run("std_vector", bench_std_vector);
    return 0;
}
