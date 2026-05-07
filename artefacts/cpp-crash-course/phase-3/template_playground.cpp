// template_playground.cpp
//
// Phase 3 capstone for cpp-crash-course. Demonstrates four compile-time
// patterns side-by-side: CRTP, tag dispatch, static_assert-guarded POD,
// and if constexpr byteswap.
//
// Build:
//     g++ -std=c++17 -Wall -Wextra template_playground.cpp -o tp && ./tp
//
// Each section below has a TODO block. Fill them in, compile clean, run.

#include <cstdint>
#include <cstring>
#include <iostream>
#include <type_traits>

// ============================================================================
// 1. CRTP handler — compile-time polymorphism, no vtable
// ============================================================================
//
// TODO: Define a Base<Derived> class template with a `dispatch()` method
// that calls `static_cast<Derived*>(this)->onMessage()`. Then write a
// concrete `MyHandler : public Base<MyHandler>` that implements
// `onMessage()` and prints something visible from main.
//
// Verify: invoking `myHandler.dispatch()` runs MyHandler::onMessage()
// with no vtable indirection.

// (your code here)


// ============================================================================
// 2. Tag-dispatched router — same Message type, different paths picked by tag
// ============================================================================
//
// TODO: Two empty tag structs (e.g. FastPathTag, SafePathTag) and two
// overloads of `route()` taking a `const Message&` and a tag. From main,
// route the same message via both tags and observe each path runs.

struct Message {
    int payload;
};

// (your code here)


// ============================================================================
// 3. static_assert-guarded POD — wire-format safety net
// ============================================================================
//
// TODO: A packed protocol struct (use `__attribute__((packed))` for GCC)
// with at least 4 fields. Add:
//   - static_assert(sizeof(YourStruct) == EXPECTED_SIZE, "wire format drift")
//   - static_assert(std::is_trivially_copyable_v<YourStruct>, "must be memcpy-safe")
//
// Verify: removing a field or adding a std::string member breaks the build.

// (your code here)


// ============================================================================
// 4. if constexpr byteswap — modern replacement for SFINAE
// ============================================================================
//
// TODO: One function template `byteswap(T)` that selects the right intrinsic
// at compile time:
//   - sizeof(T) == 2 → __builtin_bswap16
//   - sizeof(T) == 4 → __builtin_bswap32
//   - sizeof(T) == 8 → __builtin_bswap64
//   - else           → static_assert(sizeof(T) == 0, "unsupported size")
// Use `if constexpr` chains; the dead branches will not be compiled per
// instantiation.

// (your code here)


// ============================================================================
// main — exercise each pattern with at least one observable test
// ============================================================================

int main() {
    std::cout << "=== Phase 3 Template Playground ===\n";

    // 1. CRTP: instantiate MyHandler, call dispatch(), see derived's print.
    // (your code here)

    // 2. Tag dispatch: route the same Message via both tags.
    // (your code here)

    // 3. static_assert POD: just declare one instance — the assertions ran
    //    at compile time, so reaching here means they passed.
    // (your code here)

    // 4. if constexpr byteswap: print three swap results so the values are
    //    visible (not optimised away).
    // (your code here)

    std::cout << "=== done ===\n";
    return 0;
}
