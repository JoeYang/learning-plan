# Day 6 (Tue Apr 14) — DS&A III: Advanced Patterns

## Overview (5 min)

This session covers three advanced algorithmic pattern families: dynamic programming, bit manipulation, and stack/queue patterns. Dynamic programming is a staple of coding interviews at any top firm. Bit manipulation is specifically tested at Jump Trading — working with low-level binary representations is directly relevant to systems programming, protocol parsing, and hardware interaction. Monotonic stacks and sliding window maximums appear in both interviews and real-time data processing.

---

## Reading Materials (60-90 min)

### 1. Dynamic Programming

Dynamic programming (DP) solves problems by breaking them into overlapping subproblems and storing the results to avoid recomputation. It applies when a problem has:

1. **Optimal substructure:** The optimal solution contains optimal solutions to subproblems
2. **Overlapping subproblems:** The same subproblems are solved repeatedly

#### Memoization vs Tabulation

**Memoization (top-down):** Write the recursive solution, then cache results. The recursion tree is pruned because cached subproblems return immediately.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

**Tabulation (bottom-up):** Build a table iteratively, starting from the smallest subproblems. No recursion — avoids stack overflow for large inputs.

```python
def fib(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

**Trade-offs:**
- Memoization: easier to write (just add caching to recursive solution), only computes needed subproblems, but has function call overhead and risks stack overflow
- Tabulation: iterative (no stack overflow), can optimize space (only keep needed rows), but computes all subproblems even if not needed

#### The DP Framework

For any DP problem, define:
1. **State:** What variables define a subproblem? (e.g., index, remaining capacity, ...)
2. **Transition:** How does the current state relate to previous states? (the recurrence relation)
3. **Base case:** What are the trivial subproblems?
4. **Answer:** Which state contains the final answer?

#### Classic Problem: 0/1 Knapsack

**Problem:** Given items with weights and values, maximize total value without exceeding weight capacity W.

**State:** `dp[i][w]` = maximum value using first i items with capacity w

**Transition:**
```
dp[i][w] = max(
    dp[i-1][w],                    # Don't take item i
    dp[i-1][w - weight[i]] + value[i]  # Take item i (if weight[i] <= w)
)
```

**Base case:** `dp[0][w] = 0` for all w (no items = no value)

```python
def knapsack(weights, values, W):
    n = len(weights)
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(W + 1):
            dp[i][w] = dp[i-1][w]  # Don't take item i
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w],
                              dp[i-1][w - weights[i-1]] + values[i-1])

    return dp[n][W]
```

**Time:** O(n * W). **Space:** O(n * W), reducible to O(W) since each row only depends on the previous row.

**Space optimization:**
```python
def knapsack_optimized(weights, values, W):
    dp = [0] * (W + 1)
    for i in range(len(weights)):
        for w in range(W, weights[i] - 1, -1):  # Reverse to avoid using same item twice
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[W]
```

Note the reverse iteration: if we went forward, `dp[w - weights[i]]` might use the updated value from this iteration (effectively allowing unlimited copies of item i — that's the unbounded knapsack variant).

**Trading analogy:** Portfolio optimization — select assets (items) with expected returns (values) constrained by risk budget (weight capacity).

#### Classic Problem: Longest Increasing Subsequence (LIS)

**Problem:** Find the length of the longest strictly increasing subsequence.

**State:** `dp[i]` = length of LIS ending at index i

**Transition:** `dp[i] = max(dp[j] + 1)` for all j < i where `nums[j] < nums[i]`

**Base case:** `dp[i] = 1` (each element is an LIS of length 1)

```python
def lis(nums):
    n = len(nums)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

**Time:** O(n^2). **Space:** O(n).

**O(n log n) approach using patience sorting:**
```python
import bisect

def lis_fast(nums):
    tails = []  # tails[i] = smallest tail element for LIS of length i+1
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)
```

**Why it works:** `tails` is always sorted. For each new element, we either extend the longest LIS (append) or replace an element to keep a smaller tail (enabling longer future sequences). Binary search on `tails` gives O(log n) per element.

#### Classic Problem: Grid Paths / Minimum Path Sum

**Problem:** Find the minimum cost path from top-left to bottom-right in a grid, moving only right or down.

