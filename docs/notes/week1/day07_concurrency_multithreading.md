# Day 7 (Wed Apr 15) — Concurrency & Multithreading

## Overview (5 min)

Concurrency is at the heart of trading systems. A single execution service simultaneously: receives market data from multiple exchanges, evaluates trading strategies, sends and manages orders, monitors risk, and reports to downstream systems. All of this happens under extreme latency constraints where a poorly placed lock can cost millions. Jump Trading interviews heavily test your understanding of thread safety, synchronization primitives, lock-free data structures, and concurrent patterns. This session goes deep into the theory and practice of concurrent programming.

---

## Reading Materials (60-90 min)

### 1. Thread Safety Fundamentals

A program is **thread-safe** if it behaves correctly when accessed from multiple threads simultaneously, without requiring external synchronization by the caller.

#### Race Conditions

A **race condition** occurs when the program's outcome depends on the relative timing of thread operations. The classic example:

```python
balance = 1000

# Thread A                    # Thread B
temp = balance    # 1000      temp = balance    # 1000
temp = temp - 200             temp = temp - 300
balance = temp    # 800       balance = temp    # 700
# Expected: 500. Actual: 700 or 800 (whoever writes last "wins")
```

The problem: `balance -= 200` is not atomic. It's three operations (read, modify, write), and another thread can interleave between them.

**Data race** (more precise): Two threads access the same memory location, at least one is a write, and they are not ordered by synchronization. Data races cause **undefined behavior** in C/C++ — the compiler and hardware can reorder or optimize away accesses in surprising ways.

#### Critical Sections

A **critical section** is a code region that accesses shared resources and must not be executed by more than one thread simultaneously.

```python
import threading

lock = threading.Lock()
balance = 1000

def withdraw(amount):
    global balance
    with lock:  # Critical section begins
        if balance >= amount:
            balance -= amount
            return True
        return False
    # Critical section ends
```

#### Deadlock

**Deadlock** occurs when two or more threads are blocked forever, each waiting for a resource held by another.

```
Thread A:                     Thread B:
  lock(resource_1)              lock(resource_2)
  lock(resource_2)  # BLOCKED   lock(resource_1)  # BLOCKED
  # Deadlock!
```

#### The Four Coffman Conditions

All four must hold simultaneously for deadlock to occur:

1. **Mutual exclusion:** At least one resource is non-shareable (only one thread can hold it)
2. **Hold and wait:** A thread holds one resource while waiting for another
3. **No preemption:** Resources cannot be forcibly taken from a thread
4. **Circular wait:** A circular chain of threads, each waiting for a resource held by the next

**Breaking any one condition prevents deadlock:**
- **Break mutual exclusion:** Use lock-free data structures
- **Break hold and wait:** Acquire all locks at once (atomically) or release all before requesting new ones
- **Break no preemption:** Use trylock with timeout — release all locks and retry if acquisition fails
- **Break circular wait:** Impose a global ordering on locks — always acquire in the same order

```python
# Lock ordering prevents deadlock
# Always acquire lock_a before lock_b
def transfer(from_acct, to_acct, amount):
    # Order locks by account ID to prevent deadlock
    first, second = sorted([from_acct, to_acct], key=lambda a: a.id)
    with first.lock:
        with second.lock:
            from_acct.balance -= amount
            to_acct.balance += amount
```

**Trading context:** A deadlock in a trading system is catastrophic. If the order router deadlocks, orders can't be sent or cancelled. Risk management can't update limits. Markets move and you can't respond. Prevention through design (lock ordering, lock-free structures) is far better than detection and recovery.

### 2. Synchronization Primitives

#### Mutex (Mutual Exclusion Lock)

The most basic synchronization primitive. At most one thread can hold the mutex at a time. Others block until it's released.

```python
import threading

mutex = threading.Lock()

def critical_operation():
    mutex.acquire()
    try:
        # Only one thread executes this at a time
        modify_shared_state()
    finally:
        mutex.release()

# Better: use context manager
with mutex:
    modify_shared_state()
```

**Reentrant mutex (RLock):** Can be acquired multiple times by the same thread without deadlocking. Must be released the same number of times.

```python
rlock = threading.RLock()

def outer():
    with rlock:
        inner()  # Doesn't deadlock — same thread can reacquire

def inner():
    with rlock:
        do_work()
```

