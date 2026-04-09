# Day 1 (Thu Apr 9) — Python Internals & Language Mastery

## Overview (5 min)

Jump Trading's Futures Execution Services team uses Python extensively for trading infrastructure — order management systems, risk engines, market data processors, and strategy orchestration. While the hot path may be in C++, Python glues the system together and is often the first language you'll whiteboard in during interviews. Demonstrating deep knowledge of Python internals signals that you understand performance implications of your code — critical when milliseconds matter.

This session covers the CPython object model, data structure internals, the GIL, generators, decorators, context managers, memory management, and concurrency. These are the topics interviewers probe to distinguish engineers who merely write Python from those who truly understand it.

---

## Reading Materials (60-90 min)

### 1. The Object Model: Everything Is an Object

In CPython, every value — integers, strings, functions, classes, even `None` — is a `PyObject` on the heap. Each `PyObject` contains at minimum:

- A **reference count** (`ob_refcnt`)
- A **type pointer** (`ob_type`) pointing to the object's type

```python
x = 42
print(type(x))    # <class 'int'>
print(id(x))      # Memory address of the PyObject
```

**`id()`, `is`, and `==`**

`id(x)` returns the memory address of the object `x` points to. The `is` operator checks identity (same address), while `==` checks equality (calls `__eq__`).

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b   # True — same contents
a is b   # False — different objects in memory

c = a
a is c   # True — same object
```

CPython caches small integers (-5 to 256) and interned strings, so `is` may return `True` for small ints, but relying on this is a bug:

```python
x = 256
y = 256
x is y   # True (cached)

x = 257
y = 257
x is y   # False (not cached) — implementation detail, not guaranteed
```

**Mutability**

Mutable objects (lists, dicts, sets) can be modified in place. Immutable objects (ints, strings, tuples, frozensets) cannot — any "modification" creates a new object.

```python
s = "hello"
s[0] = "H"  # TypeError — strings are immutable

lst = [1, 2, 3]
lst[0] = 99  # Fine — lists are mutable
```

This distinction matters for trading systems: if you pass a mutable object to a function and it modifies it, you've introduced a side effect. In concurrent code, mutable shared state is the root of race conditions.

### 2. Data Structure Internals

#### dict — Hash Table with Open Addressing

Python's `dict` is implemented as a hash table using **open addressing** (specifically, a probing scheme). Since Python 3.7, dicts maintain insertion order (this was an implementation detail in 3.6, guaranteed in 3.7+).

The internal structure has two arrays:
1. A **compact hash table** (indices array) — sparse, stores indices into the entries array
2. A **dense entries array** — stores `(hash, key, value)` tuples in insertion order

When you insert a key:
1. Compute `hash(key)`
2. Use the hash to index into the sparse indices array
3. If the slot is empty, store the index of the new entry
4. If occupied (collision), probe for the next open slot using a perturbation scheme: `j = ((5 * j) + 1 + perturb) % table_size; perturb >>= 5`

This probing scheme is better than linear probing because it uses all bits of the hash, reducing clustering.

**Load factor**: When the table is 2/3 full, it resizes (typically doubles). This gives amortized O(1) for insertions.

**Why this matters for trading**: Order books, instrument lookups, and position maps are all dict-heavy. Understanding that dict operations are O(1) amortized but O(n) worst-case during resize helps you reason about latency spikes.

```python
# Dict comprehension — common in trading code
prices = {sym: get_price(sym) for sym in symbols}