```python
def min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = grid[0][0]

    for i in range(1, m):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    for j in range(1, n):
        dp[0][j] = dp[0][j-1] + grid[0][j]

    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])

    return dp[m-1][n-1]
```

#### Coin Change

**Problem:** Given coin denominations, find the minimum number of coins to make a target amount.

```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1

    return dp[amount] if dp[amount] != float('inf') else -1
```

**Time:** O(amount * len(coins)). **Space:** O(amount).

### 2. Bit Manipulation

Bit manipulation operates on the binary representation of integers. This is a core skill at Jump Trading because trading systems work directly with binary protocols, hardware registers, flags, and compact data representations.

#### Binary Basics

```
Decimal  Binary     Hex
0        0000 0000  0x00
1        0000 0001  0x01
5        0000 0101  0x05
10       0000 1010  0x0A
255      1111 1111  0xFF
```

#### Bitwise Operators

| Operator | Symbol | Description | Example (a=5=101, b=3=011) |
|---|---|---|---|
| AND | `&` | Both bits 1 | `5 & 3 = 1` (001) |
| OR | `\|` | Either bit 1 | `5 \| 3 = 7` (111) |
| XOR | `^` | Exactly one bit 1 | `5 ^ 3 = 6` (110) |
| NOT | `~` | Flip all bits | `~5 = -6` (two's complement) |
| Left shift | `<<` | Shift left, fill 0s | `5 << 1 = 10` (1010) |
| Right shift | `>>` | Shift right | `5 >> 1 = 2` (10) |

#### Two's Complement

Negative numbers in binary use two's complement: flip all bits and add 1.

```
 5 in 8-bit:  0000 0101
~5:           1111 1010
-5 = ~5 + 1: 1111 1011
```

**Key property:** `-x = ~x + 1`, or equivalently `~x = -x - 1`.

**Range for n-bit signed integer:** -2^(n-1) to 2^(n-1) - 1. For 32-bit: -2,147,483,648 to 2,147,483,647.

#### Essential Bit Tricks

**Check if a number is even/odd:**
```python
is_odd = (n & 1) == 1    # Last bit is 1 for odd numbers
is_even = (n & 1) == 0
```

**Check if a number is a power of 2:**
```python
is_power_of_two = n > 0 and (n & (n - 1)) == 0
```
Why: A power of 2 has exactly one bit set (e.g., 8 = 1000). `n-1` flips that bit and all lower bits (7 = 0111). AND produces 0.

**Get/set/clear/toggle a specific bit:**
```python
# Get bit at position i
bit = (n >> i) & 1

# Set bit at position i
n = n | (1 << i)

# Clear bit at position i
n = n & ~(1 << i)

# Toggle bit at position i
n = n ^ (1 << i)
```

**Count the number of set bits (population count / Hamming weight):**
```python
def count_bits(n):
    count = 0
    while n:
        n &= (n - 1)  # Clear lowest set bit
        count += 1
    return count
```
The trick `n & (n-1)` clears the lowest set bit. Each iteration removes one bit, so this runs in O(number of set bits) time, not O(total bits).

In Python: `bin(n).count('1')` or the built-in `int.bit_count()` (3.10+).

**Isolate the lowest set bit:**
```python
lowest_bit = n & (-n)  # Uses two's complement
```
Example: n = 12 = 1100. `-n` = 0100 (two's complement). `n & -n` = 0100 = 4.

#### XOR Tricks

XOR has special properties:
- `a ^ 0 = a` (identity)
- `a ^ a = 0` (self-inverse)
- Commutative and associative

**Find the single number (all others appear twice):**
```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result
```
Pairs cancel out: `a ^ b ^ a = b`. Only the unpaired number survives.

**Swap two numbers without a temporary variable:**
```python
a ^= b
b ^= a
a ^= b
# Now a and b are swapped
```

**Trading context for bit manipulation:**
- **Flags and bitmasks:** Order attributes (buy/sell, day/GTC, limit/market) stored as bit flags in a compact integer
- **Protocol parsing:** FIX/FAST binary protocols encode fields in bitwise-packed formats
- **Hardware interaction:** FPGA registers are read/written using bit operations
- **Hash functions:** Many hash functions use XOR, shifts, and masks internally
- **Set operations:** Represent a small set as a bitmask where each bit represents membership

#### Bitmask DP

When the state space is a set of N items (N <= 20), represent each subset as an integer bitmask. This enables DP over all 2^N subsets.

```python
# Example: Traveling Salesman Problem (TSP) with bitmask DP
def tsp(dist, n):
    """Find minimum cost to visit all n cities starting from city 0."""
    INF = float('inf')
    # dp[mask][i] = min cost to reach city i having visited cities in mask
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0  # Start at city 0

    for mask in range(1 << n):
        for u in range(n):
            if dp[mask][u] == INF:
                continue
            for v in range(n):
                if mask & (1 << v):  # Already visited
                    continue
                new_mask = mask | (1 << v)
                dp[new_mask][v] = min(dp[new_mask][v],
                                      dp[mask][u] + dist[u][v])

    full_mask = (1 << n) - 1
    return min(dp[full_mask][i] + dist[i][0] for i in range(n))
```

#### Reverse Bits

```python
def reverse_bits(n):
    """Reverse all 32 bits of an unsigned integer."""
    result = 0
    for i in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result
```

### 3. Stack and Queue Patterns

#### Monotonic Stack

A **monotonic stack** maintains elements in sorted order (either increasing or decreasing). When a new element violates the monotonicity, elements are popped until the invariant is restored.

**Key insight:** A monotonic stack efficiently finds the "next greater element" or "next smaller element" for every position in an array.

**Next Greater Element:**
```python
def next_greater(nums):
    """For each element, find the first greater element to its right."""
    n = len(nums)
    result = [-1] * n
    stack = []  # Stack of indices, values are decreasing

    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result

# Example: [2, 1, 2, 4, 3]
# Result:  [4, 2, 4, -1, -1]
```

**Why O(n):** Each element is pushed once and popped at most once. Total operations: 2n = O(n).

**Daily Temperatures (LC #739):**
```python
def daily_temperatures(temps):
    """Days until a warmer temperature."""
    n = len(temps)
    result = [0] * n
    stack = []  # Decreasing stack of indices

    for i in range(n):
        while stack and temps[stack[-1]] < temps[i]:
            idx = stack.pop()
            result[idx] = i - idx
        stack.append(i)

    return result
```

**Largest Rectangle in Histogram:** Another classic monotonic stack problem — for each bar, find how far left and right it extends as the minimum height.

**Trading context:** Monotonic stacks compute rolling maximums/minimums over sliding windows (though the explicit sliding window maximum uses a deque, discussed next). They also appear in matching engine logic — finding the first order at a better price.

#### Sliding Window Maximum (Monotonic Deque)

**Problem:** Given an array and window size k, find the maximum in each window.

Brute force: O(nk). Monotonic deque: O(n).

```python
from collections import deque

def max_sliding_window(nums, k):
    """Maximum in each window of size k."""
    dq = deque()  # Stores indices. Values at these indices are decreasing.
    result = []

    for i in range(len(nums)):
        # Remove elements outside the window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove elements smaller than current (they'll never be the max)
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()

        dq.append(i)

        if i >= k - 1:
            result.append(nums[dq[0]])  # Front of deque is the max

    return result
```

**Why it works:** The deque maintains a decreasing sequence of "candidates." The front is always the current maximum. When a new element arrives that's larger than the back, it evicts smaller elements (they can never be the maximum of any future window). Elements that fall out of the window are removed from the front.

**Each element enters and leaves the deque at most once: O(n) total.**

**Trading context:** Real-time rolling maximum/minimum for risk monitoring. "What's the highest price in the last 100 ticks?" is exactly this problem. Also used for circuit breaker detection — "has the price moved more than X% from the rolling max in the last N ticks?"

#### Stack-Based Expression Evaluation

Stacks naturally evaluate expressions: operands are pushed, operators pop operands and push results. This pattern appears in any system that parses and evaluates expressions (trading strategy configuration, risk rule engines).

```python
def eval_rpn(tokens):
    """Evaluate Reverse Polish Notation."""
    stack = []
    ops = {'+': lambda a,b: a+b, '-': lambda a,b: a-b,
           '*': lambda a,b: a*b, '/': lambda a,b: int(a/b)}

    for token in tokens:
        if token in ops:
            b, a = stack.pop(), stack.pop()
            stack.append(ops[token](a, b))
        else:
            stack.append(int(token))

    return stack[0]
```

---

## Practice Questions (20-30 min)

1. **Explain the difference between memoization and tabulation. When would you prefer one over the other? Discuss stack overflow concerns.**

2. **Walk through the 0/1 Knapsack problem. Explain the state, transition, and how to optimize space from O(nW) to O(W). Why do we iterate weights in reverse?**

3. **Explain how `n & (n-1)` clears the lowest set bit. Why is this useful for counting set bits? What's the time complexity?**

4. **What is two's complement? How does it represent negative numbers? Why is `-x = ~x + 1`?**

5. **Explain the monotonic stack pattern. How does it find the "next greater element" for all positions in O(n)?**

6. **Walk through the sliding window maximum using a monotonic deque. Why is this O(n) despite the nested while loops?**

7. **Design a bitmask to represent order types (market, limit, stop, stop-limit, IOC, FOK, GTC, DAY). How would you check if an order is both limit and IOC?**

8. **Explain the LIS problem and both the O(n^2) and O(n log n) solutions. Why does the patience sorting approach work?**

9. **You need to find the single number in an array where every other number appears exactly three times. XOR alone won't work. How would you solve this?**

10. **Compare the Coin Change problem to the 0/1 Knapsack. How does the "unlimited supply" of coins change the iteration order?**

---

## Quiz (20 questions)

### Multiple Choice

**Q1.** Dynamic programming requires which two properties?
- (A) Greedy choice and optimal substructure
- (B) Overlapping subproblems and optimal substructure
- (C) Divide and conquer and memoization
- (D) Backtracking and pruning

**Q2.** What does `n & (n-1)` do?
- (A) Sets the lowest bit
- (B) Clears all bits
- (C) Clears the lowest set bit
- (D) Counts the number of bits

**Q3.** In the 0/1 Knapsack space-optimized solution, we iterate weights in reverse because:
- (A) It's faster
- (B) It prevents using the same item twice in one iteration
- (C) It reduces the number of iterations
- (D) Python requires reverse iteration for lists

**Q4.** The XOR of all elements in `[3, 5, 3, 7, 5]` is:
- (A) 0
- (B) 7
- (C) 3
- (D) 5

**Q5.** A monotonic decreasing stack pops an element when:
- (A) The stack is empty
- (B) A smaller element arrives
- (C) A larger element arrives
- (D) The array ends

**Q6.** The time complexity of the O(n log n) LIS algorithm is achieved by:
- (A) Sorting the array first
- (B) Using binary search on a tails array
- (C) Using a hash table
- (D) Using divide and conquer

**Q7.** `5 ^ 3` equals:
- (A) 2
- (B) 6
- (C) 7
- (D) 8

**Q8.** The Coin Change problem (minimum coins for amount) uses:
- (A) Greedy algorithm
- (B) Dynamic programming
- (C) Binary search
- (D) Backtracking

**Q9.** In the sliding window maximum with a monotonic deque, the deque stores:
- (A) Values in increasing order
- (B) Indices with values in decreasing order
- (C) All elements in the current window
- (D) Only the maximum value

**Q10.** `n & (-n)` isolates:
- (A) The highest set bit
- (B) The lowest set bit
- (C) All even bits
- (D) All odd bits

**Q11.** To check if bit position 3 is set in n, you use:
- (A) `n & 3`
- (B) `n & (1 << 3)`
- (C) `n | (1 << 3)`
- (D) `n ^ 3`

**Q12.** The space complexity of the standard Coin Change DP solution for amount A is:
- (A) O(1)
- (B) O(A)
- (C) O(A^2)
- (D) O(n * A) where n is number of coin types

### Short Answer

**Q13.** Trace through the Coin Change algorithm for coins = [1, 3, 4] and amount = 6.

**Q14.** Explain why `is_power_of_two = n > 0 and (n & (n-1)) == 0` works. Give two examples.

**Q15.** Given the array [73, 74, 75, 71, 69, 72, 76, 73], trace through the Daily Temperatures monotonic stack solution.

**Q16.** How would you use bitmask DP to solve a problem with 15 items where you need to find the optimal subset? What is the time and space complexity?

**Q17.** Explain why the brute-force sliding window maximum is O(nk) while the deque approach is O(n). What invariant does the deque maintain?

**Q18.** Reverse the bits of the 8-bit number 10110010. Show your work.

**Q19.** In the LIS patience sorting approach, what does the `tails` array represent? Why is it always sorted?

**Q20.** How would you represent a chess board's occupied squares using a bitmask? How many bits do you need?

---

## Quiz Answer Key

**Q1: (B)** Overlapping subproblems (same subproblems recur) and optimal substructure (optimal solution is built from optimal solutions to subproblems). Greedy choice is for greedy algorithms, not DP.

**Q2: (C)** `n-1` flips the lowest set bit and all bits below it. ANDing with n clears the lowest set bit and everything below, keeping all higher bits. Example: n=12 (1100), n-1=11 (1011), n&(n-1)=8 (1000).

**Q3: (B)** Forward iteration would let `dp[w]` use the updated `dp[w - weight[i]]` from the same iteration, effectively allowing item i to be taken multiple times. Reverse iteration ensures we use values from the previous iteration (i.e., without item i), enforcing the 0/1 constraint.

**Q4: (B)** `3^5^3^7^5` = `(3^3)^(5^5)^7` = `0^0^7` = `7`. Pairs cancel to 0, leaving only the unpaired element.

**Q5: (C)** A monotonic decreasing stack maintains the invariant that elements decrease from bottom to top. When a larger element arrives, all smaller elements on top are popped (they've found their "next greater element").

**Q6: (B)** The `tails` array is maintained in sorted order. For each new element, binary search (`bisect_left`) finds where it fits in O(log n). Over n elements: O(n log n).

**Q7: (B)** 5 = 101, 3 = 011. XOR: 110 = 6. XOR produces 1 where bits differ.

**Q8: (B)** The greedy approach (always take the largest coin) doesn't work for all coin systems. For example, coins = [1, 3, 4], amount = 6: greedy gives 4+1+1 = 3 coins, but optimal is 3+3 = 2 coins. DP explores all possibilities.

**Q9: (B)** The deque stores indices whose corresponding values are in decreasing order. This ensures the front of the deque is always the index of the maximum in the current window. Indices of smaller values are evicted from the back when a larger value arrives.

**Q10: (B)** In two's complement, `-n` flips all bits and adds 1. The result shares only the lowest set bit with `n`. Example: n=12=1100, -n=0100. n & (-n) = 0100 = 4 (the lowest set bit).

**Q11: (B)** `1 << 3` creates a mask with only bit 3 set (= 8 = 1000). `n & (1 << 3)` is nonzero if and only if bit 3 of n is set. Note: `n & 3` would check bits 0 AND 1, which is wrong.

**Q12: (B)** The DP table has `A + 1` entries (from 0 to A). For each entry, we check all coin types, but the table itself is O(A). Total time is O(A * n), but space is O(A).

**Q13:**
```
coins = [1, 3, 4], amount = 6
dp = [0, inf, inf, inf, inf, inf, inf]

i=1: min(inf, dp[0]+1) = 1  -> dp = [0, 1, inf, inf, inf, inf, inf]
i=2: min(inf, dp[1]+1) = 2  -> dp = [0, 1, 2, inf, inf, inf, inf]
i=3: min(inf, dp[2]+1)=3, min(3, dp[0]+1)=1 -> dp = [0, 1, 2, 1, inf, inf, inf]
i=4: min(inf, dp[3]+1)=2, min(2, dp[1]+1)=2, min(2, dp[0]+1)=1 -> dp = [0, 1, 2, 1, 1, inf, inf]
i=5: min(inf, dp[4]+1)=2, min(2, dp[2]+1)=2 -> dp = [0, 1, 2, 1, 1, 2, inf]
i=6: min(inf, dp[5]+1)=3, min(3, dp[3]+1)=2, min(2, dp[2]+1)=3 -> dp = [0, 1, 2, 1, 1, 2, 2]
```
Answer: 2 coins (3 + 3).

**Q14:** A power of 2 has exactly one bit set: 1=1, 2=10, 4=100, 8=1000, etc. `n-1` flips that bit and sets all lower bits: 8=1000, 7=0111. `n & (n-1)` = 0. For a non-power: 6=110, 5=101, `6&5` = 100 != 0. The `n > 0` check handles n=0, which has no bits set but isn't a power of 2.

**Q15:**
```
Temps: [73, 74, 75, 71, 69, 72, 76, 73]
Stack (indices): result initialized to [0,0,0,0,0,0,0,0]

i=0: push 0. Stack: [0]
i=1: 74>73, pop 0, result[0]=1-0=1. Push 1. Stack: [1]
i=2: 75>74, pop 1, result[1]=2-1=1. Push 2. Stack: [2]
i=3: 71<75, push 3. Stack: [2,3]
i=4: 69<71, push 4. Stack: [2,3,4]
i=5: 72>69, pop 4, result[4]=5-4=1. 72>71, pop 3, result[3]=5-3=2. 72<75, push 5. Stack: [2,5]
i=6: 76>72, pop 5, result[5]=6-5=1. 76>75, pop 2, result[2]=6-2=4. Push 6. Stack: [6]
i=7: 73<76, push 7. Stack: [6,7]

Result: [1, 1, 4, 2, 1, 1, 0, 0]
```

**Q16:** With 15 items, there are 2^15 = 32,768 possible subsets. Use an integer bitmask from 0 to 32767 to represent each subset. For each subset, compute the optimal value using DP transitions that add one item to the subset. Time: O(2^N * N). Space: O(2^N). This is exponential but feasible for N <= 20 (~1 million subsets).

**Q17:** Brute force: for each of n-k+1 windows, scan k elements to find the max = O(nk). Deque approach: each element is added to the deque once and removed at most once, so total operations across all windows is 2n = O(n). The deque maintains the invariant that elements (at their indices) are in decreasing order of value. The front is always the maximum of the current window. Elements smaller than the incoming element are useless (they'll never be the max), so they're evicted from the back.

**Q18:** 10110010 reversed: read right to left = 01001101.
Step by step: bit 7->0, bit 6->1, bit 5->2, etc.
Original: 1 0 1 1 0 0 1 0
Reversed: 0 1 0 0 1 1 0 1 = 01001101 = 77 in decimal.

**Q19:** `tails[i]` holds the smallest possible tail element among all increasing subsequences of length `i+1`. It's always sorted because: if we have an LIS of length 3 ending in 5, then we can always find an LIS of length 2 ending in something <= 5 (just remove the last element). So `tails[i] <= tails[i+1]`. This sortedness enables binary search for each insertion.

**Q20:** A chess board has 64 squares. Use a 64-bit integer (uint64) where bit i represents whether square i is occupied. Operations: check if square i is occupied: `board & (1 << i)`. Place a piece: `board |= (1 << i)`. Remove: `board &= ~(1 << i)`. This is how chess engines (Stockfish, etc.) represent boards — called "bitboards." Bitwise operations on bitboards enable extremely fast move generation and evaluation.

---

## Coding Practice (Outside 2-hour budget)

### Problem List

1. **Coin Change** (LC #322) — Bottom-up DP
   - Key insight: `dp[amount]` = min coins, try each coin denomination
   - Time: O(amount * coins), Space: O(amount)

2. **Longest Increasing Subsequence** (LC #300) — DP or patience sorting
   - O(n^2) DP or O(n log n) with binary search on tails array

3. **Single Number** (LC #136) — XOR all elements
   - Key insight: `a ^ a = 0`, so all pairs cancel out

4. **Reverse Bits** (LC #190) — Bit-by-bit reversal
   - Key insight: Extract lowest bit, shift result left, shift n right, repeat 32 times

5. **Daily Temperatures** (LC #739) — Monotonic decreasing stack
   - Key insight: Stack stores indices of unresolved temperatures. Pop when warmer day found.

6. **Number of 1 Bits** (LC #191) — Brian Kernighan's algorithm
   - Key insight: `n &= (n-1)` clears lowest set bit. Count iterations.

### Special Emphasis: Bit Manipulation for Jump

Jump specifically tests bit manipulation. Practice these additional patterns:
- XOR to find missing/unique elements
- Bitmask to represent sets (subsets, power set enumeration)
- Bit shifts for multiplication/division by powers of 2
- Using bits to encode/decode compact data structures
- Understanding integer overflow and wraparound in fixed-width types
