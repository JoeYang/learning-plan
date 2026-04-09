# Day 10 (Sat Apr 18) -- Low-Latency System Design Patterns

## Overview (5 min)

Low-latency programming is the defining technical discipline at Jump Trading. While most software engineering optimizes for throughput, maintainability, or developer productivity, trading systems optimize for the time between receiving market data and sending an order. A 1-microsecond advantage translates directly into profit. This day covers the patterns, techniques, and mental models that separate a standard backend engineer from a low-latency systems engineer. Every concept here has direct application to the Futures Execution Services role.

---

## Reading Materials (60-90 min)

### 1. Memory Management

**The GC Problem**

Garbage collection is the enemy of predictable latency. A GC pause of even 10 milliseconds is catastrophic in a system where the total latency budget is 2-5 microseconds. Even "low-pause" collectors like G1GC can introduce multi-millisecond pauses during full GC events.

**Object Pooling**

Instead of allocating new objects and letting the GC reclaim them, pre-allocate a pool of objects at startup and reuse them:

```java
// Bad: allocates on every message
OrderMessage msg = new OrderMessage();  // GC pressure

// Good: pool of pre-allocated messages
OrderMessage msg = messagePool.acquire();
try {
    msg.reset();
    msg.setPrice(price);
    msg.setQuantity(qty);
    process(msg);
} finally {
    messagePool.release(msg);
}
```

The pool is typically a fixed-size ring buffer or a stack (LIFO for cache warmth). All objects are allocated at startup, so the pool adds zero GC pressure during operation.

**Pre-allocation**

Beyond object pooling, pre-allocate all data structures to their maximum expected size:

```java
// Bad: grows dynamically, triggers GC from old arrays
List<Order> orders = new ArrayList<>();

// Good: pre-sized, never resizes
List<Order> orders = new ArrayList<>(MAX_ORDERS);
// Or better: use a primitive array
Order[] orders = new Order[MAX_ORDERS];
int orderCount = 0;
```

Pre-allocating eliminates:
- Dynamic resizing (which copies the old array and creates garbage)
- Unpredictable allocation timing
- Memory fragmentation

**G1GC Tuning (when you must use Java)**

If you are stuck with Java (as many trading systems are for non-latency-critical paths), G1GC is the standard choice:

```
-XX:+UseG1GC
-XX:MaxGCPauseMillis=1          # Target max pause (aspirational)
-XX:G1HeapRegionSize=16m        # Larger regions = fewer regions to track
-XX:InitiatingHeapOccupancyPercent=30  # Start GC earlier, avoid full GC
-Xms8g -Xmx8g                  # Fixed heap size (no resizing)
-XX:+AlwaysPreTouch             # Touch all pages at startup (avoid page faults)
```

Key principles:
- Fixed heap size (Xms = Xmx) to avoid heap resizing.
- AlwaysPreTouch to force the OS to allocate physical pages at startup rather than on first access (avoiding page faults on the hot path).
- Low initiating occupancy to trigger concurrent GC cycles early and avoid emergency full GC pauses.

**Off-Heap Storage**

For the most latency-sensitive data, bypass the managed heap entirely:

```java
// Java: use DirectByteBuffer or Unsafe
ByteBuffer buffer = ByteBuffer.allocateDirect(1024 * 1024);

// Or using sun.misc.Unsafe for direct memory access
long address = UNSAFE.allocateMemory(size);
UNSAFE.putLong(address + PRICE_OFFSET, price);
long price = UNSAFE.getLong(address + PRICE_OFFSET);
```

Off-heap memory is invisible to the GC. The trade-off: you lose type safety, bounds checking, and automatic cleanup. You are effectively writing C inside Java.

**C++ Approach**

C++ avoids GC entirely but introduces its own memory management challenges:
- Use custom allocators (pool allocators, arena allocators) to avoid system malloc calls on the hot path.
- `malloc` and `free` acquire global locks in many implementations -- deadly for latency.
- Pre-allocate all memory at startup. The hot path should have zero allocations.

```cpp
// Arena allocator: bump pointer, O(1) allocation, bulk deallocation
class Arena {
    char* base_;
    char* current_;
    char* end_;
public:
    void* allocate(size_t size) {
        // No branching, no locks, no system calls
        char* result = current_;
        current_ += size;
        return result;
    }
    void reset() { current_ = base_; }  // "free" everything at once
};
```

### 2. Data Structures for Speed

**Cache Locality: The Dominant Factor**