#### Semaphore

A semaphore maintains a counter. `acquire()` decrements; if zero, the thread blocks. `release()` increments and wakes a blocked thread. A semaphore with count 1 behaves like a mutex, but semantically they're different — any thread can release a semaphore (not just the one that acquired it).

```python
# Limit concurrent database connections
db_semaphore = threading.Semaphore(10)  # Max 10 connections

def query_database(sql):
    with db_semaphore:  # Blocks if 10 threads already inside
        conn = get_connection()
        result = conn.execute(sql)
        return result
```

**Trading use case:** Rate limiting — some exchanges limit the number of concurrent requests. A semaphore enforces this naturally.

#### Condition Variable

A condition variable lets threads wait for a specific condition to become true. It's always used with a mutex.

```python
import threading

class OrderQueue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)

    def put(self, order):
        with self.not_empty:
            self.queue.append(order)
            self.not_empty.notify()  # Wake one waiting consumer

    def get(self):
        with self.not_empty:
            while not self.queue:  # WHILE, not IF — spurious wakeups!
                self.not_empty.wait()  # Release lock and sleep atomically
            return self.queue.pop(0)
```

**Critical detail:** Always use `while`, not `if`, for the condition check. **Spurious wakeups** can occur (the thread wakes without `notify` being called), so you must re-check the condition.

**Why `wait()` is atomic:** `wait()` releases the lock and suspends the thread as a single atomic operation. If these were separate, another thread could sneak in between (notify after lock release but before sleep — the notification would be lost).

#### Read-Write Lock

Allows multiple concurrent readers OR one exclusive writer. Useful when reads vastly outnumber writes.

```python
import threading

class ReadWriteLock:
    def __init__(self):
        self.readers = 0
        self.lock = threading.Lock()
        self.write_lock = threading.Lock()

    def acquire_read(self):
        with self.lock:
            self.readers += 1
            if self.readers == 1:
                self.write_lock.acquire()

    def release_read(self):
        with self.lock:
            self.readers -= 1
            if self.readers == 0:
                self.write_lock.release()

    def acquire_write(self):
        self.write_lock.acquire()

    def release_write(self):
        self.write_lock.release()
```

**Trading use case:** The order book is read by many strategy threads but written by one market data handler. A read-write lock allows concurrent reads without blocking.

**Caveat:** Writer starvation — if readers keep arriving, the writer may never get access. Solutions: write-preferring RW locks, or timeouts.

### 3. Lock-Free Programming

Lock-free data structures guarantee system-wide progress — at least one thread makes progress in a finite number of steps, even if other threads are suspended. They avoid the problems of locks: deadlock, priority inversion, convoying.

#### CAS (Compare-and-Swap)

The fundamental building block of lock-free programming. CAS atomically: reads a memory location, compares it to an expected value, and if they match, writes a new value.

```c
// Pseudocode
bool CAS(int *addr, int expected, int desired) {
    // Atomic — implemented as a single CPU instruction (CMPXCHG on x86)
    if (*addr == expected) {
        *addr = desired;
        return true;
    }
    return false;
}
```

**Lock-free counter using CAS:**
```python
import ctypes
import threading

class AtomicCounter:
    """Simplified illustration (Python doesn't have true CAS)."""
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()  # Simulating CAS

    def increment(self):
        while True:
            old = self.value
            # CAS: if value is still old, set to old+1
            if self._cas(old, old + 1):
                return old + 1

    def _cas(self, expected, desired):
        with self.lock:  # Real CAS is a CPU instruction, no lock needed
            if self.value == expected:
                self.value = desired
                return True
            return False
```

In C/C++, CAS maps to hardware instructions:
```c
#include <stdatomic.h>

atomic_int counter = 0;

void increment() {
    int old;
    do {
        old = atomic_load(&counter);
    } while (!atomic_compare_exchange_weak(&counter, &old, old + 1));
}
```

#### Atomic Operations

Modern CPUs provide atomic read-modify-write operations:
- **atomic_load / atomic_store:** Read/write with memory ordering guarantees
- **atomic_fetch_add:** Atomically add (useful for counters)
- **atomic_compare_exchange (CAS):** The universal building block

In Python, operations on simple types under the GIL are effectively atomic (single bytecode instruction), but this is an implementation detail, not a guarantee.

