# Concurrency Primitives

Threads, atomics, memory ordering, and the lock-free SPSC queue — the machinery that moves a parsed message from the feedhandler thread to the strategy thread without a lock.

> **The theme:** on the hot path, the cost model isn't "is it correct?" — it's "how many nanoseconds, and how predictable?" A mutex is correct and *catastrophically* slow under contention. This phase is about getting correctness **and** single-digit-nanosecond handoffs by reasoning explicitly about what each thread is allowed to observe.

---

<!-- class: is-section -->

# Part one — the model

Two threads, one shared buffer, and the bug that doesn't reproduce until production.

---

## The problem in protocol code

A feedhandler decodes wire frames on one core; a strategy evaluates them on another. The decoded message has to cross the gap:

```
  Core 0 (feedhandler)            Core 1 (strategy)
  ┌──────────────────┐           ┌──────────────────┐
  │ parse packet      │  ──msg──▶ │ read msg          │
  │ write into buffer │           │ run strategy      │
  └──────────────────┘           └──────────────────┘
```

The naïve handoff — both threads touch the same variable — is the single most common source of "works on my machine, corrupts in prod" bugs in trading code. We need a way to pass data between cores that is both **correct** and **fast** (target: tens of nanoseconds, not microseconds).

+++

## The challenge — a data race is undefined behaviour

If two threads access the same memory location, at least one writes, and there's no synchronisation between them, that's a **data race** → **undefined behaviour**. Not "stale value" — *undefined*. The compiler is allowed to assume it never happens.

```cpp
bool ready = false;            // plain bool — NOT safe across threads
Message msg;

// Core 0                       // Core 1
msg = parse(packet);            while (!ready) {}   // may spin forever
ready = true;                   process(msg);       // may see torn msg
```

Two things can betray you, and both are invisible in a single-threaded mental model:

- **Compiler reordering** — `ready = true` may be hoisted *above* `msg = ...`.
- **CPU reordering** — Core 1 may observe `ready == true` before `msg`'s bytes land.

The fix is not "add `volatile`" (see Part three). The fix is a synchronisation primitive.

+++

## The first tool — `std::mutex` (and why the hot path rejects it)

`std::mutex` + `std::lock_guard` makes the handoff correct by mutual exclusion:

```cpp
std::mutex m;
{
  std::lock_guard<std::mutex> lk(m);   // acquire in ctor, release in dtor (RAII)
  shared = value;                       // critical section
}                                        // unlock here — exception-safe
```

Correct, and the right default for cold paths. But under contention a mutex can drop into a **kernel syscall** (`futex`) and invoke the OS scheduler — **microseconds**, and worse, *unbounded* jitter when a thread is descheduled holding the lock. On a path with a tens-of-nanoseconds budget, that's three orders of magnitude too slow. We need lock-free.

---

<!-- class: is-section -->

# Part two — `std::atomic`

The smallest correct unit of cross-thread communication.

---

## `std::atomic<T>` — problem and solution

**Problem:** we need a single variable that two threads can read and write with no torn reads, no lost updates, and no lock.

**Solution:** `std::atomic<T>` guarantees each operation is **indivisible** — another thread sees either the old value or the new value, never a half-written one.

```cpp
std::atomic<size_t> count{0};

count.store(1);                          // atomic write
size_t c = count.load();                 // atomic read
count.fetch_add(1);                      // atomic read-modify-write — returns old value
bool ok = count.compare_exchange_strong(expected, desired);  // CAS — see Part four
```

**The size constraint:** lock-freedom is only guaranteed for types the hardware can operate on atomically — on x86-64 that's `sizeof(T) ≤ 8`. (16-byte atomics *can* use `cmpxchg16b`, but mainstream GCC/Clang route them through `libatomic` and report **not** lock-free by default, because a 16-byte atomic *load* would have to write — so don't count on it.) A `std::atomic<BigStruct>` compiles but silently falls back to an internal lock — defeating the purpose.

+++

## `std::atomic` — validation

How you confirm it's actually doing what you think:

- `static_assert(std::atomic<T>::is_always_lock_free)` — a **compile-time** guarantee, fails the build if the platform would give you a hidden mutex. (`x.is_lock_free()` is the *runtime* equivalent — useful in a startup `assert`, but it can't fail the build.)
- A two-thread stress test: producer `fetch_add`s N times, consumer reads — the final value must equal N exactly (a plain `int` will lose updates and the count comes up short).
- Under ThreadSanitizer (`-fsanitize=thread`), the atomic version is clean; the plain-variable version reports the race. **TSan is the validation tool for this whole phase.**

---

<!-- class: is-section -->

# Part three — memory ordering

The hardest idea in the course, and the one that separates "it compiled" from "it's correct."

---

## The problem — atomicity is not ordering

Making `ready` atomic stops *torn* reads. It does **not**, by itself, guarantee that when Core 1 sees `ready == true`, it also sees the `msg` bytes Core 0 wrote *before* setting `ready`. Atomicity is about one variable; **ordering** is about what other writes become visible alongside it.

Each atomic operation takes a `std::memory_order` argument that says how much ordering you're buying:

| Order | Guarantee | Cost |
|---|---|---|
| `memory_order_relaxed` | Atomic only — no ordering w.r.t. other variables | Cheapest |
| `memory_order_acquire` | On a load: nothing after it can move before it | Cheap on x86 |
| `memory_order_release` | On a store: nothing before it can move after it | Cheap on x86 |
| `memory_order_seq_cst` | Single global total order across all threads | Most expensive — the default |

+++

## The solution — acquire/release pairing

This is the pattern you must be able to read on sight. The producer **releases**; the consumer **acquires** the *same* atomic. That pairing creates a *happens-before* edge:

```cpp
std::atomic<bool> ready{false};
Message msg;                             // plain data — no atomic needed

// Producer (Core 0)                     // Consumer (Core 1)
msg = parse(packet);                     while (!ready.load(acquire)) {}
ready.store(true, release);              process(msg);   // GUARANTEED to see msg
//          └─ "publish": every write    //         └─ "subscribe": everything the
//             before me is now visible   //            producer did before release
```

The guarantee: when the acquire-load observes the value the release-store wrote, **all writes the producer made before the release are visible to the consumer.** `msg` rides across on the back of the one atomic flag. This is how you publish a whole structure with a single atomic.

+++

## The trap — `volatile` is not `atomic`

A recurring interview filter. `volatile` was designed for memory-mapped hardware registers, not threads:

- `volatile` stops the **compiler** from reordering/eliding accesses to that variable.
- It does **nothing** about **CPU** reordering, and gives **no** atomicity for read-modify-write.

```cpp
volatile bool ready;     // WRONG for threading — no CPU-ordering, no happens-before
std::atomic<bool> ready; // RIGHT — atomicity + the ordering you ask for
```

Using `volatile` for thread communication is a data race wearing a disguise. The rule: **`volatile` for hardware, `atomic` for threads.** For an explicit standalone barrier there's `std::atomic_thread_fence(order)` — rarely needed once you're pairing acquire/release correctly.

---

<!-- class: is-section -->

# Part four — the lock-free SPSC queue

The single most important data structure in feedhandler-to-strategy plumbing.

---

## SPSC — problem and challenge

**Problem:** pass thousands of messages per microsecond from exactly one producer thread to exactly one consumer thread, with no lock and no allocation on the hot path.

**Challenge:** correctness without a lock means reasoning about ordering by hand, and *performance* means fighting the cache-coherence protocol — two cores writing nearby memory will ping-pong cache lines between them even when they touch logically separate variables.

The shape is a **ring buffer**: a fixed-size array with a write index (`tail`) and a read index (`head`), both wrapping with modulo. One producer owns `tail`, one consumer owns `head` — so there's no contention on either index, only publication across them.

+++

## SPSC — the solution

```cpp
template <typename T, size_t N>
class SpscQueue {
  alignas(64) std::atomic<size_t> head_{0};   // consumer's index — own cache line
  alignas(64) std::atomic<size_t> tail_{0};   // producer's index — own cache line
  alignas(64) std::array<T, N> buf_;

public:
  bool push(const T& v) {
    size_t t = tail_.load(relaxed);            // producer owns tail — relaxed is fine
    size_t next = (t + 1) % N;
    if (next == head_.load(acquire)) return false;   // full — acquire sees consumer's progress
    buf_[t] = v;                                // write payload FIRST
    tail_.store(next, release);                 // THEN publish — release pairs with pop's acquire
    return true;
  }

  bool pop(T& out) {
    size_t h = head_.load(relaxed);            // consumer owns head
    if (h == tail_.load(acquire)) return false; // empty — acquire sees producer's publish
    out = buf_[h];                              // read payload that release made visible
    head_.store((h + 1) % N, release);          // publish that the slot is free
    return true;
  }
};
```

The acquire/release pairs do all the synchronisation; there is no lock anywhere.

+++

## SPSC — false sharing, the silent killer

`head_` and `tail_` are *logically* independent, but if they share a 64-byte cache line, every producer write to `tail_` **invalidates the consumer's cached copy of the whole line** — including `head_` — and vice versa. The line bounces between cores on every operation. Throughput can drop 5–10×.

```
Without alignas:  [ head_ | tail_ | ... ]   ← one cache line, both cores fight over it
With alignas(64): [ head_ ........... ]      ← consumer's line
                  [ tail_ ........... ]      ← producer's line — no ping-pong
```

The fix is `alignas(64)` (the cache-line size) on each index so they land on separate lines. This is *the* reason you see `alignas(64)` scattered through lock-free code — and rigtorp's SPSCQueue additionally keeps a thread-local *cached* copy of the other index to avoid even reading the other core's line on the common path.

+++

## CAS and the ABA problem (for the multi-producer case)

SPSC needs no CAS — single owner per index. The moment you go multi-producer (MPSC/MPMC), two threads race to claim the same slot, and you need **compare-and-swap**:

```cpp
size_t expected = tail_.load();
while (!tail_.compare_exchange_weak(expected, expected + 1)) { /* expected reloaded */ }
//      └─ atomically: "if tail is still `expected`, set it to expected+1 and return true;
//         otherwise write the current value back into `expected` and return false"
```

**The ABA problem:** a CAS only checks the *value*, not the *history*. A pointer can be freed and a new node reallocated at the **same address** — the CAS sees the original value, succeeds, and corrupts the structure. Guards: tagged pointers (pack a generation counter beside the pointer), hazard pointers, or epoch reclamation. **Rule of thumb: reach for SPSC and a mutex first; only pay the CAS/ABA complexity when the profile proves you need MPMC.**

---

## SPSC — validation

You do **not** trust a lock-free queue by reading it. You validate:

- **Correctness under TSan** — run producer/consumer under `-fsanitize=thread`; it must be clean. A missing `release` shows up here.
- **A latency histogram across two cores** — pin producer and consumer to specific cores (`taskset`/`pthread_setaffinity_np`), timestamp each message round-trip, and plot the distribution. You care about **p99 / p999 / max**, not the mean — the tail is where jitter hides.
- **`perf c2c`** to detect false sharing directly: it reports cache lines bouncing between cores. After `alignas(64)`, the head/tail contention line should disappear.

This histogram-plus-`perf` discipline **is** the Phase 5 capstone.

---

<!-- class: is-dark -->

# Phase 5 takeaways

Five ideas to carry into real code:

1. **A data race is undefined behaviour, not a stale read** — the compiler assumes it can't happen, so it can do anything. `atomic` or synchronise; never a plain shared variable.
2. **Atomicity ≠ ordering.** `std::atomic` stops torn values; `memory_order` controls what *other* writes become visible. They are separate guarantees.
3. **Acquire/release is the publish/subscribe pattern** — producer `store(release)`, consumer `load(acquire)` on the *same* atomic carries every prior write across the gap.
4. **`volatile` is for hardware, `atomic` is for threads.** They are not interchangeable and `volatile` will silently fail to synchronise.
5. **False sharing is a latency bug with no logical symptom** — `alignas(64)` separates contended atomics onto their own cache lines. Validate with `perf c2c` and a tail-latency histogram, never with the mean.

---

## Glossary

- **Data race** — concurrent access to one location, ≥1 write, no synchronisation → undefined behaviour.
- **Atomic** — an operation other threads see as all-or-nothing; no torn reads/writes.
- **Memory order** — the visibility/reordering contract attached to an atomic op (`relaxed` < `acquire`/`release` < `seq_cst`).
- **Acquire / release** — paired loads/stores that create a happens-before edge so prior writes become visible.
- **Happens-before** — the formal "this write is visible to that read" relationship synchronisation establishes.
- **SPSC** — single-producer, single-consumer queue; one writer, one reader, no contention on either index.
- **Ring buffer** — fixed-size array with wrapping head/tail indices; no allocation after construction.
- **False sharing** — independent variables on the same cache line forcing coherence traffic between cores.
- **CAS** — compare-and-swap; atomic "set to desired only if still equal to expected." The building block of multi-producer structures.
- **ABA problem** — a CAS succeeds because the value matches, even though the underlying state changed and changed back.