On modern hardware, a cache miss costs ~100 nanoseconds (main memory access). A cache hit costs ~1 nanosecond (L1) to ~10 nanoseconds (L3). This 10-100x difference means data layout matters more than algorithmic complexity for small-to-medium-sized data.

```
Register:     ~0.3 ns
L1 Cache:     ~1 ns      (32-64 KB)
L2 Cache:     ~4 ns      (256 KB - 1 MB)
L3 Cache:     ~10 ns     (8-32 MB, shared across cores)
Main Memory:  ~100 ns
```

**Arrays Over Linked Lists**

A linked list has O(1) insertion/deletion, but each node is a separate allocation scattered in memory. Traversing a linked list causes a cache miss on nearly every node. An array stored contiguously in memory benefits from hardware prefetching -- the CPU speculatively loads the next cache line before you ask for it.

```
Linked List: [Node] -> ... -> [Node] -> ... -> [Node]
              0x1000          0x5A00          0x2300
              (cache miss)    (cache miss)    (cache miss)

Array:       [Elem][Elem][Elem][Elem][Elem][Elem]
              0x1000                              
              (one cache miss, then all hits from prefetch)
```

For a trading system's order book with price levels, an array indexed by tick offset from a reference price is dramatically faster than a balanced BST, even though the BST has better theoretical complexity for some operations:

```cpp
// Price level array indexed by tick offset
// Assume price range is bounded (e.g., 10000 ticks)
struct PriceLevel {
    int64_t total_qty;
    Order* head;  // linked list of orders at this level
};

PriceLevel levels[MAX_TICKS];  // contiguous, cache-friendly

// Access best bid: scan down from last known best
// In practice, price changes are small, so scan is 1-2 steps
```

**Open-Addressing Hash Maps**

Standard hash maps (e.g., `std::unordered_map`, Java `HashMap`) use chaining -- each bucket contains a linked list of entries. This causes pointer chasing and cache misses.

Open-addressing hash maps store all entries in a single contiguous array. On collision, they probe to the next slot. This is dramatically more cache-friendly:

```
Chained (std::unordered_map):
  Buckets: [ptr] [ptr] [ptr] [ptr]
             |     |
             v     v
           [K,V]->[K,V]    (pointer chasing = cache misses)
           [K,V]

Open-addressing:
  Slots: [K,V] [K,V] [empty] [K,V] [K,V] [empty]
          (all contiguous, prefetch-friendly)
```

Libraries like `absl::flat_hash_map` (Google), `robin_hood::unordered_map`, or `ankerl::unordered_dense` use open addressing and are standard in trading systems.

**Struct-of-Arrays (SoA) vs Array-of-Structs (AoS)**

```cpp
// Array of Structs (AoS) -- traditional
struct Order {
    int64_t price;
    int32_t quantity;
    int64_t timestamp;
    char side;
    // ... 7 bytes padding
};
Order orders[N];
// To sum all prices: loads entire struct per element (wastes bandwidth)

// Struct of Arrays (SoA) -- cache-friendly for columnar access
struct Orders {
    int64_t prices[N];
    int32_t quantities[N];
    int64_t timestamps[N];
    char sides[N];
};
// To sum all prices: sequential access to prices array only
// Perfect for SIMD vectorization
```

SoA is better when you frequently access one field across many elements (common in market data processing -- e.g., scan all prices to find the best). AoS is better when you always access all fields of one element together.

### 3. I/O Optimization

**Kernel Bypass**

Standard network I/O goes through the kernel:
```
NIC -> Kernel (interrupt, copy to socket buffer) -> User space (syscall to read)
```

Each transition costs microseconds. Kernel bypass eliminates the kernel from the data path:

```
Standard path:
  NIC ──> Kernel ──> Socket Buffer ──> read() syscall ──> User App
  ~5-15 us total

Kernel bypass (DPDK / ef_vi / Solarflare OpenOnload):
  NIC ──> User-space memory (via DMA) ──> User App
  ~1-2 us total
```

**DPDK (Data Plane Development Kit)**: Polls the NIC directly from user space using a dedicated CPU core. No interrupts, no kernel involvement. Used widely in network-intensive applications.

**ef_vi / OpenOnload**: Solarflare-specific kernel bypass. OpenOnload is a user-space TCP/IP stack that intercepts socket calls and handles them without entering the kernel. ef_vi provides raw access to the NIC for custom protocol handling.

**Busy Polling**

Instead of blocking on a syscall (`read()`, `epoll_wait()`), the application continuously polls for new data:

```cpp
while (true) {
    // Busy poll: check for data without blocking
    int n = ef_vi_receive(&vi, &event);
    if (n > 0) {
        process(event);
    }
    // No sleep, no yield -- burn the CPU core
}
```

This uses 100% of a CPU core but eliminates the latency of waking up from a blocked state (context switch, interrupt handling). In trading systems, dedicating a core to busy-polling the market data NIC is standard practice.

**Zero-Copy**

Standard I/O copies data multiple times:
1. NIC DMA to kernel buffer
2. Kernel buffer to user-space buffer (read syscall)
3. User-space processing
4. User-space buffer to kernel buffer (write syscall)
5. Kernel buffer to NIC DMA

Zero-copy techniques eliminate some or all of these copies:
- `sendfile()`: Copies directly from file descriptor to socket in kernel space (skips user-space copy).
- `splice()`: Moves data between file descriptors without copying through user space.
- Memory-mapped I/O (`mmap`): Maps a file or device into user address space.
- DPDK: NIC DMAs directly into user-space memory -- zero copies in the receive path.

### 4. Single-Threaded Event Loops vs Multi-Threaded

**Why Trading Systems Are Often Single-Threaded**

This is counterintuitive -- modern CPUs have many cores, so why not use them all? The reasons are fundamental:

1. **No locks**: Locks add latency (even uncontended locks require atomic operations ~10-25ns) and introduce unpredictable latency spikes when contended. A single-threaded system never waits for a lock.

2. **No cache thrashing**: When multiple threads share data, the CPU cache coherency protocol (MESI/MOESI) forces cache line bouncing between cores. Writing to shared data invalidates the cache line on all other cores, causing misses.

3. **Deterministic execution**: The same sequence of market data events always produces the same sequence of orders. This makes testing, debugging, and replay trivial.

4. **Sequential consistency**: No need to reason about memory ordering, happens-before relationships, or memory barriers.

**The Event Loop Pattern**

```
+---------------------------------------------------+
|                  Event Loop                        |
|                                                    |
|  1. Poll NIC for market data (busy poll)           |
|  2. Decode + normalize message                     |
|  3. Update order book                              |
|  4. Run strategy logic                             |
|  5. Risk check                                     |
|  6. Encode + send order                            |
|  7. Process any execution reports                   |
|  8. Go to 1                                        |
|                                                    |
|  All on ONE core. No context switches.             |
|  No locks. No cache invalidation.                  |
+---------------------------------------------------+
```

**When to Use Multiple Threads**

Multi-threading is used for components that are NOT on the critical path:
- Logging (write to disk asynchronously)
- Risk monitoring / surveillance (can lag by milliseconds)
- Position reconciliation
- Connectivity management (heartbeats, session management)

The pattern: single-threaded hot path, multi-threaded cold path, with lock-free queues (e.g., SPSC ring buffer) connecting them.

```
                  +----> [Logger Thread]     (cold path)
                  |
[Hot Path Core] --+----> [Risk Monitor]      (cold path)
  (single thread) |
                  +----> [Connectivity Mgr]  (cold path)

  Connected via lock-free SPSC ring buffers
```

### 5. Hot Path / Cold Path Separation

The hot path is the minimal set of operations between "market data arrives" and "order is sent." Everything else is the cold path.

**Design Principle**: Move everything possible off the hot path.

```
HOT PATH (microsecond budget):           COLD PATH (millisecond budget):
  - Decode market data                     - Logging
  - Update book                            - Metrics collection
  - Strategy signal generation             - Position reconciliation
  - Risk check (pre-computed limits)       - Configuration updates
  - Order encoding                         - Heartbeat management
  - NIC transmit                           - P&L calculation display
                                           - Alert generation
```

**Techniques for separation**:
- **Async logging**: Write log entries to a lock-free ring buffer; a background thread drains it to disk.
- **Snapshot-based monitoring**: Cold path periodically takes a snapshot of hot path state, rather than hot path pushing every update.
- **Configuration reload**: Hot path reads config from a struct in shared memory. Cold path writes new config and atomically flips a pointer.

### 6. Batching vs Streaming

**Streaming**: Process each event individually as it arrives.
- Lowest latency for individual events.
- Higher per-event overhead (function call, cache warming, etc.).

**Batching**: Collect multiple events, process them together.
- Higher latency for individual events (must wait for batch to fill or timeout).
- Lower per-event overhead (amortize function call, better cache utilization, SIMD opportunities).

