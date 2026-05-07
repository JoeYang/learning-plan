# STL in the Wild

The containers and algorithms you'll meet in real protocol code — and why the container choice is a latency decision, not a convenience one.

> **The theme:** big-O is the wrong axis for hot-path code. **Cache behaviour and worst-case latency** are what matter. Pick containers based on layout (where do the bytes live?) and worst case (how bad does it get under collision or growth?), not average case.

---

<!-- class: is-section -->

# Part one — choosing containers

Why the default reach is wrong as often as it's right.

---

## The problem in protocol code

You need to handle four kinds of state, all on the hot path:

- **Order book** — `price → qty`, sorted, frequent top-of-book reads.
- **Per-session order state** — `orderID → state`, point lookup at submission and ack.
- **Fixed-size message buffers** — wire frames during parse, lifetime ≤ one packet.
- **Aggregated statistics** — per-second counters, per-symbol P&L, risk inputs.

Each has a "default" container the rest of the world reaches for. In protocol code, **the defaults are wrong as often as they're right** — because cache misses, allocator pressure, and worst-case spikes dominate latency at hot-path rates.

+++

## Why the defaults break

Three failure modes you have to design around:

| Failure mode | Where it bites | Why it's invisible to an average-case mindset |
|---|---|---|
| **Allocation spike** | `vector::push_back` past capacity | Amortised O(1) hides the occasional copy of all N elements |
| **Hash collision** | `unordered_map` under adversarial keys | Average O(1) silently degrades to O(N) when buckets collide |
| **Cache miss chain** | Linked / chunked containers | Pointer chasing across heap fragments stalls the pipeline at every hop |

This phase teaches the right choice for each use case **and** the failure mode of the wrong choice. The validation discipline is benchmarking under the actual access pattern — not staring at big-O.

---

## The map at a glance

| Container | Layout | Average | Worst case | Where it dominates |
|---|---|---|---|---|
| `std::vector<T>` | Contiguous heap | O(1) push, O(1) access | O(N) on realloc | Cache-friendly, no pointer chasing |
| `std::array<T, N>` | Contiguous stack | O(1) access | O(1) access | Compile-time-known buffers |
| `std::unordered_map<K, V>` | Hash table + buckets | O(1) lookup | O(N) under collision | Bounded keys, average-case-tolerant |
| `std::map<K, V>` | Red-black tree | O(log N) | O(log N) | Sorted iteration, range queries |
| `std::deque<T>` | Chunked heap | O(1) at both ends | O(1) at both ends | Rare in hot path; common elsewhere |

**The latency question:** which of these has a *predictable* worst case? Only `std::array` and `std::map`. The others have spikes — and spikes break latency budgets.

---

<!-- class: is-section -->

# Part two — the contiguous containers

`std::vector<T>` and `std::array<T, N>` — the two cache-friendliest options, and the ones you'll reach for most often.

---

## `std::vector<T>` — problem

You need a growable list of T. Common in protocol code: per-session active orders, per-symbol observed trades, message frames buffered for a reorder window.

Cache-friendly: elements are contiguous in memory. CPU prefetchers love this — sequential reads come "for free" because the cache line ahead is already loaded.

```cpp
std::vector<Order> book;
book.push_back(o1);   // amortised O(1)
book.push_back(o2);   // amortised O(1)
// ...
auto& last = book.back();   // O(1) random access
```

The default for "I need a list" — and right almost everywhere except the trap on the next slide.

+++

## `std::vector<T>` — challenge

`push_back` is **amortised** O(1), not O(1). The amortisation hides the occasional reallocation:

When `size() == capacity()`, the next `push_back` does:

1. Allocate a new buffer, typically `1.5 × capacity` or `2 × capacity`.
2. **Copy every element** from the old buffer to the new one.
3. Free the old buffer.

That copy is O(N). On a hot path where the vector grows from 0 to 10⁵ elements, you pay reallocation maybe 17 times — each one a latency spike at an unpredictable moment.

