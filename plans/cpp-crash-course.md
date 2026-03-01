# Learning Plan: C++ Crash Course for Protocol Code Readers

**Start date:** 2026-03-01
**Target completion:** ~2026-03-22 (3 weeks)
**Schedule:** 5 sessions/week, ~1.5 hours each (15 sessions)
**Status:** not-started

---

## Phase 1: Memory, Types & Casting (Sessions 1–4)
*Foundation for reading binary protocol parsing code — every feedhandler starts here*

### Session 1: Types, Pointers & References
**Objective:** Refresh raw memory manipulation — the building blocks of all protocol parsing
- [x] Raw pointers: declaration, dereferencing, pointer arithmetic (`ptr + n` skips `n * sizeof(T)` bytes)
- [x] `const` correctness: `const T*` (pointer to const) vs `T* const` (const pointer) vs `const T* const`
- [x] References vs pointers: when protocol code uses `const MsgType&` vs `const MsgType*` and why
- [x] `nullptr` vs `NULL` vs `0` — modern C++ convention
- [x] Void pointers: `void*` in low-level buffer code, why you need a cast to use them
- [x] Pointer vs array: why `uint8_t buf[1500]` decays to `uint8_t*` when passed to a function
- [x] Stack vs heap: what lives where, why protocol parsers avoid heap allocation
**Key concepts:** pointer arithmetic, const correctness, references, void pointers, stack vs heap
**Resources:** cppreference — Pointer, Reference; Tour of C++ Ch. 1

### Session 2: Memory Layout — Structs, Padding & Packing
**Objective:** Understand how C++ lays out structs in memory — critical for mapping structs to wire formats
- [ ] Struct layout basics: members laid out in declaration order
- [ ] Alignment rules: each member aligned to its own size (int at 4-byte boundary, double at 8-byte)
- [ ] Padding: compiler inserts padding bytes to satisfy alignment — `sizeof` includes padding
- [ ] `alignof(T)`: returns the alignment requirement of type T
- [ ] `offsetof(Type, member)`: byte offset of a member within a struct
- [ ] `#pragma pack(1)`: suppress padding — struct layout matches wire format byte-for-byte
- [ ] `__attribute__((packed))`: GCC equivalent of pragma pack
- [ ] `static_assert(sizeof(AddOrder) == 36, "size mismatch")`: compile-time layout validation
- [ ] Why packed structs can cause unaligned access faults on some architectures (x86 tolerates it, ARM may not)
- [ ] Unions: overlapping storage, used for type punning in protocol code
**Key concepts:** alignment, padding, `offsetof`, `sizeof`, `#pragma pack`, packed structs, unions
**Resources:** cppreference — alignof, offsetof; "Data alignment: Straighten Up and Fly Right" (IBM)

### Session 3: Casting — static_cast, reinterpret_cast, const_cast
**Objective:** Understand every cast you'll see in protocol code and what each one actually does
- [ ] C-style cast `(T)x`: the old way — avoid in modern C++, hard to grep for
- [ ] `static_cast<T>(x)`: checked at compile time, for related types (numeric conversions, base↔derived with known type)
- [ ] `reinterpret_cast<T*>(ptr)`: reinterpret bits — the workhorse of protocol parsing
  - `reinterpret_cast<const AddOrder*>(buf + 1)`: treat raw bytes as a typed struct
  - Zero-copy: no data moved, just a reinterpretation of the pointer type
  - Undefined behavior risk: strict aliasing — why `__attribute__((packed))` or `memcpy` is safer
- [ ] `const_cast<T*>(ptr)`: remove const — rare, usually a code smell
- [ ] When each cast appears in protocol code:
  - `reinterpret_cast` → parsing binary messages from buffers
  - `static_cast` → numeric type conversions (uint16_t to int, enum to underlying type)
  - `const_cast` → almost never in good code
- [ ] `std::bit_cast<T>` (C++20): type-safe bit reinterpretation, the right way to do type punning
**Key concepts:** reinterpret_cast, static_cast, zero-copy parsing, strict aliasing, bit_cast
**Resources:** cppreference — reinterpret_cast, static_cast; CppCon "Type Punning in C++"

### Session 4: Endianness & Byte Manipulation
**Objective:** Understand byte order issues that affect every field in every binary protocol message
- [ ] Big-endian vs little-endian: which byte comes first in a multi-byte integer
  - Big-endian (network byte order): most significant byte first — used by most exchange protocols
  - Little-endian (x86 host byte order): least significant byte first