# Avoid repeated lookups
pos = positions.get(symbol, 0)  # O(1) with default
```

#### list — Dynamic Array

A Python `list` is a contiguous array of pointers to `PyObject`s. It over-allocates to make `append()` amortized O(1):

- Growth pattern: 0, 4, 8, 16, 24, 32, 40, 52, 64, 76... (roughly 1.125x growth factor)
- `append()` is amortized O(1)
- `insert(0, x)` is O(n) — shifts everything
- `pop()` from end is O(1), `pop(0)` is O(n)
- Random access `lst[i]` is O(1)

For a FIFO queue in trading (e.g., order queue), don't use `list` — use `collections.deque` which is a doubly-linked list of fixed-size blocks, giving O(1) at both ends.

```python
from collections import deque
order_queue = deque(maxlen=10000)  # Bounded queue
order_queue.append(order)          # O(1)
order_queue.popleft()              # O(1)
```

#### set — Hash Set

A `set` is essentially a `dict` without values — same hash table, open addressing, same resize behavior. Membership testing is O(1) average.

```python
active_symbols = {"ESM5", "NQM5", "ZNM5"}
if symbol in active_symbols:  # O(1) average
    process(symbol)
```

#### tuple — Immutable Sequence

Tuples are fixed-size arrays of pointers. Being immutable, they:
- Can be hashed (if all elements are hashable), so they can be dict keys or set members
- Are slightly faster to create than lists (CPython caches small tuples)
- Use less memory than lists (no over-allocation)

```python
# Tuple as a composite key
order_key = (exchange, symbol, order_id)
orders[order_key] = order_details
```

### 3. The Global Interpreter Lock (GIL)

The GIL is a mutex in CPython that allows only one thread to execute Python bytecode at a time. It exists because CPython's memory management (reference counting) is not thread-safe.

**What the GIL means in practice:**
- CPU-bound Python code gets zero benefit from threading — threads take turns, so it's effectively single-threaded
- I/O-bound code benefits from threading because the GIL is released during I/O operations (network calls, file reads, `time.sleep()`)
- C extensions can explicitly release the GIL (NumPy does this for matrix operations)

**Why the GIL matters for trading:**
Trading systems are often I/O bound (waiting for market data, sending orders), so `threading` actually works well for network-heavy tasks. But for CPU-bound work like risk calculations, you need `multiprocessing` or C extensions.

```python
# GIL is released during I/O — threading works here
import threading

def fetch_market_data(exchange):
    data = socket.recv(4096)  # GIL released during recv
    process(data)

threads = [threading.Thread(target=fetch_market_data, args=(ex,)) for ex in exchanges]
```

**Python 3.13+ note:** PEP 703 introduces a "free-threaded" build of CPython (no GIL), but it's experimental and not yet the default.

### 4. Generators and Iterators

An **iterator** is any object implementing `__iter__()` and `__next__()`. A **generator** is a function that uses `yield` to produce values lazily.

```python
def price_stream(socket):
    """Generator that yields prices as they arrive."""
    buffer = b""
    while True:
        data = socket.recv(4096)
        if not data:
            return
        buffer += data
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            yield parse_price(line)

# Lazy evaluation — only processes one price at a time
for price in price_stream(mkt_data_socket):
    update_book(price)
```

**Generator internals:** When a generator hits `yield`, its stack frame is frozen — local variables, instruction pointer, and all. When `next()` is called, execution resumes exactly where it left off. This is why generators use O(1) memory regardless of how many values they produce.

**`yield from`** delegates to a sub-generator:

```python
def combined_feed(*sockets):
    for sock in sockets:
        yield from price_stream(sock)
```

**Generator expressions** are the lazy equivalent of list comprehensions:

```python
# List comprehension — creates entire list in memory
total = sum([trade.pnl for trade in trades])  # O(n) memory

# Generator expression — processes one at a time
total = sum(trade.pnl for trade in trades)     # O(1) memory
```

### 5. Decorators

A decorator is a function that takes a function (or class) and returns a modified version. They're syntactic sugar for `func = decorator(func)`.

```python
import functools
import time

def latency_monitor(func):
    """Decorator to measure function execution time — useful in trading."""
    @functools.wraps(func)  # Preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        result = func(*args, **kwargs)
        elapsed_ns = time.perf_counter_ns() - start
        if elapsed_ns > 1_000_000:  # Log if > 1ms
            logger.warning(f"{func.__name__} took {elapsed_ns/1e6:.2f}ms")
        return result
    return wrapper