> "Amortised O(1)" averages out fine over a million calls. **It is not fine if any single call must complete in 1 µs.**

+++

## `std::vector<T>` — solution

`reserve(n)` pre-allocates capacity once. After that, `push_back` is genuinely O(1) until you exceed `n`.

```cpp
std::vector<Order> book;
book.reserve(1024);             // ← single allocation up front

for (auto& o : incoming) {
  book.push_back(o);             // O(1), no realloc
}
```

The contract:

- `size()` — number of elements actually stored.
- `capacity()` — number of slots allocated. `≥ size()` always.
- `reserve(n)` — grow `capacity` to at least `n` if smaller; never shrinks.
- `shrink_to_fit()` — release unused capacity (rare in hot paths).

+++

## `std::vector<T>` — validation

Two checks before shipping any hot-path vector:

1. **Static check** — read the code. Does any `push_back` site lack a corresponding `reserve`? If yes, document the upper bound or fix it.
2. **Dynamic check** — under load, count realloc events. With `reserve` correct, the count is **zero** after warm-up. Any non-zero number means your reserved capacity is wrong.

```cpp
// Diagnostic — count reallocations in a load test
size_t prev_capacity = book.capacity();
size_t realloc_count = 0;
// ... after each push_back:
if (book.capacity() != prev_capacity) {
  ++realloc_count;
  prev_capacity = book.capacity();
}
// realloc_count must be 0 after the warm-up phase.
```

> Rule: **if a vector lives on the hot path and grows beyond its initial size, you are paying a latency tax.** Reserve generously, or pick a different structure.

---

## `std::array<T, N>` — fixed size, in the type

When `N` is known at compile time, `std::array<T, N>` beats every alternative. Stack-allocated, zero overhead over a C array, plus the type-system wins from Phase 3 Box 6:

```cpp
std::array<uint8_t, 1500> packet_buf;        // stack-allocated, no heap touch

// Pass to a function — size travels with the type
template<size_t N>
void parse(const std::array<uint8_t, N>& buf);   // N visible at the callee
parse(packet_buf);                                // ✓ N = 1500 deduced
```

+++

## `std::array<T, N>` — three wins over C arrays

1. **Size in the type.** `array<int, 36>` and `array<int, 32>` are distinct types. The compiler enforces it at the function boundary. C arrays decay to `int*` and lose the size.
2. **Proper STL container interface.** `begin()`, `end()`, range-for, algorithms compose naturally. `at(i)` provides bounds-checked access.
3. **Returnable, assignable, copyable.** `std::array` is a value type. `arr1 = arr2` works element-wise. `auto a = make_buffer()` works — C arrays cannot be returned by value.

> Default first reach for any fixed-size buffer. There is no situation on a modern compiler where a C array is better than `std::array` of the same size.

---

<!-- class: is-section -->

# Part three — the associative containers

`std::unordered_map`, `std::map`, and the flat-array escape hatch.

---

## `std::unordered_map<K, V>` — problem

You need point lookup keyed by something with no natural ordering — `orderID → OrderState`, `accountID → SessionInfo`. Hash maps are the textbook answer:

```cpp
std::unordered_map<uint64_t, OrderState> orders;
orders[order_id] = state;
auto it = orders.find(order_id);   // O(1) average
```

This is fine on most days.

+++

## `std::unordered_map<K, V>` — challenge

O(1) **average** is great until adversarial keys produce hash collisions. Then it's **O(N)** — every lookup walks the bucket chain.

For absolute-latency code (microsecond budgets), the worst case is what matters. And the worst case is reachable:

- **Accidental collision** — your hash function distributes order IDs unevenly. Unlikely but possible.
- **Adversarial collision** — an attacker controls keys (e.g., user-submitted client order IDs) and crafts them to collide on purpose, slowing down every subsequent lookup.

> "Unbounded worst case" + "external input drives the keys" = **a denial-of-service primitive**. If you wouldn't ship that elsewhere, don't ship it here.