**In Trading**:
- Market data processing is streaming -- you want the lowest latency for each update.
- Logging is batched -- buffer log entries and write them together.
- Risk reporting is batched -- aggregate position changes and send periodic snapshots.
- Order submission is streaming -- each order is sent immediately.

The decision depends on whether the consumer is latency-sensitive or throughput-sensitive.

### 7. Time and Measurement

**Why Accurate Time Matters**

In trading, timestamps are used for:
- Measuring system latency (how fast are we?)
- Regulatory compliance (MiFID II requires microsecond timestamps)
- Event ordering (which event happened first?)
- Detecting stale data (is this market data still fresh?)

**Clock Sources**

```
Source               Resolution    Accuracy      Cost
─────────────────────────────────────────────────────────
System clock         ~1 us        ~1 ms         Free
NTP-synced clock     ~1 us        ~1 ms         Free
PTP-synced clock     ~1 ns        ~100 ns       Moderate
NIC hardware TS      ~1 ns        ~10 ns        High
GPS-disciplined      ~1 ns        ~10 ns        High
```

**PTP (Precision Time Protocol)**

PTP (IEEE 1588) synchronizes clocks across a network to nanosecond accuracy. It works by exchanging timestamps between a grandmaster clock (often GPS-disciplined) and slave clocks, measuring and compensating for network delay.

Trading systems use PTP-capable NICs that can stamp packets at the hardware level -- the timestamp reflects exactly when the packet's first bit crossed the wire, not when software processed it.

**Wire-to-Wire Latency**

```
                    Wire-to-wire latency
    <─────────────────────────────────────────>
    │                                         │
  NIC RX          Application              NIC TX
  timestamp       processing               timestamp
    │                                         │
    │<── RX overhead ──>│<── app ──>│<── TX ──>│
    │                   │           │          │
    │<── application latency ──────>│          │
```

- **Wire-to-wire latency**: Time from packet arriving at NIC to response packet leaving NIC. This is what matters competitively.
- **Application latency**: Time from when userspace code gets the data to when it hands the response to the NIC driver. This is what you can optimize in software.
- The difference is NIC/driver overhead, which kernel bypass minimizes.

**Measurement Best Practices**

- Use `rdtsc` (Read Time Stamp Counter) on x86 for nanosecond-resolution timing within a process. It reads the CPU's cycle counter directly (no syscall).
- Use `clock_gettime(CLOCK_MONOTONIC)` for portable high-resolution timing.
- Never use `gettimeofday()` -- it is affected by NTP adjustments and can jump backwards.
- Measure in percentiles (p50, p99, p999), not averages. Averages hide tail latency.
- Log latency histograms (e.g., HDR Histogram) rather than individual samples.

```cpp
// rdtsc-based timing
inline uint64_t rdtsc() {
    uint32_t lo, hi;
    asm volatile("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}

uint64_t start = rdtsc();
// ... hot path code ...
uint64_t end = rdtsc();
uint64_t cycles = end - start;
double ns = cycles / (cpu_freq_ghz);  // convert to nanoseconds
```

### Summary: The Low-Latency Checklist

```
Memory:
  [ ] No allocations on hot path
  [ ] Object pools for reusable structures
  [ ] Pre-allocated buffers at startup
  [ ] Off-heap or custom allocators if using managed language

Data Structures:
  [ ] Arrays over linked lists
  [ ] Open-addressing hash maps
  [ ] SoA layout for columnar access patterns
  [ ] Cache-line-aligned critical structures

I/O:
  [ ] Kernel bypass for network I/O
  [ ] Busy polling on dedicated cores
  [ ] Zero-copy where possible

Threading:
  [ ] Single-threaded hot path
  [ ] Lock-free queues to cold path threads
  [ ] No shared mutable state on hot path

Architecture:
  [ ] Hot path / cold path separation
  [ ] Streaming for latency-sensitive, batching for throughput-sensitive
  [ ] Core pinning + CPU isolation for hot path threads

Time:
  [ ] PTP-synchronized clocks
  [ ] NIC hardware timestamps
  [ ] Percentile-based latency measurement
```

---

## Practice Questions (20-30 min)

1. **You are designing a market data processing pipeline in Java. How do you minimize GC impact?** Discuss object pooling, pre-allocation, off-heap storage, and GC tuning. When would you switch to C++?

2. **Explain why a std::unordered_map is a poor choice for a latency-critical lookup table. What would you use instead and why?**