@latency_monitor
def send_order(order):
    connection.send(order.encode())
```

**Decorators with arguments** require an extra level of nesting:

```python
def retry(max_attempts=3, delay_ms=100):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except ConnectionError:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay_ms / 1000)
        return wrapper
    return decorator

@retry(max_attempts=5, delay_ms=50)
def connect_to_exchange(addr):
    ...
```

**Class decorators** modify classes:

```python
@dataclass  # A class decorator from stdlib
class Order:
    symbol: str
    side: str
    quantity: int
    price: float
```

### 6. Context Managers

Context managers implement `__enter__` and `__exit__` to manage resource acquisition and release. The `with` statement guarantees cleanup even if exceptions occur.

```python
class DatabaseConnection:
    def __enter__(self):
        self.conn = connect_to_db()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        return False  # Don't suppress exceptions

with DatabaseConnection() as conn:
    conn.execute("SELECT * FROM positions")
```

The `contextlib` module provides shortcuts:

```python
from contextlib import contextmanager

@contextmanager
def order_lock(symbol):
    """Acquire a per-symbol lock for order modification."""
    lock = symbol_locks[symbol]
    lock.acquire()
    try:
        yield lock
    finally:
        lock.release()

with order_lock("ESM5"):
    modify_order(order_id, new_price)
```

**Trading relevance:** Context managers are essential for managing connections (FIX sessions, database connections), file handles (log files, market data recordings), and locks (order state modifications).

### 7. Memory Management

CPython uses a three-pronged approach:

#### Reference Counting

Every `PyObject` has a reference count. When it drops to zero, the object is immediately deallocated.

```python
import sys
a = [1, 2, 3]
print(sys.getrefcount(a))  # 2 (a + temporary ref from getrefcount)
b = a
print(sys.getrefcount(a))  # 3
del b
print(sys.getrefcount(a))  # 2
```

**Advantage:** Deterministic deallocation — objects are freed immediately when no longer referenced. This matters for trading where you want predictable memory behavior.

**Disadvantage:** Cannot handle reference cycles.

#### Generational Garbage Collector

For reference cycles (A references B, B references A), CPython has a generational GC with three generations (0, 1, 2). New objects start in generation 0. If they survive a GC pass, they're promoted.

```python
import gc

# Disable GC for latency-critical sections
gc.disable()
process_market_data_batch()
gc.enable()

# Or tune thresholds
gc.set_threshold(700, 10, 10)  # (gen0, gen1, gen2)
```

**HFT consideration:** GC pauses can cause latency spikes. Some trading systems disable the GC entirely and rely on reference counting alone (avoiding cycles by design) or schedule GC during quiet periods.

#### `__slots__`

By default, Python objects store attributes in a `__dict__` (a hash table per instance). `__slots__` replaces this with a fixed-size array, saving ~40-50% memory per instance and providing faster attribute access.

```python
class Order:
    __slots__ = ('symbol', 'side', 'qty', 'price', 'timestamp')

    def __init__(self, symbol, side, qty, price, timestamp):
        self.symbol = symbol
        self.side = side
        self.qty = qty
        self.price = price
        self.timestamp = timestamp

# Cannot add arbitrary attributes:
# o.extra = 1  # AttributeError
```

**When to use:** Any class with many instances (orders, ticks, positions). If you're creating millions of `Tick` objects, `__slots__` can save gigabytes.

#### Weak References

A weak reference doesn't increment the reference count, so the object can be garbage collected even if weak references exist.

```python
import weakref

class MarketDataCache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()

    def get_snapshot(self, symbol):
        snap = self._cache.get(symbol)
        if snap is None:
            snap = fetch_snapshot(symbol)
            self._cache[symbol] = snap
        return snap