+++

## `std::unordered_map<K, V>` — solution

When the key domain is bounded — order tokens assigned by the session, capped at some `MAX_ORDERS` — flatten the structure:

```cpp
constexpr size_t MAX_ORDERS_PER_SESSION = 1 << 20;   // 1M tokens
std::array<OrderState, MAX_ORDERS_PER_SESSION> order_table;

// O(1), worst-case O(1)
order_table[order_token] = state;
```

The trade-off is memory for predictability. The flat array uses `MAX × sizeof(OrderState)` bytes regardless of actual count, but every access is a single indexed load — no hashing, no bucket walk, no chain.

For unbounded but rare-collision keys, keep `unordered_map` but use a **measured, non-default hash** and verify load factors stay below 0.5 in production.

+++

## `std::unordered_map<K, V>` — validation

Three diagnostics for any hash-map-on-the-hot-path you keep:

1. **Adversarial test.** Generate keys that hash to the same bucket using your hash function. Measure lookup latency under that load. If it rises by more than 2×, you have a problem.
2. **Load-factor monitor.** `bucket_count()`, `load_factor()`, `max_load_factor()`. Default `max_load_factor` is 1.0; for latency-critical maps, push it to 0.25–0.5 and `reserve` upfront.
3. **Hash-distribution histogram.** Count keys per bucket on production data. A skewed distribution means your hash function isn't right for your key shape.

> Rule: **if your worst case is unbounded, an attacker can find it.** Bounded keys → flat array. Unbounded keys → measured hash + load-factor discipline.

---

## `std::map<K, V>` — the tree

```cpp
std::map<int64_t, int64_t> bids;       // price (in ticks) → total qty, sorted
bids.emplace(price, qty);

auto top = bids.rbegin();              // best bid — O(1) on a sorted structure
for (auto& [p, q] : bids) { ... }      // ordered iteration, descending if rbegin
```

Why a *tree* for order books:

- **Sorted iteration matters** — top-of-book is `rbegin()` / `begin()`, an O(1) op on a sorted structure.
- **Range queries** — "all bids above $X" is a sub-tree traversal.
- **N is bounded and small** — even a wide book has < 10⁴ price levels. log₂(10⁴) ≈ 13.3 — every operation is < 14 node touches.

+++

## `std::map<K, V>` — when not to use it

Cache behaviour is worse than vector because tree nodes are scattered on the heap. Each `find` chases pointers from root to leaf. Acceptable for order books because the tree is small; **bad** if you only need point lookup with no ordering.

When to reach for something else:

- **Point lookup, no ordering needed** → `std::unordered_map` or flat array.
- **Dense prices in a known range** → `std::array<int64_t, TICKS_PER_RANGE>` indexed by `(price - min_price) / tick_size`. Even faster than the tree.
- **Rare insertions, frequent reads, sorted** → sorted `std::vector` with `std::lower_bound`. Single contiguous allocation, perfect cache behaviour.

> The tree wins when *all three* of {sorted iteration, dynamic insertion, log N is small} are true at once. Drop any one and a flatter structure beats it.

---

## `std::deque<T>` — chunked, both ends fast

Non-contiguous segments stitched together. O(1) push/pop at both ends, but each segment boundary is a pointer chase.

Rarely the right choice in hot-path code — segment indirection costs cache misses, and you almost never need both-ended O(1) on a hot path.

```cpp
std::deque<Task> work;
work.push_back(t);     // O(1)
work.push_front(t);    // O(1)  ← but cache-hostile vs vector
```

Common in cooler-path queues — work-stealing pools, request queues with no latency budget. `std::queue<T>` and `std::stack<T>` are adaptors over `std::deque` by default — same constraints.

> Recognise it; rarely write it.

---

<!-- class: is-section -->

# Part four — the silent UB

Iterator invalidation rules. The bugs that compile cleanly, pass tests, and crash the gateway at 09:31:00.