- [ ] `htons`/`htonl` (host-to-network): convert 16/32-bit values before sending
- [ ] `ntohs`/`ntohl` (network-to-host): convert 16/32-bit values after receiving
- [ ] `__builtin_bswap16/32/64`: GCC intrinsics for byte swapping — faster than manual shifts
- [ ] Manual byte swap: `(x >> 8) | (x << 8)` — why this appears in hot-path code
- [ ] Reading a big-endian field from a buffer without casting: `(buf[0] << 8) | buf[1]`
- [ ] Bitfields: `uint8_t flags : 3` — packing multiple values into one byte, endianness interactions
- [ ] Fixed-width integer types: `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t` — why protocol code never uses `int`
- [ ] `int64_t` price fields: many exchanges encode price as integer (price × 10^8) — no floating point
**Key concepts:** endianness, ntohl/ntohs, byte swap, bitfields, fixed-width integers, price encoding
**Resources:** cppreference — Fixed width integer types; ITCH spec field descriptions (check byte order notes)

---

## Phase 2: OOP & Resource Management (Sessions 5–6)
*Understanding the class structure wrapping protocol state*

### Session 5: Classes, RAII & Rule of 0/3/5
**Objective:** Read class definitions in protocol code without confusion — understand lifetime and ownership
- [ ] Constructor types: default, parameterized, copy, move — which is called when
- [ ] Destructor: `~MyClass()` — called when object goes out of scope or is deleted
- [ ] RAII (Resource Acquisition Is Initialization): resource acquired in constructor, released in destructor
  - Examples in protocol code: socket wrapper (opens in ctor, closes in dtor), lock guard
- [ ] Rule of Zero: if you don't manage resources, don't write any of the five special members
- [ ] Rule of Three: if you write destructor, write copy constructor and copy assignment too
- [ ] Rule of Five: add move constructor and move assignment for performance
- [ ] `= delete` and `= default`: explicitly disabling or defaulting special members
  - `MyHandler(const MyHandler&) = delete`: non-copyable (common in protocol handlers)
- [ ] `explicit` constructors: prevents implicit conversion — common in protocol code to avoid accidents
- [ ] `inline` and member functions defined in headers: why protocol code is often header-heavy
- [ ] `struct` vs `class`: only difference is default access (public vs private)
**Key concepts:** RAII, rule of 0/3/5, move semantics, deleted functions, explicit constructors
**Resources:** cppreference — Constructors; Effective C++ Items 5, 6, 17

### Session 6: Smart Pointers & Ownership
**Objective:** Read ownership patterns in protocol code — know what each smart pointer signals
- [ ] `std::unique_ptr<T>`: sole ownership, non-copyable, movable — the default choice
  - `make_unique<T>(args)`: prefer over `new T(args)`
  - Appears in protocol code for: session objects, parser instances, configuration
- [ ] `std::shared_ptr<T>`: shared ownership, reference-counted — use sparingly on hot path
  - Atomic ref-count increment/decrement — overhead on every copy
  - When you'll see it: shared market data subscriptions, cross-thread shared state
- [ ] `std::weak_ptr<T>`: non-owning observer of a shared_ptr — breaks cycles
- [ ] Raw pointers in modern C++: still appear as non-owning observers (`T*` = "I don't own this")
- [ ] `std::optional<T>` (C++17): represents a value that may or may not be present — replaces nullable pointers for value types
- [ ] When to use each:
  - `unique_ptr`: single owner, transfer of ownership
  - `shared_ptr`: genuinely shared, multiple owners
  - Raw pointer: non-owning reference, performance-critical paths
  - `optional`: optional value without heap allocation
**Key concepts:** unique_ptr, shared_ptr, ownership semantics, RAII, optional
**Resources:** cppreference — unique_ptr, shared_ptr; Effective Modern C++ Items 18–22

---

## Phase 3: Templates & Compile-Time Programming (Sessions 7–10)
*The hardest-to-read patterns in protocol code — this phase is the core*

