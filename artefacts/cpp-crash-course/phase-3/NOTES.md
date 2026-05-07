# Phase 3 Capstone — Template Playground Notes

Maps each section of `template_playground.cpp` to the protocol-code pattern it
models. Fill out as the capstone is implemented; the goal is to be able to
explain each snippet to a peer in two sentences.

---

## 1. CRTP Handler

**Pattern in the playground:** `class Base<Derived>` with `dispatch()` calling
`static_cast<Derived*>(this)->onMessage()`; `class MyHandler : public Base<MyHandler>`.

**Protocol-code analogue:**
<!-- e.g. NASDAQ ITCH parser dispatching to a derived feed handler that
implements onAddOrder, onModifyOrder, etc. without vtable cost. -->

**Why CRTP over `virtual`:**
<!-- Vtable adds 8B per object + indirect call + cache-miss risk per call.
At feed rates of millions of messages per second the cost compounds. CRTP
resolves the call at compile time and inlines. -->

---

## 2. Tag-Dispatched Router

**Pattern in the playground:** `struct FastPathTag {}; struct SafePathTag {};`
plus two `route(const Message&, Tag)` overloads.

**Protocol-code analogue:**
<!-- e.g. an order-entry session routing follow-on orders via a fast path
(skip pre-trade risk) and fresh orders via a safe path (run risk first).
Same Order type, different processing depending on caller intent. -->

**Why tag dispatch over `if` / `enum`:**
<!-- Compile-time selection — no runtime branch in the binary. The compiler
emits the chosen path directly at the call site. An enum-based dispatch
would still have a runtime switch and dead code in the binary. -->

---

## 3. static_assert-Guarded POD

**Pattern in the playground:** packed struct + `static_assert(sizeof(...) == N)`
+ `static_assert(std::is_trivially_copyable_v<...>)`.

**Protocol-code analogue:**
<!-- Every wire-format struct in a feed handler that's parsed via
reinterpret_cast<const Msg*>(buf). Examples: ITCH AddOrder (36 bytes),
SoupBinTCP packet headers, FIX FAST encoded messages. -->

**What each assertion catches:**

- `sizeof(...) == N` — **layout drift**. Someone reorders fields, adds padding,
  changes a type width, or pragma-pack settings change globally. Build breaks
  before any wire packets are misparsed.
- `is_trivially_copyable_v<...>` — **type drift that breaks memcpy semantics**.
  Someone adds a `std::string`, `std::unique_ptr`, virtual function, or
  user-defined destructor. Without this, `reinterpret_cast` from wire bytes
  silently produces UB (segfault, garbage data, or heap corruption when the
  destructor calls `free()` on a wire-bytes-as-pointer).

**The principle:** *fail at compile time, not at market open.*

---

## 4. `if constexpr` Byteswap

**Pattern in the playground:** one function template `byteswap(T)` with
`if constexpr (sizeof(T) == 2 / 4 / 8)` chain selecting the appropriate
`__builtin_bswap` intrinsic.

**Protocol-code analogue:**
<!-- Generic helpers in feed handlers that read big-endian fields from
wire buffers regardless of the field's width — same function for uint16_t
sequence numbers, uint32_t order IDs, uint64_t timestamps. -->

**Why `if constexpr` over SFINAE / tag dispatch:**

| | SFINAE / tag dispatch | `if constexpr` |
|---|---|---|
| Definitions needed | One overload per case, or helper traits | One function template |
| Readability | Indirection through `enable_if` / dispatchers | Linear, top-to-bottom |
| Dead branch | Removed from candidate set | Removed from binary per instantiation |
| Body type-safety | Each overload type-checks fully | Dead branch needs only syntactic validity |

`if constexpr` (C++17) is the modern replacement when the dispatching dimension
is "a property of `T`" (size, trait, category). Tag dispatch is still relevant
when the dispatching dimension is "caller intent" (which path do I want?) — see
section 2.

---

## Build & verify

```bash
cd artefacts/cpp-crash-course/phase-3/
g++ -std=c++17 -Wall -Wextra template_playground.cpp -o tp
./tp
```

Expected: clean compile (zero warnings), run produces visible output for each
of the four sections, exits 0.

Stretch verification — break and observe the build fail:

1. Add a `std::string` member to the packed struct → expect
   `static_assert failed: "must be memcpy-safe"`.
2. Reorder the struct fields → expect
   `static_assert failed: "wire format drift"`.
3. Call `byteswap(double{3.14})` → expect
   `static_assert failed: "unsupported size"` (since `sizeof(double) == 8`,
   actually this would *succeed* through bswap64 — to see the assert fire,
   try `byteswap(char{'a'})` for `sizeof == 1`).