```python
# In C++
std::atomic<int> sequence_number{0};
int next_seq = sequence_number.fetch_add(1, std::memory_order_relaxed);
```

#### Memory Ordering

Modern CPUs and compilers reorder memory operations for performance. This is invisible to single-threaded code but breaks multi-threaded assumptions.

```
Thread A:                Thread B:
  data = 42               while (!ready) {}
  ready = true             print(data)   // Might print 0!
```

Without proper memory ordering, Thread B might see `ready = true` before `data = 42` due to store buffer reordering.

**Memory order levels (C++ memory model):**

| Order | Guarantee | Cost |
|---|---|---|
| `relaxed` | Only atomicity, no ordering | Cheapest |
| `acquire` | No reads/writes after this can move before it | Moderate |
| `release` | No reads/writes before this can move after it | Moderate |
| `acq_rel` | Both acquire and release | Higher |
| `seq_cst` | Total global ordering of all seq_cst operations | Most expensive |

**The acquire-release pattern:**
```c
// Thread A (producer)
data = 42;                            // Store data
flag.store(true, memory_order_release);  // Release: all prior writes visible

// Thread B (consumer)
while (!flag.load(memory_order_acquire)) {}  // Acquire: sees all writes before release
assert(data == 42);  // Guaranteed!
```

**Trading context:** Lock-free queues between the market data thread and the strategy thread use acquire-release semantics to ensure that when the strategy reads a price update, all related fields (price, size, timestamp) are visible and consistent.

#### The ABA Problem

ABA occurs in lock-free algorithms using CAS: a value changes from A to B and back to A. The CAS succeeds (it sees A as expected) even though the value was modified.

**Example with a lock-free stack:**
```
Initial stack: A -> B -> C

Thread 1: reads top = A, prepares to CAS(top, A, B) [pop A]
Thread 1: suspended

Thread 2: pops A, pops B, pushes new D, pushes A back
Stack: A -> D -> C  (B is gone, A is recycled)

Thread 1: resumes, CAS(top, A, B) succeeds! (top was A)
But B no longer exists in the stack. Corruption!
```

**Solutions:**
- **Tagged pointers:** Add a version counter to the pointer. CAS checks both pointer and version. ABA would need the same pointer AND same version, which the counter prevents.
- **Hazard pointers:** Threads publish pointers they're accessing. Memory isn't reclaimed while any thread has a hazard pointer to it.
- **Epoch-based reclamation:** Track "epochs" and only reclaim memory after all threads have advanced past the epoch in which it was freed.

### 4. Producer-Consumer Pattern

The producer-consumer pattern decouples data production from consumption using a shared buffer.

#### Ring Buffer (Circular Buffer)

A ring buffer is a fixed-size array with head (read) and tail (write) pointers that wrap around. It's the workhorse of trading systems for passing data between threads.

```
Buffer: [_][_][data][data][data][_][_][_]
              ^                 ^
              head (read)       tail (write)

After wrapping:
Buffer: [data][data][_][_][_][data][data][data]
                     ^       ^
                     head    tail
```

```python
class RingBuffer:
    def __init__(self, capacity):
        self.buffer = [None] * capacity
        self.capacity = capacity
        self.head = 0  # Read position
        self.tail = 0  # Write position
        self.size = 0
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    def put(self, item):
        with self.not_full:
            while self.size == self.capacity:
                self.not_full.wait()
            self.buffer[self.tail] = item
            self.tail = (self.tail + 1) % self.capacity
            self.size += 1
            self.not_empty.notify()

    def get(self):
        with self.not_empty:
            while self.size == 0:
                self.not_empty.wait()
            item = self.buffer[self.head]
            self.head = (self.head + 1) % self.capacity
            self.size -= 1
            self.not_full.notify()
            return item
```

**Lock-free ring buffer (single producer, single consumer — SPSC):**

When there's exactly one producer and one consumer, the ring buffer can be lock-free:

```c
// C pseudocode
struct SPSCQueue {
    T buffer[CAPACITY];
    atomic<size_t> head;  // Consumer reads from head
    atomic<size_t> tail;  // Producer writes to tail
};

void produce(T item) {
    size_t t = tail.load(relaxed);
    size_t next = (t + 1) % CAPACITY;
    while (next == head.load(acquire)) {}  // Spin until not full
    buffer[t] = item;
    tail.store(next, release);  // Publish new tail
}

T consume() {
    size_t h = head.load(relaxed);
    while (h == tail.load(acquire)) {}  // Spin until not empty
    T item = buffer[h];
    head.store((h + 1) % CAPACITY, release);
    return item;
}
```

**Why SPSC doesn't need locks:** Only one thread writes `tail`, only one thread writes `head`. No conflicting writes means no CAS needed — just atomic loads/stores with proper memory ordering.

**Trading context:** The market data handler (producer) writes ticks into a ring buffer. The strategy engine (consumer) reads ticks from it. This is the single most common concurrency pattern in trading. Ring buffers are preferred because:
- Fixed size — no allocation on the hot path
- Cache-friendly — contiguous memory
- Lock-free for SPSC — no contention overhead
- Bounded — natural back-pressure (producer waits when full)

### 5. Thread Pools and Work Queues

A **thread pool** maintains a set of pre-created threads that pull tasks from a shared work queue. This avoids the overhead of thread creation/destruction per task.

```python
from concurrent.futures import ThreadPoolExecutor

def process_order(order):
    validate(order)
    send_to_exchange(order)

# Create a pool of 8 threads
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(process_order, order) for order in orders]
    for future in futures:
        result = future.result()  # Block until complete
```

**Work stealing:** Some thread pool implementations (Java ForkJoinPool, Intel TBB) use work stealing — idle threads "steal" tasks from busy threads' local queues. This balances load automatically.

### 6. Python Concurrency

#### GIL Implications Revisited

The GIL means:
- Only one thread executes Python bytecode at a time
- CPU-bound multithreading is essentially serial
- I/O-bound multithreading works because the GIL is released during I/O
- C extensions (NumPy, ctypes) can release the GIL for compute-heavy sections

#### threading Module

```python
import threading

class MarketDataProcessor(threading.Thread):
    def __init__(self, exchange):
        super().__init__(daemon=True)
        self.exchange = exchange
        self.running = True

    def run(self):
        while self.running:
            data = self.exchange.recv()  # GIL released during I/O
            self.process(data)

    def stop(self):
        self.running = False
```

**Thread-local storage:** When each thread needs its own copy of data:
```python
local_data = threading.local()

def process_request(request):
    local_data.connection = get_connection()  # Each thread gets its own
    local_data.connection.execute(request)
```

#### multiprocessing Module

```python
from multiprocessing import Process, Queue, shared_memory
import numpy as np

def risk_calculator(shm_name, shape, dtype, result_queue):
    """Runs in a separate process — has its own GIL."""
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    positions = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    var = compute_var(positions)
    result_queue.put(var)
    existing_shm.close()

# Main process
positions = np.array([...])  # Large position matrix
shm = shared_memory.SharedMemory(create=True, size=positions.nbytes)
shared_positions = np.ndarray(positions.shape, dtype=positions.dtype, buffer=shm.buf)
np.copyto(shared_positions, positions)

q = Queue()
p = Process(target=risk_calculator,
            args=(shm.name, positions.shape, positions.dtype, q))
p.start()
var = q.get()
p.join()
shm.close()
shm.unlink()
```

#### asyncio Event Loop

asyncio provides cooperative multitasking. A single thread runs an event loop that schedules coroutines.

```python
import asyncio

class FIXSession:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.seq_num = 1

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port)
        await self.send_logon()

    async def send_logon(self):
        msg = self.build_message("A", {"108": "30"})
        self.writer.write(msg)
        await self.writer.drain()

    async def receive_messages(self):
        while True:
            data = await self.reader.readline()
            if not data:
                break
            await self.process_message(data)

async def main():
    sessions = [
        FIXSession("cme.example.com", 9823),
        FIXSession("ice.example.com", 9824),
        FIXSession("asx.example.com", 9825),
    ]

    for session in sessions:
        await session.connect()

    # All sessions receive concurrently (but single-threaded!)
    await asyncio.gather(*(s.receive_messages() for s in sessions))

asyncio.run(main())
```

**How asyncio is concurrent but single-threaded:** When a coroutine hits `await` on an I/O operation, it suspends and yields control back to the event loop. The event loop runs another ready coroutine. When the I/O completes, the original coroutine is resumed. No thread switching, no locks needed for coroutine-local data.