### Session 7: Function & Class Templates
**Objective:** Read template syntax fluently — understand instantiation and specialization
- [ ] Function template syntax: `template<typename T> void foo(T x)` — T is deduced from argument
- [ ] Template type deduction: how the compiler infers T from the call site
- [ ] Explicit instantiation: `foo<int>(42)` — forcing a specific type
- [ ] Class template syntax: `template<typename Config> class Handler { ... }`
- [ ] Template instantiation: each unique T creates a separate compiled function/class
- [ ] Explicit template specialization: `template<> void foo<AddOrder>(const AddOrder& msg)` — per-type overrides
- [ ] Partial specialization: specializing on some template parameters but not all (class templates only)
- [ ] Non-type template parameters: `template<int N>` — compile-time integer, used for buffer sizes
- [ ] `typename` vs `class` in template parameter lists: identical, use `typename` for clarity
- [ ] Template member functions: reading `template<typename T> class Foo { template<typename U> void bar(U); }`
**Key concepts:** template syntax, type deduction, specialization, instantiation, non-type parameters
**Resources:** cppreference — Templates; CppCon "Template Normal Programming"

### Session 8: CRTP & Static Polymorphism
**Objective:** Spot and fully understand CRTP wherever it appears — the most common pattern in hot-path C++
- [ ] Virtual function cost recap: vtable pointer per object + indirect call + potential cache miss (~3–5 ns)
- [ ] CRTP pattern: `template<typename Derived> class Base { ... }` — derived passes itself as template arg
  - `class MyHandler : public Handler<MyHandler>` — the tell-tale sign
- [ ] `static_cast<Derived*>(this)`: how base calls derived — resolved at compile time, zero overhead
- [ ] Why it works: when `Handler<MyHandler>` is instantiated, compiler knows the full type of `Derived`
- [ ] Common uses in protocol code:
  - Callback dispatch: parser calls `static_cast<Derived*>(this)->onAddOrder(msg)` — no vtable
  - Mixin: base class adds functionality, derived class provides policy (e.g., logging, throttle checking)
- [ ] When NOT to use CRTP: when you genuinely need runtime polymorphism (heterogeneous collections)
- [ ] CRTP vs virtual: side-by-side comparison of the same handler implemented both ways
- [ ] Reading exercise: identify CRTP in rigtorp/SPSCQueue or an open-source ITCH parser
**Key concepts:** CRTP, static polymorphism, zero-overhead abstraction, vtable vs static dispatch
**Resources:** CppCon "The Curiously Recurring Template Pattern"; cppreference — CRTP

### Session 9: Tag Dispatch & Type Traits
**Objective:** Understand compile-time branching patterns — how code selects behavior without if/else at runtime
- [ ] Tag dispatch: empty structs used as compile-time labels
  ```cpp
  struct MarketDataTag {};
  struct OrderEntryTag {};
  ```
  Overload resolution picks the right function based on tag type — zero runtime cost
- [ ] Type traits: `std::is_same<T, U>`, `std::is_integral<T>`, `std::is_trivially_copyable<T>`
  - Used to query type properties at compile time
  - Common in protocol code: `static_assert(std::is_trivially_copyable<AddOrder>::value)`
- [ ] `std::enable_if<condition, T>`: enables a function only when condition is true (SFINAE)
  - Harder to read: `template<typename T, typename = std::enable_if_t<std::is_integral_v<T>>>`
  - Modern alternative: `if constexpr` (Session 10)
- [ ] `decltype(expr)`: deduce type from an expression — used in trailing return types and auto
- [ ] `std::conditional<B, T, F>`: pick type T if B is true, F if false — compile-time ternary for types
- [ ] `using` type aliases: `using Price = int64_t` — makes protocol field types readable
- [ ] Reading exercise: find a type_traits use in open-source protocol code and explain what it does
**Key concepts:** tag dispatch, type traits, SFINAE, enable_if, decltype, type aliases
**Resources:** cppreference — type_traits; CppCon "Modern Template Metaprogramming"

### Session 10: constexpr & Compile-Time Computation
**Objective:** Understand compile-time constants and branching — how protocol code eliminates runtime overhead
- [ ] `constexpr` variables: `constexpr size_t MSG_SIZE = 36` — evaluated at compile time, stored in read-only memory
- [ ] `constexpr` functions: evaluated at compile time if arguments are compile-time constants
  ```cpp
  constexpr uint32_t makeTag(char a, char b, char c, char d) {
      return (a << 24) | (b << 16) | (c << 8) | d;
  }
  ```
- [ ] `static_assert(expr, "msg")`: compile-time assertion — fails the build if condition is false
  - Protocol use: `static_assert(sizeof(AddOrder) == 36, "wire format changed")`