---

## Iterator invalidation — the problem

Every container has rules about which mutations invalidate which iterators. Modifying a container while iterating it without obeying these rules is **undefined behaviour** — sometimes a crash, sometimes silent corruption.

The compiler does not warn. The test suite often passes. The bug surfaces under production load when memory layout shifts.

```cpp
std::vector<int> v = {1, 2, 3};
auto it = v.begin();             // it points to v[0]

v.push_back(4);                  // may reallocate the buffer
                                 // if so, it now points to FREED memory
*it;                             // ← undefined behaviour
```

+++

## The vector traps

Two patterns to recognise:

```cpp
// Trap 1: push_back may invalidate ALL iterators
auto it = v.begin();
v.push_back(99);                // realloc possible
*it;                            // ← UB

// Trap 2: erase invalidates iterators at and after the erased element
for (auto it = v.begin(); it != v.end(); ++it) {
  if (*it == 0) v.erase(it);    // ← UB on next ++it
}
```

The fix for trap 2 is using `erase`'s return value:

```cpp
for (auto it = v.begin(); it != v.end(); ) {
  if (*it == 0) it = v.erase(it);   // erase returns next valid iterator
  else          ++it;
}
```

+++

## Per-container invalidation rules

| Container | `insert` invalidates | `erase` invalidates |
|---|---|---|
| `std::vector` | All iterators if reallocation; else those at/after insert point | Iterators at/after erase point |
| `std::deque` | All iterators in most cases | All iterators in most cases |
| `std::list` | Nothing | Only the erased iterator |
| `std::map` / `std::set` | Nothing | Only the erased iterator |
| `std::unordered_map` / `std::unordered_set` | All iterators if rehash; else nothing | Only the erased iterator |

`std::map` and `std::list` are the gentlest — only the erased iterator dies. `std::vector` and `std::deque` are the harshest. **Always check cppreference before mutating-while-iterating.**

+++

## Safe patterns

Three patterns that avoid the trap entirely:

```cpp
// 1. Range-for — no exposed iterator (read-only is safe)
for (const auto& msg : messages) { process(msg); }

// 2. Collect-then-apply — defer mutations
std::vector<size_t> to_remove;
for (size_t i = 0; i < v.size(); ++i) {
  if (v[i].expired) to_remove.push_back(i);
}
for (auto it = to_remove.rbegin(); it != to_remove.rend(); ++it) {
  v.erase(v.begin() + *it);
}

// 3. erase_if (C++20) — built-in, correct, concise
std::erase_if(v, [](const auto& x) { return x.expired; });
```

> If you find yourself reaching for raw iterator surgery on a hot path, stop. There's almost always a flatter pattern that the compiler can vectorise.

---

<!-- class: is-section -->

# Part five — modern iteration & algorithms (Session 12)

Range-for, `auto`, lambdas, structured bindings, and the algorithms you'll see in real code.

---

## Range-for and `auto`

Range-for is the standard iteration pattern. `auto` deduces the type from the initialiser:

```cpp
for (const auto& msg : messages) {       // const& — no copy, read-only
  process(msg);
}

auto price = msg.price;                  // type deduced — same as int64_t
auto it    = orders.find(id);            // type is iterator — long-form unwieldy
```

Use `auto` when the type is *obvious from context* or *unwieldy to spell*. Don't use it to hide the type from yourself or the reader.

The capture forms inside range-for matter:

| Form | Semantics | When to use |
|---|---|---|
| `for (auto x : v)` | Copy each element | Element is small / trivial / you need to mutate locally |
| `for (auto& x : v)` | Reference, mutable | Element is large or you need to mutate in place |
| `for (const auto& x : v)` | Reference, read-only | Default for read-only iteration |

+++

## Structured bindings (C++17)

Destructure pairs and tuples — including map iteration:

```cpp
for (const auto& [order_id, state] : orders) {        // map<uint64_t, OrderState>
  if (state.expired()) flush(order_id);
}

auto [iter, inserted] = orders.emplace(id, state);    // pair returned by emplace
if (!inserted) {
  // already present — handle as needed
}
```

The names you bind to are local — pick descriptive ones. `auto [k, v]` is fine for short scopes; `auto [order_id, state]` is better in longer code.

+++

## Lambdas

Anonymous functions, often inline:

```cpp
//      capture        params           return-type   body
//     ┌─────┐  ┌──────────────────┐  ┌─────────┐  ┌─────────────────┐
auto comparator = [&](const Order& a, const Order& b) -> bool {
  return a.price > b.price;
};

std::sort(orders.begin(), orders.end(), comparator);
```

Capture modes:

| Form | Effect |
|---|---|
| `[]` | Capture nothing |
| `[=]` | Copy all named variables — careful, this can compound |
| `[&]` | Reference all named variables — cheap, requires lifetime discipline |
| `[x]` | Copy `x` only |
| `[&x]` | Reference `x` only |
| `[this]` | Capture `this` pointer (for member-function lambdas) |

> Default to `[&]` for short-lived lambdas. Reserve `[=]` for callbacks that outlive the enclosing scope (which is rare on hot paths).

---

## Algorithms — `find_if`, `sort`, `lower_bound`

The algorithms library is a uniform interface over begin/end iterator pairs — works with any container including `std::array`.

```cpp
// Find first matching element
auto it = std::find_if(orders.begin(), orders.end(),
                       [](const Order& o) { return o.qty > 100; });

// Sort in place — ascending by default
std::sort(orders.begin(), orders.end(),
          [](auto& a, auto& b) { return a.price > b.price; });   // descending
```

+++

## Binary search — `lower_bound` / `upper_bound`

`lower_bound` returns an iterator to the first element **not less than** target. The workhorse for order-book lookup on a sorted vector:

```cpp
std::vector<int64_t> sorted_prices;   // ascending, populated elsewhere
int64_t target = 12345;

auto it = std::lower_bound(sorted_prices.begin(), sorted_prices.end(), target);

if (it == sorted_prices.end())            { /* target larger than all */ }
else if (*it == target)                    { /* exact match */ }
else                                       { /* target falls between *(it-1) and *it */ }
```

O(log N) on a contiguous container with vastly better cache behaviour than `std::map`. The combination of "sorted vector + lower_bound" beats `std::map` for read-heavy workloads with rare insertions.

+++

## `transform` and `accumulate`

Map and reduce, by name:

```cpp
// transform — apply a function elementwise, write to output range
std::vector<int64_t> notionals(orders.size());
std::transform(orders.begin(), orders.end(), notionals.begin(),
               [](const Order& o) { return o.qty * o.price; });

// accumulate — fold/reduce
auto total_notional = std::accumulate(
    orders.begin(), orders.end(), int64_t{0},
    [](int64_t acc, const Order& o) { return acc + o.qty * o.price; });
```

`accumulate`'s third argument is the **initial value** — note the explicit type `int64_t{0}`. If you pass `0` (untyped int), accumulation may overflow at 2³¹. Always type the seed.

---

## `emplace_back` vs `push_back`

`push_back(x)` copies (or moves) `x` into the vector. `emplace_back(args...)` constructs `T` *in place* using `args` — no intermediate temporary.

```cpp
std::vector<Order> book;

book.push_back(Order{id, price, qty});      // construct Order, then move into vector
book.emplace_back(id, price, qty);          // construct Order directly inside the vector
```

For complex types or types with non-trivial constructors, `emplace_back` saves one move. For trivial types it doesn't matter — the compiler optimises both to the same code.

> Rule of thumb: prefer `emplace_back` when you'd otherwise write `push_back(T{args...})`. Stick with `push_back` when you have an existing `T` to insert.

+++

## `std::move(x)` — what it does and doesn't do