```

**Trading use case:** Caches that shouldn't prevent garbage collection. If no one else holds a reference to the snapshot, it gets cleaned up automatically.

### 8. Concurrency: threading vs multiprocessing vs asyncio

#### threading

- Uses OS threads but limited by the GIL
- Good for I/O-bound tasks: network I/O, file I/O, database queries
- Shared memory space — easy data sharing but requires synchronization
- Thread creation has ~100 microsecond overhead

```python
import threading

class MarketDataHandler:
    def __init__(self):
        self.book = {}
        self.lock = threading.Lock()

    def update(self, symbol, price):
        with self.lock:
            self.book[symbol] = price
```

#### multiprocessing

- Uses separate OS processes — each has its own GIL and memory space
- Good for CPU-bound tasks: risk calculations, strategy backtesting
- Data sharing via `Queue`, `Pipe`, `shared_memory`, or `Manager`
- Process creation is expensive (~10-100ms)

```python
from multiprocessing import Process, Queue

def calculate_risk(positions, result_queue):
    var = compute_value_at_risk(positions)
    result_queue.put(var)

q = Queue()
p = Process(target=calculate_risk, args=(positions, q))
p.start()
var = q.get()  # Blocks until result is available
p.join()
```

#### asyncio

- Single-threaded cooperative multitasking using an event loop
- Good for high-concurrency I/O (thousands of connections)
- Uses `async`/`await` syntax — no locks needed (single-threaded!)
- Lower overhead than threading — no OS thread switching

```python
import asyncio

async def subscribe_to_feed(exchange):
    reader, writer = await asyncio.open_connection(exchange.host, exchange.port)
    while True:
        data = await reader.readline()
        process_update(data)

async def main():
    await asyncio.gather(
        subscribe_to_feed(cme),
        subscribe_to_feed(ice),
        subscribe_to_feed(asx),
    )