- [ ] `if constexpr` (C++17): compile-time branching — the dead branch is not compiled at all
  ```cpp
  if constexpr (std::is_same_v<T, AddOrder>) {
      // only compiled for AddOrder
  }
  ```
  Replaces SFINAE and tag dispatch for many use cases — much more readable
- [ ] `constexpr` vs `const`: `const` is runtime-constant (can be initialized from a variable), `constexpr` is truly compile-time
- [ ] `std::array<T, N>`: fixed-size array, size is a compile-time constant — prefer over C arrays
- [ ] Reading exercise: find constexpr uses in a protocol spec header and explain each one
**Key concepts:** constexpr, static_assert, if constexpr, compile-time computation, std::array
**Resources:** cppreference — constexpr; CppCon "constexpr ALL the things!"

---

## Phase 4: STL in the Wild (Sessions 11–12)
*The containers and algorithms you'll encounter in real code*

### Session 11: Containers — vector, array, unordered_map, deque
**Objective:** Know the performance characteristics and memory layout of every container you'll see
- [ ] `std::vector<T>`: contiguous heap memory, amortized O(1) push_back, O(1) random access
  - `reserve(n)`: pre-allocate to avoid reallocation — critical for hot-path code
  - `size()` vs `capacity()`: elements in use vs allocated slots
  - Why vectors dominate: cache-friendly, no pointer chasing
- [ ] `std::array<T, N>`: fixed-size, stack-allocated, zero overhead over C array — prefer for message buffers
- [ ] `std::unordered_map<K, V>`: hash map, O(1) average lookup — used for order maps (orderID → order state)
  - Worst case O(N) — not suitable for absolute latency guarantees
  - Alternative: flat arrays indexed by order token when domain is bounded
- [ ] `std::map<K, V>`: tree-based, O(log N) — used for order books (price → qty), sorted by price
- [ ] `std::deque<T>`: double-ended queue — O(1) push/pop at both ends, non-contiguous
- [ ] `std::queue<T>` and `std::stack<T>`: adaptors over deque — rarely seen in hot-path code
- [ ] Container choice in protocol code: why order books use `std::map`, why order state uses flat arrays or hash maps
- [ ] Iterators: `begin()`/`end()`, range-for, iterator invalidation rules (critical when modifying while iterating)
**Key concepts:** vector, array, unordered_map, map, reserve, cache locality, iterator invalidation
**Resources:** cppreference — Containers library; CppCon "std::map Performance"

### Session 12: Algorithms, Lambdas & Modern Iteration
**Objective:** Read modern C++ iteration and functional patterns without confusion
- [ ] Range-for: `for (const auto& msg : messages)` — the standard way to iterate
- [ ] `auto` type deduction: `auto price = msg.price` — compiler deduces type, reduces verbosity
- [ ] Structured bindings (C++17): `auto [key, value] = *it` — destructure pairs and tuples
- [ ] Lambda syntax: `[capture](params) -> return_type { body }`
  - Capture modes: `[=]` copy all, `[&]` reference all, `[x]` copy x, `[&x]` reference x
  - Common use: comparators for sorting, callbacks, `std::for_each`
- [ ] `std::for_each`, `std::find_if`, `std::count_if`, `std::sort` — the algorithms you'll see most
- [ ] `std::transform`: apply a function to each element, write results to output range
- [ ] `std::lower_bound` / `std::upper_bound`: binary search on sorted containers — used in order book price lookup
- [ ] `std::accumulate`: fold/reduce — sum quantities, aggregate statistics
- [ ] Move semantics basics: `std::move(x)` transfers ownership, avoids copy — appears in container insertions
- [ ] `emplace_back` vs `push_back`: construct in-place vs copy/move — prefer emplace for complex types
**Key concepts:** range-for, auto, lambdas, structured bindings, algorithms, move semantics, emplace
**Resources:** cppreference — Algorithm library; "Effective Modern C++" Items 11–15

---

## Phase 5: Concurrency Primitives (Sessions 13–14)
*Lock-free queues and atomics appear everywhere in hot-path code*