3. **Draw the data flow from a market data packet arriving at the NIC to a strategy decision being made, comparing kernel networking vs kernel bypass.** Label where time is spent.

4. **Why are single-threaded event loops preferred over multi-threaded architectures for trading hot paths?** Discuss locks, cache coherency, and determinism.

5. **You need to send log entries from the hot path to a logging thread. Design the communication mechanism.** What data structure do you use? Why?

6. **Explain the difference between AoS and SoA layouts. Give a concrete trading example where SoA is better and one where AoS is better.**

7. **Your trading system's p50 latency is 2us but p99 is 50us. What are the likely causes of the tail latency?** How would you investigate and fix it?

8. **Describe how PTP works at a high level and why it matters for a trading firm. What happens if your clock is wrong by 1 millisecond?**

9. **You are given a CPU core dedicated to your trading application. How do you ensure nothing else runs on that core?** Discuss CPU isolation, core pinning, and interrupt steering.

10. **Compare busy polling vs interrupt-driven I/O. When is each appropriate?**

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** What is the approximate latency cost of an L1 cache miss that hits main memory?
- A) 1 nanosecond
- B) 10 nanoseconds
- C) 100 nanoseconds
- D) 1 microsecond

**Q2.** Why do low-latency trading systems use busy polling instead of epoll/select?
- A) Busy polling uses less CPU
- B) Busy polling avoids the latency of waking up from a blocked state
- C) Busy polling is more portable across operating systems
- D) Busy polling handles more connections simultaneously

**Q3.** What is the primary benefit of kernel bypass (DPDK/ef_vi)?
- A) Increased network bandwidth
- B) Elimination of kernel-to-userspace data copy and context switch latency
- C) Better security through isolation
- D) Automatic packet retransmission

**Q4.** In a Struct-of-Arrays (SoA) layout, what is the main advantage over Array-of-Structs (AoS)?
- A) Simpler code
- B) Better cache utilization when accessing a single field across many elements
- C) Lower memory usage
- D) Thread safety

**Q5.** Why is -Xms set equal to -Xmx in latency-sensitive Java applications?
- A) To reduce startup time
- B) To prevent heap resizing during operation, which causes GC pauses
- C) To increase maximum throughput
- D) To enable off-heap storage

**Q6.** What is the purpose of `rdtsc` in latency measurement?
- A) It reads the current wall clock time
- B) It reads the CPU's cycle counter for nanosecond-resolution timing without a syscall
- C) It synchronizes clocks across machines
- D) It measures network round-trip time

**Q7.** Why do trading systems prefer open-addressing hash maps over chained hash maps?
- A) Open-addressing has better worst-case complexity
- B) Open-addressing stores entries contiguously, avoiding pointer chasing and cache misses
- C) Open-addressing supports more concurrent readers
- D) Open-addressing uses less memory

**Q8.** What connects the hot path to cold path threads in a well-designed trading system?
- A) Shared mutex-protected data structures
- B) Database writes
- C) Lock-free SPSC ring buffers
- D) TCP sockets

**Q9.** Which statement about PTP (Precision Time Protocol) is correct?
- A) PTP provides millisecond accuracy
- B) PTP requires GPS on every machine
- C) PTP can achieve sub-microsecond clock synchronization across a network
- D) PTP is only used for regulatory compliance

### Short Answer

**Q10.** Explain why even an uncontended mutex can add ~25ns of latency and why this matters in a trading system with a 2-3us total latency budget.

**Q11.** What is "cache line bouncing" and how does it occur in multi-threaded trading systems?

**Q12.** Describe the trade-off between batching and streaming in the context of market data processing. Which does a latency-sensitive system prefer and why?

**Q13.** Your application has a 2us latency budget. You add a feature that calls `malloc()` on the hot path. Why is this dangerous?

**Q14.** What is the AlwaysPreTouch JVM flag and why is it used in trading systems?

**Q15.** Explain why you would measure latency in percentiles (p50, p99, p999) rather than averages.

**Q16.** A colleague suggests using a `ConcurrentHashMap` on the hot path for sharing state between the strategy thread and the risk thread. What is wrong with this suggestion and what would you propose instead?

---

## Quiz Answer Key

**Q1.** C) 100 nanoseconds. L1 hit is ~1ns, L2 ~4ns, L3 ~10ns, main memory ~100ns. This 100x difference between L1 and main memory is why cache-friendly data structures are critical.