asyncio.run(main())
```

**When to use what:**

| Scenario | Best Choice | Why |
|---|---|---|
| Multiple FIX connections | threading or asyncio | I/O bound, GIL released |
| Risk computation across positions | multiprocessing | CPU bound, bypasses GIL |
| High-connection-count gateway | asyncio | Lowest overhead per connection |
| Quick concurrent API calls | asyncio or threading | I/O bound |
| Number crunching with NumPy | threading | NumPy releases GIL in C code |

---

## Practice Questions (20-30 min)

Write out answers to these as if you were explaining to an interviewer:

1. **Explain the difference between `is` and `==` in Python. Give an example where they produce different results and explain why.**

2. **How does Python's `dict` handle hash collisions? Walk through what happens when you insert a key that collides with an existing key.**

3. **You're building a system that processes 1 million market data ticks per second, each represented as a Python object with 5 fields. How would you optimize memory usage? Discuss at least three techniques.**

4. **Explain the GIL. Your trading system needs to both listen for market data (I/O) and compute risk metrics (CPU) in real time. How would you design the concurrency model?**

5. **What is the difference between a generator and a list comprehension? When would you prefer one over the other in a trading system context?**

6. **Write a decorator that caches the last N results of a function call (an LRU cache). Explain your design choices.**

7. **Why might you disable Python's garbage collector in a latency-sensitive application? What are the risks of doing so?**

8. **Explain how `asyncio` works at a high level. Why is it single-threaded yet concurrent? Compare it to threading for a system that manages 500 simultaneous FIX connections.**

9. **What happens internally when you call `dict[key]` and the key doesn't exist? Trace through the hash table lookup process.**

10. **You observe that your Python application's memory usage keeps growing even though you're deleting objects. What could cause this and how would you diagnose it?**

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** What does `id(x)` return in CPython?
- (A) The hash of x
- (B) The memory address of the PyObject
- (C) A unique integer assigned at object creation
- (D) The reference count of x

**Q2.** What is the time complexity of `list.insert(0, x)` for a list of n elements?
- (A) O(1)
- (B) O(log n)
- (C) O(n)
- (D) O(n log n)

**Q3.** Python dicts use which collision resolution strategy?
- (A) Separate chaining with linked lists
- (B) Open addressing with linear probing
- (C) Open addressing with a perturbation-based probing scheme
- (D) Cuckoo hashing

**Q4.** Which statement about the GIL is FALSE?
- (A) It prevents multiple threads from executing Python bytecode simultaneously
- (B) It is released during I/O operations
- (C) It makes all Python programs thread-safe
- (D) It exists because reference counting is not thread-safe

**Q5.** What is the output?
```python
a = (1, 2, [3, 4])
a[2].append(5)
print(a)
```
- (A) TypeError — tuples are immutable
- (B) (1, 2, [3, 4, 5])
- (C) (1, 2, [3, 4])
- (D) AttributeError

**Q6.** `__slots__` provides which benefits?
- (A) Faster attribute access and reduced memory usage
- (B) Thread safety for attribute access
- (C) Automatic garbage collection of instances
- (D) Dynamic attribute addition at runtime

**Q7.** Which concurrency model bypasses the GIL for CPU-bound work?
- (A) threading
- (B) asyncio
- (C) multiprocessing
- (D) concurrent.futures.ThreadPoolExecutor

**Q8.** What does `functools.wraps` do in a decorator?
- (A) Makes the decorator thread-safe
- (B) Copies metadata (__name__, __doc__) from the wrapped function to the wrapper
- (C) Automatically caches the function's return values
- (D) Prevents the decorated function from being called recursively

**Q9.** In CPython's generational GC, objects that survive collection are:
- (A) Immediately freed
- (B) Moved to a younger generation
- (C) Moved to an older generation
- (D) Marked as immortal

**Q10.** Which is NOT a valid way to share data between processes in Python's `multiprocessing`?
- (A) multiprocessing.Queue
- (B) multiprocessing.shared_memory
- (C) Global variables
- (D) multiprocessing.Pipe

### Short Answer

**Q11.** Explain why this code produces unexpected behavior:
```python
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item(1))
print(add_item(2))
```

**Q12.** What is the difference between `weakref.ref` and a normal reference? Give a use case relevant to trading systems.

**Q13.** A generator function contains a `try/finally` block. When is the `finally` block executed?

**Q14.** You have a dict with 1000 entries and the hash table has 1536 slots (2/3 load factor not yet reached). You insert one more entry whose hash collides with an existing entry. Describe what happens step by step.

**Q15.** Write a context manager using `contextlib.contextmanager` that times a block of code and logs the duration.

**Q16.** Why is `collections.deque` preferred over `list` for a FIFO queue? What is the algorithmic reason?

**Q17.** Explain the difference between `gc.disable()` and setting high GC thresholds. Which approach would you recommend for a latency-sensitive trading system and why?

**Q18.** What is the difference between an iterator and an iterable? Can an object be both?

---

## Quiz Answer Key

**Q1: (B)** In CPython, `id()` returns the memory address of the underlying C `PyObject` struct. This is an implementation detail — other Python implementations may return different identifiers. The id is guaranteed to be unique among simultaneously existing objects.

**Q2: (C)** `list.insert(0, x)` is O(n) because every element must be shifted right by one position. The list is a contiguous array of pointers, so insertion at the front requires memmove of all n pointers.

**Q3: (C)** CPython uses open addressing with a perturbation-based probing scheme: `j = ((5*j) + 1 + perturb) % size; perturb >>= 5`. This uses all bits of the hash value, producing better distribution than simple linear probing.

**Q4: (C)** The GIL does NOT make Python programs thread-safe. It only ensures that bytecode instructions are atomic, but compound operations (like `lst.append(x)` where `x` depends on `lst[-1]`) are not atomic. You still need locks for shared mutable state.

**Q5: (B)** The tuple itself is immutable (you can't reassign `a[2]`), but the list object at index 2 is mutable. `a[2].append(5)` mutates the list in place without changing the tuple's pointer to it. Result: `(1, 2, [3, 4, 5])`.

**Q6: (A)** `__slots__` replaces the per-instance `__dict__` (a hash table) with a compact fixed-size array, resulting in faster attribute access (direct offset calculation) and ~40-50% memory savings per instance. The trade-off is no dynamic attribute addition.

**Q7: (C)** `multiprocessing` creates separate OS processes, each with its own Python interpreter and GIL. This is the standard way to achieve true parallelism for CPU-bound Python code. (Note: C extensions like NumPy can also release the GIL within threads.)

**Q8: (B)** `functools.wraps` copies `__name__`, `__module__`, `__qualname__`, `__doc__`, `__dict__`, and `__wrapped__` from the original function to the wrapper. Without it, debugging and introspection tools see the wrapper's metadata instead of the original function's.

**Q9: (C)** Objects that survive garbage collection are promoted to an older (higher-numbered) generation. Generation 0 is collected most frequently, generation 2 least. This is based on the "generational hypothesis" — most objects die young.

**Q10: (C)** Global variables are NOT shared between processes. Each process gets its own copy of the memory space after `fork()`. Changes to globals in one process are invisible to others. Use `Queue`, `Pipe`, or `shared_memory` for inter-process communication.

**Q11:** Default arguments are evaluated once at function definition time, not at each call. The list `[]` is created once and shared across all calls. First call appends 1 to get `[1]`. Second call appends 2 to the SAME list, producing `[1, 2]`. Fix: use `lst=None` and `lst = lst or []` inside the function.

**Q12:** A `weakref.ref` does not increment the object's reference count. If all strong references are deleted, the object is garbage collected even though weak references exist. Trading use case: caching market data snapshots — the cache holds weak references so snapshots can be GC'd when memory is tight, without the cache preventing cleanup.

**Q13:** The `finally` block executes when the generator is closed — either explicitly via `generator.close()`, when the generator object is garbage collected, or when a `return` or unhandled exception terminates the generator. If you iterate to completion (StopIteration), `finally` also runs.

**Q14:** 1) Compute `hash(key)`. 2) Calculate index = hash % 1536. 3) Find that slot occupied. 4) Apply perturbation probe: `j = ((5 * index) + 1 + perturb) % 1536; perturb >>= 5`. 5) Check the new slot. 6) If empty, store the new entry's index there. 7) If occupied, repeat probing. 8) Write `(hash, key, value)` to the next position in the dense entries array.

**Q15:**
```python
from contextlib import contextmanager
import time, logging

