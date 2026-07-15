# Quiz: Session 12 — Algorithms, Lambdas & Modern Iteration

**Date:** 2026-07-15
**Score:** 5.5 / 10 *(cold quiz — taken before the Session 12 Apply step)*

**Instructions:** 7 multiple-choice + 3 short-answer. Answers at the bottom.

---

### Q1. You're iterating a `std::vector<Order>` (Order is 64 bytes) on the hot path to compute a running total — read-only. Which loop form is right, and why?

A) `for (auto o : book)` — a fresh copy per element keeps the source safe from accidental writes
B) `for (auto& o : book)` — mutable reference, no copy, fastest since nothing is const-checked
C) `for (const auto& o : book)` — no copy, and read-only access is enforced by the compiler
D) `for (const auto o : book)` — a const copy per element; the const is what makes each copy cheap

---

### Q2. You register a lambda as a callback that fires on the *next* market-data tick — after the enclosing function has returned. The lambda needs the local variable `config`. Which capture is correct?

A) `[&]` — reference-capture everything; cheapest, and config stays current if it changes
B) `[config]` — copy config into the lambda so it has its own instance with independent lifetime
C) `[&config]` — reference only what's needed; tighter scope than `[&]`, same zero-copy cost
D) `[this]` — capture the enclosing object pointer so the lambda reads config through the member

---

### Q3. All four snippets compile cleanly and pass a small unit test. `Order::qty` and `Order::price` are both `int64_t` (price in ticks × 10⁸). One has a latent production bug — which?

A) `std::vector<int64_t> notionals(orders.size()); std::transform(orders.begin(), orders.end(), notionals.begin(), [](const Order& o) { return o.qty * o.price; });`
B) `auto it = std::find_if(orders.begin(), orders.end(), [](const Order& o) { return o.qty > 100; }); if (it != orders.end()) process(*it);`
C) `std::sort(orders.begin(), orders.end(), [](const Order& a, const Order& b) { return a.price > b.price; });`
D) `auto total = std::accumulate(orders.begin(), orders.end(), 0, [](int64_t acc, const Order& o) { return acc + o.qty * o.price; });`

---

### Q4. You keep bid price levels in an ascending sorted `std::vector<int64_t>`. Given a target price, you need an iterator to the first level ≥ target (or `end()` if none). Which call does exactly that?

A) `std::lower_bound(v.begin(), v.end(), target)` — first element not less than target, O(log N)
B) `std::upper_bound(v.begin(), v.end(), target)` — first element greater than target, O(log N)
C) `std::find_if(v.begin(), v.end(), […]{ return x >= target; })` — first match scanning forward
D) `std::binary_search(v.begin(), v.end(), target)` — O(log N) membership test on sorted data

---

### Q5. `Order` has a constructor `Order(uint64_t id, int64_t px, int64_t qty)`. You already hold a fully-constructed `Order o` and want it appended to `std::vector<Order> book`. Which is the right call, and why?

A) `book.emplace_back(o)` — emplace always constructs in place, so it skips the copy push_back would make
B) `book.emplace_back(o.id, o.px, o.qty)` — re-constructing from members avoids touching o
C) `book.push_back(std::move(o))` — moving is mandatory since a plain copy reallocates
D) `book.push_back(o)` — with an existing object there's nothing to construct in place; both calls copy, push_back states it plainly

---

### Q6. Which statement about `std::move(x)` itself is accurate?

A) It's a cast — marks x as an rvalue, eligible to be moved from; the receiving function decides whether a move or copy actually happens
B) It transfers x's resources to the destination immediately, at the call site, before the receiving function runs
C) It resets x to its default-constructed state, which is what makes the transfer safe and guaranteed
D) It tells the compiler x can be copied bytewise with memcpy instead of running the copy constructor

---

### Q7. `std::unordered_map<uint64_t, OrderState> orders;` You run `auto [it, inserted] = orders.emplace(id, state);` — but `id` is already a key in the map. What state are things in afterwards?

A) `inserted == true` and the map's value for id has been replaced with the new state
B) `inserted == false` to signal the collision, but the value was still updated to the new state
C) `inserted == false`, the existing value is unchanged, and `it` points at that existing entry
D) emplace on a duplicate key raises an exception since uniqueness would be violated

---

### Q8 (short answer). A colleague writes lambdas with `[&]` everywhere because "it's the cheapest capture." Explain the difference between capture-by-value (`[=]`/`[x]`) and capture-by-reference (`[&]`/`[&x]`), and give a practical rule for when each is the safe choice.

**Rubric:** (1) `[&]` = references, no copy, but the lambda must not outlive the captured scope; (2) `[=]`/`[x]` = copies at creation → independent lifetime, safe for stored/deferred callbacks; (3) rule: `[&]` for short-lived in-place lambdas (comparators, `for_each`), copy-capture for anything that outlives the scope.

---

### Q9 (short answer). Unsorted `std::vector<Trade> trades`; `qty` and `price` are `int64_t` (price in ticks × 10⁸). Compute the total notional (qty × price) of only trades with qty > 100 using standard algorithms. Sketch the approach and name the one numeric trap to avoid.

**Rubric:** (1) `std::accumulate` with a conditional lambda (or equivalent composition, e.g. `transform_reduce`); (2) predicate qty > 100 inside the fold; (3) the seed must be typed `int64_t{0}` — a bare `0` deduces `int` as the accumulator type and silently overflows/truncates.

---

### Q10 (short answer). After `std::string s = "ADDORDER"; names.push_back(std::move(s));` — what operations are you still allowed to do with `s`, what assumption is now illegal, and what is the standard's term for the state `s` is in?

**Rubric:** (1) allowed: assign, destruct, reuse — any operation without preconditions; (2) illegal: reading `s` and assuming the original contents survive; (3) term: **valid but unspecified** (typically empty for `std::string`, but never rely on it).

---

## Answers & result (2026-07-15)

| Q | Correct | Joe | Result |
|---|---|---|---|
| 1 | C | C | ✓ |
| 2 | B | C | ✗ — reference-captured a local that dies before the deferred callback fires (dangling → UB) |
| 3 | D | B | ✗ — missed the untyped `0` seed deducing `int` as accumulate's accumulator type |
| 4 | A | C | ✗ — `find_if` works but is O(N); `lower_bound` gives the same iterator in O(log N) on sorted data |
| 5 | D | C | ✗ — `std::move` on an all-integer type buys nothing (move == copy) and the "copy reallocates" rationale is false |
| 6 | A | A | ✓ |
| 7 | C | C | ✓ |
| 8 | rubric 3/3 | — | ✓ full credit (concept from Q2 recovered in full) |
| 9 | rubric 3/3 | — | ✓ full credit — used `accumulate` with a typed `int64_t{0}` seed (Q3's trap, avoided) |
| 10 | rubric 2/3 | — | ◐ half credit — allowed ops + illegal assumption right; missed the term "valid but unspecified" |

**Weak areas to review before re-quiz:** the `*_bound` family as the reflex on sorted containers (Q4); the emplace_back/push_back rule of thumb — emplace for `T{args…}`, push_back for an existing `T` (Q5); "valid but unspecified" as the named moved-from contract (Q10).

**Note:** Q2's and Q3's concepts were re-tested in Q8/Q9 after feedback and both landed — treat those as learned-in-quiz, verify at the 7-day retrieval check.
