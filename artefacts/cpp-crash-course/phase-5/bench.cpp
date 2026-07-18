// Phase 5 capstone bench — cross-core latency histogram for SpscQueue.
// Harness is complete; it compiles and runs once spsc_queue.hpp is implemented.
//
//   g++ -std=c++17 -Wall -Wextra -O2 -pthread bench.cpp -o bench && ./bench
//
// Method: producer (core 0) pushes a timestamped message roughly every
// PACE_NS; consumer (core 1) pops and records now - ts. Pacing keeps the
// queue near-empty so the histogram measures HANDOFF latency, not queueing
// delay — push at full speed instead and you are measuring occupancy.
// steady_clock costs ~20 ns per stamp; fine for a learning bench, switch to
// rdtsc if you want to see under that floor.

#include "spsc_queue.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <thread>
#include <vector>

#if defined(__linux__)
#include <pthread.h>
static void pin_to_core(int core) {
  cpu_set_t set;
  CPU_ZERO(&set);
  CPU_SET(core, &set);
  if (pthread_setaffinity_np(pthread_self(), sizeof(set), &set) != 0)
    std::fprintf(stderr, "warn: could not pin to core %d\n", core);
}
#else
static void pin_to_core(int) {}
#endif

using Clock = std::chrono::steady_clock;

struct Msg {
  std::uint64_t seq;
  Clock::time_point ts;
};

constexpr std::size_t QUEUE_CAP = 1024;
constexpr std::uint64_t SAMPLES = 1'000'000;
constexpr std::int64_t PACE_NS = 500;  // inter-send gap; keeps queue shallow

int main() {
  SpscQueue<Msg, QUEUE_CAP> q;
  std::vector<std::uint64_t> lat_ns(SAMPLES);

  std::thread consumer([&] {
    pin_to_core(1);
    Msg m;
    for (std::uint64_t received = 0; received < SAMPLES;) {
      if (q.pop(m)) {
        auto now = Clock::now();
        lat_ns[received++] =
            std::chrono::duration_cast<std::chrono::nanoseconds>(now - m.ts).count();
      }
      // busy spin — this is the hot-path consumer model
    }
  });

  std::thread producer([&] {
    pin_to_core(0);
    auto next_send = Clock::now();
    for (std::uint64_t seq = 0; seq < SAMPLES;) {
      auto now = Clock::now();
      if (now < next_send) continue;  // pace with a busy wait, no sleep jitter
      if (q.push(Msg{seq, now})) {
        ++seq;
        next_send = now + std::chrono::nanoseconds(PACE_NS);
      }
      // push false => queue full: consumer is behind, just retry
    }
  });

  producer.join();
  consumer.join();

  std::sort(lat_ns.begin(), lat_ns.end());
  auto pct = [&](double p) {
    return lat_ns[static_cast<std::size_t>(p * (SAMPLES - 1))];
  };
  std::uint64_t sum = 0;
  for (auto v : lat_ns) sum += v;

  std::printf("samples: %llu   pace: %lld ns\n",
              static_cast<unsigned long long>(SAMPLES),
              static_cast<long long>(PACE_NS));
  std::printf("min    %6llu ns\n", static_cast<unsigned long long>(lat_ns.front()));
  std::printf("p50    %6llu ns\n", static_cast<unsigned long long>(pct(0.50)));
  std::printf("p90    %6llu ns\n", static_cast<unsigned long long>(pct(0.90)));
  std::printf("p99    %6llu ns\n", static_cast<unsigned long long>(pct(0.99)));
  std::printf("p99.9  %6llu ns\n", static_cast<unsigned long long>(pct(0.999)));
  std::printf("max    %6llu ns\n", static_cast<unsigned long long>(lat_ns.back()));
  std::printf("mean   %6llu ns\n", static_cast<unsigned long long>(sum / SAMPLES));

  // Simple log-ish histogram for the writeup
  const std::uint64_t edges[] = {50, 100, 200, 500, 1000, 10000};
  std::size_t idx = 0;
  for (std::uint64_t edge : edges) {
    std::size_t upto =
        std::upper_bound(lat_ns.begin(), lat_ns.end(), edge) - lat_ns.begin();
    std::printf("<%6llu ns  %6.2f%%\n", static_cast<unsigned long long>(edge),
                100.0 * (upto - idx) / SAMPLES);
    idx = upto;
  }
  std::printf(">=10000 ns  %6.2f%%\n", 100.0 * (SAMPLES - idx) / SAMPLES);
  return 0;
}
