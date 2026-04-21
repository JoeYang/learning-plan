# Templates & Compile-Time Programming

How protocol code gets zero-runtime-cost polymorphism, type safety, and branching — all resolved before the binary ever runs.

> **The theme:** the compiler is a runtime you can program. Tell it what you know at build time, and it removes work, inserts checks, and specialises code — so the hot path has nothing left to decide.

---

## Templates — the parameterised unit

Two kinds you will see in protocol code:

```cpp
// Function template — one definition, many specialisations
template<typename T>
void handle(const T& msg);

// Class template — parameterised container or policy
template<typename Config>
class Parser { /* ... */ };
```

Each unique `T` instantiates a separate compiled function. No runtime dispatch — the call is as fast as a plain function call.

**Non-type parameters** let you parameterise on values too:

```cpp
template<size_t N>
struct FixedBuffer { char data[N]; };
```

`N` is a compile-time constant, suitable as an array size.

---

## CRTP — the hot-path pattern (Session 8 recap)

The "weird" template you keep seeing:

```cpp
template<typename Derived>
class Handler {
  void dispatch() {
    static_cast<Derived*>(this)->onMessage();  // compile-time bound
  }
};

class MyHandler : public Handler<MyHandler> {
  void onMessage() { /* ... */ }
};
```

- **Virtual dispatch:** vtable pointer + indirect call + potential cache miss (~3–5 ns)
- **CRTP dispatch:** resolved at compile time — inlined, zero overhead

The tell: a class inheriting from a template of itself. When you see `: public Base<Derived>`, you're looking at CRTP.

---

## Tag dispatch — compile-time labels

Empty structs used to select an overload at compile time:

```cpp
struct MarketDataTag {};
struct OrderEntryTag {};

void route(const Message& m, MarketDataTag);
void route(const Message& m, OrderEntryTag);

// Caller picks the branch by passing the tag type:
route(msg, MarketDataTag{});
```

**Why not an `if`?**
- `if` branches on a value at runtime — the wrong-branch code is still compiled and lives in the binary.
- Tag dispatch picks the overload at compile time — the unused function is never instantiated for that site.

Used in protocol routers when the message type is known at the call site (e.g., per-session handlers).

---

## Type traits — querying types at compile time

Compile-time introspection. Two common uses:

```cpp
// Is this type what I expect?
static_assert(std::is_trivially_copyable<AddOrder>::value,
              "AddOrder must be memcpy-safe");

// Pick behaviour based on type:
if constexpr (std::is_integral_v<T>) { /* byteswap path */ }
else                                 { /* passthrough path */ }
```

Values end in `::value`; type-producing traits end in `::type`. C++17 adds `_v` and `_t` shortcuts.

---

## Traits you'll actually see

| Trait | Asks |
|---|---|
| `std::is_same<T, U>` | T and U the same type? |
| `std::is_integral<T>` | `int` / `long` / `bool` etc.? |
| `std::is_trivially_copyable<T>` | safe to `memcpy`? |
| `std::is_base_of<B, D>` | D inherits from B? |
| `std::is_pointer<T>` | T a pointer? |
| `std::remove_cv<T>::type` | T stripped of `const` / `volatile` |

Used extensively in protocol code to validate wire-format assumptions at build time — a bad trait assertion means a failed build, not a runtime crash during trading hours.

---

## SFINAE, `enable_if`, `decltype`

The old way to say "this function only exists for integral types":

```cpp
template<typename T,
         typename = std::enable_if_t<std::is_integral_v<T>>>
T byteswap(T x);
```

**SFINAE** — "Substitution Failure Is Not An Error." If substituting `T` into a template produces an invalid type, the compiler quietly removes that overload rather than erroring.

**`decltype(expr)`** — deduces the type of an expression without evaluating it. Useful in trailing return types and in generic wrappers:

```cpp
template<typename F, typename... A>
auto call(F f, A... a) -> decltype(f(a...));
```

These are still everywhere in older codebases. Modern code usually replaces them with `if constexpr` and concepts.

---

## `constexpr` and `static_assert` (Session 10)

**`constexpr`** — values and functions evaluated at compile time:

```cpp
constexpr size_t MSG_SIZE = 36;

constexpr uint32_t tag(char a, char b, char c, char d) {
  return (a << 24) | (b << 16) | (c << 8) | d;
}
```

**`static_assert`** — a compile-time check. Build fails, not runtime:

```cpp
static_assert(sizeof(AddOrder) == 36, "wire format changed");
static_assert(std::is_trivially_copyable_v<AddOrder>);
```

**`const` vs `constexpr`:** `const` just means "not modified after init" — value can come from a variable. `constexpr` means "known at compile time" — the compiler guarantees it.

---

## `if constexpr` — the modern branch

C++17's answer to SFINAE and tag-dispatch-for-simple-cases:

```cpp
template<typename T>
T byteswap(T x) {
  if constexpr (sizeof(T) == 2) return __builtin_bswap16(x);
  else if constexpr (sizeof(T) == 4) return __builtin_bswap32(x);
  else if constexpr (sizeof(T) == 8) return __builtin_bswap64(x);
  else static_assert(false, "unsupported size");
}
```

**The key difference from a regular `if`:** the dead branch is *not compiled* for that instantiation. No code bloat, no compile errors from unreachable code, no runtime check.

This collapses three SFINAE overloads into one readable function. Most modern protocol code prefers this over `enable_if` whenever the branch is a simple compile-time predicate.

---

<!-- class: is-dark -->

# Phase 3 takeaways

Five ideas to carry forward:

1. **Templates compile once per unique type** — each instantiation is its own function, selected at compile time.
2. **CRTP replaces virtual calls** when the derived type is known at compile time — zero overhead, no vtable.
3. **Tag dispatch and type traits** give the compiler enough information to pick the right path without runtime branches.
4. **`static_assert`** is your wire-format safety net — fail the build, not the market open.
5. **`if constexpr`** is the modern replacement for most SFINAE — same compile-time branching, vastly more readable.

**Where does the work live? With the compiler — given enough type information to resolve it all before the binary ships.**