### Session 13: std::thread & std::atomic Basics
**Objective:** Understand the threading and atomic primitives in exchange connectivity code
- [ ] `std::thread`: launch a thread, `join()` to wait, `detach()` to release — basic mechanics
- [ ] Thread safety problem: two threads reading/writing the same variable without synchronization = data race = undefined behavior
- [ ] `std::mutex` + `std::lock_guard`: mutual exclusion — why this is too slow for the hot path
- [ ] `std::atomic<T>`: operations that appear instantaneous to other threads — no locks needed for simple operations
  - `load()`, `store()`, `fetch_add()`, `compare_exchange_strong()`
  - Only works for types T where `sizeof(T) <= 8` (on x86)
- [ ] Memory ordering — the hardest part:
  - `memory_order_relaxed`: no ordering guarantees, just atomicity — fastest
  - `memory_order_acquire`: no reads/writes can move before this load
  - `memory_order_release`: no reads/writes can move after this store
  - `memory_order_seq_cst`: full sequential consistency — slowest, the default
- [ ] Acquire-release pairing: producer does `store(val, release)`, consumer does `load(acquire)` — guarantees consumer sees all writes producer made before the store
- [ ] `volatile` is NOT `atomic`: volatile prevents compiler reordering, not CPU reordering — wrong tool for threading
- [ ] `std::atomic_thread_fence`: explicit memory fence — rarely needed if using acquire/release
**Key concepts:** std::thread, std::atomic, memory ordering, acquire/release, mutex vs atomic
**Resources:** cppreference — atomic; CppCon "atomic Weapons" (Herb Sutter); "C++ Concurrency in Action" Ch. 5

### Session 14: Lock-Free Patterns — SPSC Queues & CAS
**Objective:** Read lock-free data structures — the backbone of feedhandler-to-strategy communication
- [ ] Why lock-free: mutex acquisition can take microseconds (OS scheduler involvement), unacceptable on hot path
- [ ] SPSC queue (Single-Producer Single-Consumer): one thread writes, one thread reads — no contention
  - `head_` and `tail_` are atomics — producer increments tail, consumer increments head
  - Ring buffer: fixed-size array, wrap around using modulo — no allocation
  - Cache line padding: `alignas(64)` between head and tail to prevent false sharing
- [ ] False sharing: two atomics on the same 64-byte cache line bounce between cores — kills performance
  - Fix: `alignas(64) std::atomic<size_t> head_; alignas(64) std::atomic<size_t> tail_;`
- [ ] Compare-and-swap (CAS): `compare_exchange_strong(expected, desired)` — atomic read-modify-write
  - Returns true if the swap happened (value was `expected`), false if another thread changed it first
  - MPSC/MPMC queues use CAS loops — more complex than SPSC
- [ ] ABA problem: CAS sees the same value but state has changed — how lock-free structures guard against it
- [ ] Reading rigtorp/SPSCQueue: walk through the actual implementation, identify each pattern
- [ ] When to use lock-free vs mutex: lock-free is faster but harder to get right — use mutex first, optimize later
**Key concepts:** SPSC, ring buffer, CAS, false sharing, cache line alignment, lock-free vs mutex
**Resources:** rigtorp/SPSCQueue (GitHub), CppCon "Lock-Free Programming"; "C++ Concurrency in Action" Ch. 7

---

## Phase 6: Capstone (Session 15)

### Session 15: Read Real Code — Open-Source Protocol Handler
**Objective:** Apply all 14 sessions — read a real open-source C++ protocol handler from top to bottom
- [ ] Choose one: rigtorp/SPSCQueue, a NASDAQ ITCH parser, or a SoupBinTCP implementation on GitHub
- [ ] Read every file — for each non-obvious line, identify which session taught you that pattern
- [ ] Checklist of patterns to find and annotate:
  - [ ] reinterpret_cast used for zero-copy parsing
  - [ ] packed struct with static_assert size check
  - [ ] CRTP or template dispatch
  - [ ] constexpr protocol constants
  - [ ] std::atomic with memory ordering
  - [ ] SPSC or ring buffer for inter-thread messaging
  - [ ] smart pointer or RAII resource management
  - [ ] STL container for order or book state
- [ ] For each pattern found: write a 2-sentence explanation of what it does and why it's written that way
- [ ] Note any patterns you still don't understand — flag for follow-up
- [ ] Deliverable: a written annotated summary of the codebase (can be in the log entry for this session)
**Key concepts:** synthesis — all prior sessions applied to real code
**Resources:** rigtorp/SPSCQueue, GitHub search for "ITCH parser C++"