**Limitations:**
- CPU-bound work blocks the event loop — use `loop.run_in_executor()` to offload to a thread/process pool
- All libraries must be async-aware (can't use `requests`, must use `aiohttp`)
- Debugging is harder (stack traces cross async boundaries)

**When to choose asyncio for trading:**
- Many concurrent network connections (market data feeds, FIX sessions)
- I/O-heavy gateway/router applications
- When simplicity and determinism matter (single-threaded = no races)

### 7. Common Concurrency Patterns in Trading

```
                      +-----------------+
                      | Market Data     |
                      | Multicast Recv  |
                      +-------+---------+
                              |
                        [SPSC Ring Buffer]
                              |
                      +-------v---------+
                      | Strategy Engine |
                      | (CPU-pinned)    |
                      +-------+---------+
                              |
                        [SPSC Ring Buffer]
                              |
                      +-------v---------+
                      | Order Router    |
                      | (FIX session)   |
                      +-----------------+
```

Each component runs on a dedicated CPU core, communicating via lock-free ring buffers. No locks on the hot path. This is the "disruptor" pattern popularized by LMAX.

---

## Practice Questions (20-30 min)

1. **Explain the four Coffman conditions for deadlock. For each, describe a practical technique to break it in a trading system.**

2. **What is a race condition? Give a concrete example from a trading context (e.g., order state management). How would you prevent it?**

3. **Compare mutexes, semaphores, and condition variables. When would you use each?**

4. **Explain CAS (Compare-and-Swap). How is a lock-free counter implemented using CAS? What happens when two threads CAS simultaneously?**

5. **What is the ABA problem? Describe a scenario in a trading system where it could occur. How would tagged pointers solve it?**

6. **Design a lock-free SPSC ring buffer for passing market data ticks from a receiver thread to a processing thread. Explain the memory ordering requirements.**

7. **Explain memory ordering (relaxed, acquire, release, seq_cst). Why does the acquire-release pattern work for producer-consumer?**

8. **Your trading system has a thread for each of: market data, strategy, order routing, risk, and logging. Design the thread communication and synchronization architecture. Justify your choices.**

9. **Compare Python's threading, multiprocessing, and asyncio. You're building a FIX gateway that connects to 20 exchanges. Which would you choose and why?**

10. **What is priority inversion? How can it affect a real-time trading system? What solutions exist?**

---

## Quiz (20 questions)

### Multiple Choice

**Q1.** Which is NOT one of the four Coffman conditions for deadlock?
- (A) Mutual exclusion
- (B) Starvation
- (C) Hold and wait
- (D) Circular wait

**Q2.** A condition variable's `wait()` operation atomically:
- (A) Acquires the lock and sleeps
- (B) Releases the lock and sleeps
- (C) Checks the condition and sleeps
- (D) Notifies other threads and sleeps

**Q3.** CAS (Compare-and-Swap) is:
- (A) A software synchronization protocol
- (B) An atomic hardware instruction
- (C) A type of mutex
- (D) A deadlock detection algorithm

**Q4.** In a lock-free SPSC ring buffer, why are locks unnecessary?
- (A) The GIL provides synchronization
- (B) Only one thread writes each index (head or tail), eliminating conflicting writes
- (C) Ring buffers are inherently thread-safe
- (D) The buffer is too small for contention

**Q5.** The `memory_order_release` guarantees that:
- (A) All subsequent writes are visible to all threads
- (B) All prior writes by this thread are visible to a thread that performs an acquire on the same location
- (C) The operation is the last to complete
- (D) No other thread can access the variable

**Q6.** Which Python concurrency model bypasses the GIL for CPU-bound work?
- (A) threading
- (B) asyncio
- (C) multiprocessing
- (D) concurrent.futures.ThreadPoolExecutor

**Q7.** A read-write lock allows:
- (A) Multiple writers simultaneously
- (B) Multiple readers simultaneously but only one writer
- (C) Only one reader or writer at a time
- (D) Unlimited concurrent access

**Q8.** The ABA problem affects:
- (A) Mutex-based code
- (B) Lock-free algorithms using CAS
- (C) Condition variables
- (D) Semaphores

**Q9.** In the producer-consumer pattern, a ring buffer is preferred over a linked-list queue because:
- (A) It has O(log n) operations
- (B) It uses contiguous memory (cache-friendly) and avoids allocation on the hot path
- (C) It supports unlimited size
- (D) It's simpler to implement

**Q10.** `asyncio` achieves concurrency by:
- (A) Using multiple OS threads
- (B) Using multiple OS processes
- (C) Cooperative multitasking with an event loop on a single thread
- (D) Bypassing the GIL

**Q11.** Spurious wakeups mean that:
- (A) A thread wakes up from `wait()` without `notify()` being called
- (B) A thread is prevented from sleeping
- (C) Multiple threads are notified when only one should be
- (D) A thread deadlocks during wait

**Q12.** A thread pool avoids the overhead of:
- (A) Context switching
- (B) Thread creation and destruction per task
- (C) Memory allocation
- (D) Network I/O

### Short Answer

**Q13.** Explain why you must use `while` (not `if`) when checking a condition before `wait()` on a condition variable. Give a concrete example.

**Q14.** Describe the "disruptor" pattern used in LMAX-style trading systems. What makes it faster than traditional producer-consumer queues?

**Q15.** You have two threads that both need to lock resources A and B. Thread 1 locks A then B. Thread 2 locks B then A. How does deadlock occur? How do you fix it?

**Q16.** Explain priority inversion. Thread H (high priority) and Thread L (low priority) share a lock. Thread M (medium priority) arrives. What happens?

**Q17.** Compare `std::mutex` and `std::atomic<int>` in C++ for a simple counter increment. What are the performance implications?

**Q18.** Why does asyncio not need locks for coroutine-local data? Under what circumstances could you still have a race condition in asyncio code?

**Q19.** Design a bounded blocking queue using a mutex and two condition variables. Show the put() and get() operations.

**Q20.** A lock-free stack uses CAS to push and pop. Describe the push operation and explain how CAS ensures correctness even with concurrent access.

---

## Quiz Answer Key

**Q1: (B)** Starvation is not one of the four Coffman conditions. The four are: mutual exclusion, hold and wait, no preemption, and circular wait. Starvation is a related but separate liveness problem.

**Q2: (B)** `wait()` atomically releases the associated lock and suspends the thread. When notified (or spuriously woken), it re-acquires the lock before returning. The atomicity of release+sleep is critical — if they were separate, a notification between release and sleep would be lost.

**Q3: (B)** CAS is a single atomic CPU instruction (CMPXCHG on x86, LL/SC on ARM). It reads memory, compares to an expected value, and conditionally writes — all in one indivisible operation. This is the foundation of lock-free programming.

**Q4: (B)** In an SPSC queue, the producer only writes `tail` and the consumer only writes `head`. There are no conflicting writes to the same variable, so CAS and locks are unnecessary. Only atomic loads/stores with proper memory ordering are needed to ensure visibility.

**Q5: (B)** `memory_order_release` ensures that all writes performed by the releasing thread before the release store are visible to any thread that subsequently performs an `acquire` load on the same atomic variable. It creates a "happens-before" relationship.

**Q6: (C)** `multiprocessing` creates separate OS processes, each with its own Python interpreter and GIL. This is the standard way to achieve true CPU parallelism in Python.

**Q7: (B)** A read-write lock allows multiple readers to hold the lock simultaneously (reads don't conflict), but a writer needs exclusive access (no readers or other writers). This optimizes for read-heavy workloads.

**Q8: (B)** ABA specifically affects CAS-based lock-free algorithms. CAS checks if the value is still the expected value, but can't detect if it changed to something else and changed back. Mutex-based code doesn't use CAS and isn't affected.

**Q9: (B)** Ring buffers use a pre-allocated contiguous array — no memory allocation during operation (predictable latency) and excellent cache behavior (sequential access). Linked-list queues allocate a node per enqueue (allocation overhead, potential GC pressure) and have poor cache locality (nodes scattered in memory).

**Q10: (C)** asyncio uses a single thread running an event loop. Coroutines voluntarily yield control at `await` points. The event loop multiplexes I/O operations and resumes coroutines when their I/O completes. No OS threads or processes are involved in the concurrency.

**Q11: (A)** Spurious wakeups are a documented behavior of condition variables on most operating systems. A thread can return from `wait()` even without a corresponding `notify()`. This is why the condition must be checked in a `while` loop, not an `if` statement.

**Q12: (B)** Creating an OS thread costs ~100 microseconds and involves kernel calls. A thread pool creates threads once and reuses them, amortizing the creation cost. Tasks are submitted to a queue and executed by existing threads.

**Q13:** With `if`: Thread wakes up (possibly spuriously), assumes the condition is true, and proceeds — but the condition might have been consumed by another thread or never been true. With `while`: Thread re-checks the condition after waking. Example: Two consumer threads wait on `not_empty`. Producer adds one item and calls `notify_all()`. Both consumers wake up. The first one checks `while not queue: wait()` — queue has data, proceeds, takes the item. The second checks `while not queue: wait()` — queue is now empty, goes back to sleep. Without `while`, the second consumer would try to pop from an empty queue.

**Q14:** The LMAX Disruptor uses a pre-allocated ring buffer shared between producers and consumers. Key innovations: (1) Single-writer principle — each slot is written by exactly one thread, avoiding write contention. (2) Sequence barriers replace locks — producers and consumers track their position with atomic sequence counters. (3) Cache line padding prevents false sharing between sequence counters. (4) Batching — consumers process all available items before checking for more. Result: ~100ns latency for inter-thread message passing, vs ~1000ns for `ArrayBlockingQueue`.

**Q15:** Thread 1 acquires A, Thread 2 acquires B. Thread 1 tries to acquire B (blocked, held by Thread 2). Thread 2 tries to acquire A (blocked, held by Thread 1). Circular wait = deadlock. Fix: impose a global ordering — both threads must acquire A before B. Since both try A first, one succeeds and the other waits (no circularity).

**Q16:** Thread L holds the lock and is running. Thread H arrives, needs the lock, and blocks. Thread M arrives (doesn't need the lock) and preempts Thread L (higher priority). Thread H is now blocked by Thread L, which is blocked by Thread M. Effectively, medium-priority Thread M delays high-priority Thread H — inversion. Solutions: (a) **Priority inheritance** — when H blocks on L's lock, L temporarily inherits H's priority and preempts M. (b) **Priority ceiling** — the lock is assigned the priority of the highest-priority thread that might use it.

**Q17:** `std::mutex` involves a system call for contention (futex on Linux) — ~25ns uncontended, ~1000ns contended. `std::atomic<int>` with `fetch_add` is a single atomic instruction — ~5-10ns uncontended, ~50-100ns contended (cache line bouncing). For a simple counter, `atomic` is 5-10x faster. For complex critical sections, mutex is necessary (atomic operations only work on single variables).

**Q18:** asyncio is single-threaded — between any two `await` points, code runs without interruption. So coroutine-local data can't be modified by another coroutine between synchronous operations. However, race conditions CAN occur across `await` points: if you read a shared variable, `await` something, then write based on the old read, another coroutine might have modified the variable during the await. This is a logical race, not a data race.

**Q19:**
```python
class BoundedBlockingQueue:
    def __init__(self, capacity):
        self.queue = [None] * capacity
        self.capacity = capacity
        self.size = 0
        self.head = 0
        self.tail = 0
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    def put(self, item):
        with self.not_full:
            while self.size == self.capacity:
                self.not_full.wait()
            self.queue[self.tail] = item
            self.tail = (self.tail + 1) % self.capacity
            self.size += 1
            self.not_empty.notify()

    def get(self):
        with self.not_empty:
            while self.size == 0:
                self.not_empty.wait()
            item = self.queue[self.head]
            self.head = (self.head + 1) % self.capacity
            self.size -= 1
            self.not_full.notify()
            return item
```

**Q20:** Lock-free push:
```
1. Allocate new node, set node.data = value
2. Read current top: old_top = top.load()
3. Set node.next = old_top
4. CAS(top, old_top, node)
   - If top is still old_top, top is updated to node. Done.
   - If top changed (another thread pushed/popped), CAS fails.
     Go back to step 2 and retry.
```
CAS ensures correctness: only one thread's push succeeds per attempt. Failed threads retry with the updated top. No thread can corrupt the stack because the update is atomic — either the entire push happens or nothing changes. Progress is guaranteed because at least one thread succeeds per round of contention.