@contextmanager
def timer(label):
    start = time.perf_counter_ns()
    try:
        yield
    finally:
        elapsed = time.perf_counter_ns() - start
        logging.info(f"{label}: {elapsed/1e6:.2f}ms")
```

**Q16:** `list.pop(0)` is O(n) because all remaining elements must be shifted left. `deque.popleft()` is O(1) because `deque` is implemented as a doubly-linked list of fixed-size blocks — removing from the front only adjusts a pointer within the current block. For a FIFO queue, this difference is critical at high throughput.

**Q17:** `gc.disable()` completely stops the cyclic garbage collector — no GC pauses but reference cycles leak memory. Setting high thresholds makes GC run less frequently but still runs. For trading: `gc.disable()` during market hours combined with careful coding to avoid reference cycles, then re-enable during quiet periods. Alternatively, high thresholds with scheduled `gc.collect()` during known quiet windows. The former is more predictable but requires discipline.

**Q18:** An **iterable** is any object with `__iter__()` that returns an iterator (e.g., lists, strings, dicts). An **iterator** is an object with both `__iter__()` (returns self) and `__next__()` (returns next value or raises StopIteration). Yes, an iterator is also an iterable (since it has `__iter__`), but not all iterables are iterators (a list has `__iter__` but not `__next__`).