**Q2.** B) Busy polling avoids the latency of waking up from a blocked state. When a thread blocks on epoll, the kernel must wake it up via an interrupt and context switch when data arrives, adding microseconds of latency. Busy polling continuously checks, so data is processed immediately.

**Q3.** B) Elimination of kernel-to-userspace data copy and context switch latency. Standard networking requires the kernel to copy data from NIC to kernel buffer to user buffer, with syscalls at each transition. Kernel bypass lets the NIC DMA directly into user-space memory.

**Q4.** B) Better cache utilization when accessing a single field across many elements. If you need to scan all prices in a collection of orders, SoA stores all prices contiguously. AoS interleaves prices with other fields, wasting cache bandwidth loading unwanted data.

**Q5.** B) To prevent heap resizing during operation, which causes GC pauses. When the JVM needs to grow the heap, it must pause all threads to resize. Setting Xms = Xmx allocates the full heap at startup.

**Q6.** B) It reads the CPU's cycle counter for nanosecond-resolution timing without a syscall. `rdtsc` is a single CPU instruction that reads the time stamp counter register. No kernel transition required, so it adds ~20-30 cycles of overhead rather than the ~100+ cycles of a syscall.

**Q7.** B) Open-addressing stores entries contiguously, avoiding pointer chasing and cache misses. Chained hash maps follow pointers to linked list nodes scattered in memory. Open-addressing probes within a contiguous array, which benefits from prefetching.

**Q8.** C) Lock-free SPSC (Single Producer, Single Consumer) ring buffers. These allow the hot path thread to publish data to cold path threads without any locks, atomic operations on the critical path (beyond a store-release on the write index), or syscalls.

**Q9.** C) PTP can achieve sub-microsecond clock synchronization across a network. With PTP-capable network switches and NICs, synchronization to ~100ns or better is achievable. It does not require GPS on every machine -- only the grandmaster clock needs a GPS reference.

**Q10.** A mutex, even when uncontended, requires an atomic compare-and-swap (CAS) instruction to acquire and a store-release to release. The CAS instruction forces a memory barrier, which serializes memory accesses and can stall the CPU pipeline. At ~25ns per lock/unlock, this is ~1% of a 2-3us budget per lock acquisition. If the hot path touches 5-10 locks, that is 250-500ns -- up to 25% of the budget spent just on synchronization.

**Q11.** Cache line bouncing occurs when two or more cores write to the same cache line. The CPU's coherency protocol (MESI) forces the cache line to be invalidated on all other cores after each write, bouncing ownership back and forth. Even if the cores are writing to different variables, if those variables share a cache line (false sharing), the bouncing still occurs. Fix: pad structures to cache line boundaries (64 bytes) and avoid shared mutable state.

**Q12.** Batching collects multiple events and processes them together, which amortizes overhead but adds latency (waiting for the batch to fill). Streaming processes each event individually for minimum per-event latency. A latency-sensitive market data system uses streaming because you want to react to each price update immediately -- waiting 100us to batch 10 updates means you are 100us late on the first one.

**Q13.** `malloc()` acquires a global lock in many implementations (e.g., glibc's ptmalloc). Even without contention, the lock acquisition and the allocator's bookkeeping (searching free lists, coalescing blocks) can take 50-500ns -- a significant fraction of the 2us budget. Worse, `malloc` can trigger an `mmap` or `sbrk` syscall to request memory from the OS, which takes microseconds. On the hot path, all memory should be pre-allocated.

**Q14.** AlwaysPreTouch causes the JVM to touch (write to) every page of the heap at startup, forcing the OS to allocate physical memory pages. Without it, the OS uses demand paging -- physical pages are only allocated on first access, causing a page fault (~1-10us each). These page faults on the hot path would cause unpredictable latency spikes.

**Q15.** Averages hide the distribution. A system with p50=2us and p99=50us has an average of maybe 3us, which looks great. But 1 in 100 events takes 50us -- unacceptable for trading. Percentiles reveal tail latency, which is often where problems hide (GC pauses, page faults, interrupt interference). P999 is particularly important because a system processing 100,000 events/second will hit p999 latency 100 times per second.

**Q16.** `ConcurrentHashMap` uses locks internally (striped locking or CAS operations). Any shared mutable data structure on the hot path introduces contention risk, cache line bouncing, and non-deterministic latency. Better approach: the strategy thread publishes decisions to a lock-free SPSC ring buffer. The risk thread reads from the buffer and maintains its own private copy of the state. No shared mutable state, no locks, no cache invalidation on the hot path.