`std::move(x)` doesn't move anything. It's a *cast* that says "treat `x` as an rvalue, eligible for move semantics." The actual move (or copy) happens in whatever function receives the value.

```cpp
std::vector<std::string> names;
std::string s = "ADDORDER";

names.push_back(s);               // copies s — original still valid and intact
names.push_back(std::move(s));    // moves s — leaves it valid-but-unspecified
```

After `std::move(s)`:

- ✓ You can still use `s`.
- ✓ You can assign to `s` again.
- ✓ You can destruct `s`.
- ✗ You cannot read `s`'s contents and assume the original value.

The "valid-but-unspecified" state is the contract: the moved-from object is in *some* state that satisfies the type's invariants, but the contents are gone. For `std::string`, that's typically the empty string — but you shouldn't rely on it.

---

<!-- class: is-dark -->

# Phase 4 takeaways

Five ideas to carry forward:

1. **Cache behaviour beats big-O on hot paths.** Choose containers by layout first, complexity second.
2. **`reserve()` is mandatory** on growable hot-path vectors. Without it, you ship reallocation spikes to production.
3. **Worst case matters.** `unordered_map` is O(N) under collision. For absolute-latency code, prefer flat arrays when keys are bounded.
4. **`std::array<T, N>`** over C arrays — size travels with the type, distinct sizes are distinct types.
5. **Iterator invalidation is silent UB.** Know the rules per container, prefer range-for / `erase_if` / collect-then-apply.

**Where does the work live? With the container that matches your access pattern, your worst case, and your cache budget — chosen on purpose, not by default.**

---

## Glossary

| Term | Definition |
|---|---|
| **STL** | Standard Template Library — the C++ standard collection of generic containers, iterators, and algorithms. |
| **Big-O** | Asymptotic complexity notation describing how operation cost scales with input size. |
| **Amortised O(1)** | Average constant time per operation across a sequence, even if individual operations are occasionally O(N). |
| **Hot path** | The code path executed under latency-critical workloads (e.g., per-tick processing, per-order handling). |
| **Cache line** | The unit of memory the CPU fetches from RAM into cache, typically 64 bytes on x86-64. |
| **Cache miss** | A memory access that wasn't already in cache; costs ~100 cycles vs ~4 cycles for a hit. |
| **Realloc spike** | A latency burst caused by `vector` growing past its capacity and copying every element. |
| **Hash collision** | Two distinct keys producing the same hash value, forcing the hash map to walk a bucket chain. |
| **Adversarial keys** | Keys constructed deliberately to collide, used as a denial-of-service primitive against hash maps. |
| **Load factor** | `size() / bucket_count()` for a hash map; high values increase collision frequency. |
| **Order book** | The data structure holding all open buy and sell orders for a symbol, sorted by price. |
| **Top of book** | The best (highest) bid and best (lowest) ask in the order book — the reference price for trading decisions. |
| **Tick** | The smallest price increment allowed by the exchange (e.g., $0.01). |
| **Notional** | Quantity × price — the dollar value of an order or position. |
| **Range-for** | The C++11 syntax `for (auto& x : container)` for iterating without exposing iterators. |
| **Structured binding** | The C++17 syntax `auto [a, b] = pair` for destructuring composite values. |
| **Lambda** | An anonymous function expression, typically used as a callback or comparator. |
| **Capture mode** | The `[...]` part of a lambda controlling which outer variables are visible inside its body. |
| **Move semantics** | The mechanism that transfers resources from one object to another, leaving the source valid-but-unspecified. |
| **`std::move(x)`** | A cast that marks `x` as movable; the actual move (or copy) happens in the receiving function. |
| **`emplace_back`** | A `vector` insertion that constructs the element in place from arguments, avoiding an intermediate temporary. |
| **Iterator invalidation** | The condition where a container mutation makes existing iterators unsafe to dereference. |
| **`erase_if`** (C++20) | A free function that removes all elements satisfying a predicate, without iterator-invalidation traps. |
