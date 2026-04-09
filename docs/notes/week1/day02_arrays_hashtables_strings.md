# Day 2 (Fri Apr 10) — DS&A I: Arrays, Hash Tables, Strings

## Overview (5 min)

Arrays, hash tables, and strings form the backbone of nearly every coding interview. At Jump Trading, expect to solve problems under time pressure that test not just your ability to get a working solution, but your understanding of why your solution is efficient. Interviewers want to hear you reason about cache locality, amortized costs, and space-time trade-offs. This session builds deep intuition for these fundamental structures and the algorithmic patterns built on top of them.

The 2-hour study budget focuses on conceptual mastery. LeetCode practice is listed separately at the end.

---

## Reading Materials (60-90 min)

### 1. Arrays: The Foundation

An array is a contiguous block of memory where elements are stored at fixed offsets. Given the base address and element size, any element can be accessed in O(1) via `base + index * element_size`.

**Properties:**
- O(1) random access (direct memory offset calculation)
- O(n) insertion/deletion at arbitrary position (shifting required)
- Excellent cache locality — sequential elements are adjacent in memory, so CPU cache lines load multiple elements at once

**Dynamic arrays** (Python's `list`, Java's `ArrayList`, C++'s `std::vector`) handle resizing by allocating a larger backing array and copying elements when capacity is exceeded. The growth factor (typically 1.5x or 2x) ensures that `append` is amortized O(1). The amortization argument: if you double the array at size n, you copy n elements, but this cost is "paid for" by the n insertions since the last resize — each insertion carries a constant extra cost.

**Trading context:** Market data tick arrays, order arrays, and time series are all array-based. Cache-friendly sequential access patterns are critical for performance. When processing a batch of 10,000 ticks, iterating a contiguous array is vastly faster than chasing pointers in a linked list.

#### Pattern: Two Pointers

The two-pointer technique uses two indices moving through an array, typically from opposite ends or at different speeds.

**When to use:** Sorted arrays, partitioning, palindromes, pair-finding.

**Classic example — Two Sum on a sorted array:**

```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        elif total < target:
            left += 1  # Need larger sum
        else:
            right -= 1  # Need smaller sum
    return []
```

**Why it works:** In a sorted array, moving the left pointer right increases the sum, moving the right pointer left decreases it. This eliminates possibilities systematically — O(n) time vs O(n^2) brute force.

**Same-direction two pointers (fast/slow):**

```python
def remove_duplicates(nums):
    """Remove duplicates in-place from sorted array."""
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[read - 1]:
            nums[write] = nums[read]
            write += 1
    return write
```

The "read" pointer scans forward, and the "write" pointer tracks where to place the next unique element.

#### Pattern: Sliding Window

A sliding window maintains a subarray/substring of dynamic or fixed size, adjusting the window boundaries to explore all valid configurations.

**Fixed-size window:**
```python
def max_sum_subarray(nums, k):
    """Maximum sum of subarray of size k."""
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # Slide: add right, remove left
        max_sum = max(max_sum, window_sum)
    return max_sum
```

**Variable-size window (shrink from left when condition violated):**
```python
def longest_substring_no_repeat(s):
    """Longest substring without repeating characters."""
    seen = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in seen and seen[char] >= left:
            left = seen[char] + 1
        seen[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```

**Key insight:** The sliding window converts an O(n^2) or O(n^3) brute force (checking all subarrays) into O(n) by only adjusting the window incrementally.

**Trading context:** Sliding windows compute rolling statistics — VWAP over the last N trades, moving averages, rolling max/min for risk limits. Understanding this pattern is directly applicable.

#### Pattern: Prefix Sums

A prefix sum array stores cumulative sums: `prefix[i] = nums[0] + nums[1] + ... + nums[i-1]`. The sum of any subarray `nums[i..j]` is then `prefix[j+1] - prefix[i]` in O(1).

```python
def build_prefix_sum(nums):
    prefix = [0] * (len(nums) + 1)
    for i in range(len(nums)):
        prefix[i + 1] = prefix[i] + nums[i]
    return prefix

def range_sum(prefix, i, j):
    """Sum of nums[i..j] inclusive."""
    return prefix[j + 1] - prefix[i]
```

**Trading context:** Computing cumulative P&L, running sums for TWAP calculations, or checking if any sub-period's loss exceeds a threshold.

#### Pattern: Kadane's Algorithm

Finds the maximum sum contiguous subarray in O(n). The idea: at each position, decide whether to extend the current subarray or start a new one.

```python
def max_subarray(nums):
    max_ending_here = max_so_far = nums[0]
    for num in nums[1:]:
        max_ending_here = max(num, max_ending_here + num)
        max_so_far = max(max_so_far, max_ending_here)
    return max_so_far
```

**Why it works:** `max_ending_here` tracks the best subarray ending at the current position. If the running sum becomes negative, it's better to start fresh — a negative prefix can only hurt.

**Trading context:** Finding the best consecutive trading period (maximum cumulative return over a contiguous window).

### 2. Hash Tables: O(1) Average Lookup

A hash table maps keys to values using a hash function to compute an index into a backing array of "buckets."

**Core operations:**
- `put(key, value)`: compute `hash(key) % capacity`, store at that bucket
- `get(key)`: compute `hash(key) % capacity`, retrieve from that bucket
- `delete(key)`: find and remove

**Hash function requirements:**
1. Deterministic — same key always produces same hash
2. Uniform distribution — spread keys evenly across buckets
3. Fast to compute

#### Collision Resolution

Since multiple keys can hash to the same bucket, we need a strategy:

**Separate chaining:** Each bucket contains a linked list (or another container). Colliding keys are appended to the list.
- Pros: Simple, degrades gracefully, deletion is easy
- Cons: Pointer chasing hurts cache performance, extra memory for linked list nodes

**Open addressing:** All entries stored in the array itself. On collision, probe for another slot.
- **Linear probing:** Check slots i, i+1, i+2, ... Causes "clustering" — consecutive occupied slots form clumps, making future probes longer.
- **Quadratic probing:** Check i, i+1, i+4, i+9, ... Reduces clustering but can fail to find empty slots.
- **Double hashing:** Use a second hash function for the probe step: `(hash1(key) + j * hash2(key)) % capacity`. Best distribution but more computation.

**Robin Hood hashing:** A variant of open addressing where entries can be displaced. If a new key has a longer probe distance than the current occupant, the occupant is displaced. This equalizes probe distances, reducing worst-case lookup time.

**Trading context:** Order ID lookups, symbol-to-instrument maps, and session state tables are all hash table operations on the hot path. Understanding collision behavior helps you choose the right implementation. In C++, `std::unordered_map` uses separate chaining; `absl::flat_hash_map` uses open addressing — the latter is often 2-3x faster due to cache locality.

#### Load Factor and Resizing

The **load factor** = number of entries / number of buckets. As load factor increases:
- More collisions occur
- Average probe length increases
- Performance degrades from O(1) toward O(n)

Typical load factor thresholds for resize:
- Separate chaining: 0.75 (Java HashMap)
- Open addressing: 0.5-0.7 (because clustering gets severe above 0.7)

**Resizing** involves:
1. Allocating a new array (typically 2x size)
2. Rehashing every entry (since the modulus changes)
3. This is O(n) but amortized O(1) per insert

**Amortized O(1) argument:** If the table doubles at size n, the O(n) rehash cost is spread across the n insertions since the last resize — each pays a constant extra cost.

#### Hash Table Analysis

| Operation | Average | Worst Case |
|---|---|---|
| Insert | O(1) amortized | O(n) during resize |
| Lookup | O(1) | O(n) with pathological hash |
| Delete | O(1) | O(n) |

Worst case O(n) happens when all keys hash to the same bucket (pathological hash function or adversarial input). In practice, with a good hash function, this almost never occurs.

### 3. Strings: Arrays of Characters

Strings are arrays with character-specific patterns. Key considerations:

**Immutability:** In Python (and Java), strings are immutable. Concatenating in a loop creates a new string each time — O(n^2) total:

```python
# BAD: O(n^2)
result = ""
for s in strings:
    result += s  # Creates new string each time

# GOOD: O(n)
result = "".join(strings)  # Allocates once
```

#### Pattern: Anagram Detection

Two strings are anagrams if they contain the same characters with the same frequencies.

**Approach 1 — Sort and compare: O(n log n)**
```python
def is_anagram(s, t):
    return sorted(s) == sorted(t)
```

**Approach 2 — Character frequency count: O(n)**
```python
from collections import Counter

def is_anagram(s, t):
    return Counter(s) == Counter(t)
```

**Approach 3 — Single pass with a frequency array (for lowercase English):**
```python
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    freq = [0] * 26
    for c in s:
        freq[ord(c) - ord('a')] += 1
    for c in t:
        freq[ord(c) - ord('a')] -= 1
    return all(f == 0 for f in freq)
```

#### Pattern: Substring Problems with Sliding Window

Many string problems reduce to "find an optimal substring satisfying a condition." The sliding window technique from arrays applies directly:

```python
def min_window(s, t):
    """Minimum window substring containing all characters of t."""
    from collections import Counter
    need = Counter(t)
    missing = len(t)
    left = 0
    best = (0, float('inf'))

    for right, char in enumerate(s):
        if need[char] > 0:
            missing -= 1
        need[char] -= 1

        while missing == 0:  # Window contains all chars of t
            if right - left < best[1] - best[0]:
                best = (left, right)
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1

    return s[best[0]:best[1]+1] if best[1] != float('inf') else ""
```

#### Pattern Matching

**Rabin-Karp:** Uses a rolling hash to compare substrings. Compute the hash of the pattern and slide a window across the text, updating the hash in O(1). If hashes match, verify character by character (to handle collisions).

```python
def rabin_karp(text, pattern):
    n, m = len(text), len(pattern)
    if m > n:
        return -1
    base, mod = 256, 10**9 + 7
    p_hash = t_hash = 0
    h = pow(base, m - 1, mod)

    for i in range(m):
        p_hash = (p_hash * base + ord(pattern[i])) % mod
        t_hash = (t_hash * base + ord(text[i])) % mod

    for i in range(n - m + 1):
        if p_hash == t_hash and text[i:i+m] == pattern:
            return i
        if i < n - m:
            t_hash = (t_hash * base - ord(text[i]) * h * base + ord(text[i + m])) % mod
            t_hash %= mod
    return -1
```

**KMP (Knuth-Morris-Pratt):** Preprocesses the pattern to build a "failure function" (longest proper prefix which is also a suffix), allowing the search to skip characters it has already matched. O(n + m) time, O(m) space.

**Trading context:** FIX message parsing involves searching for delimiters and extracting tag-value pairs. Fast string matching is essential when processing thousands of FIX messages per second.

### 4. Complexity Analysis Cheat Sheet

| Data Structure | Access | Search | Insert | Delete | Space |
|---|---|---|---|---|---|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| Dynamic Array (append) | O(1) | O(n) | O(1)* | O(n) | O(n) |
| Hash Table | - | O(1)* | O(1)* | O(1)* | O(n) |
| Sorted Array | O(1) | O(log n) | O(n) | O(n) | O(n) |

\* = amortized

---

## Practice Questions (20-30 min)

1. **Explain how a dynamic array achieves amortized O(1) append. If the growth factor were 1.1x instead of 2x, how would that affect amortized cost and memory waste?**

2. **You're given an unsorted array of trade prices and need to find all pairs that sum to a target. Compare the hash table approach vs. the sort + two pointers approach. Discuss time, space, and cache behavior.**

3. **Describe Robin Hood hashing. Why might it perform better than standard linear probing in practice? What's the impact on cache lines?**

4. **Walk through the sliding window technique for finding the longest substring without repeating characters. Why does the left pointer never move backward? What invariant does this maintain?**

5. **Explain prefix sums. Your trading system needs to answer "total volume between time T1 and T2" queries quickly across millions of ticks. How would prefix sums help? What's the time-space trade-off?**

6. **You're building an order book where you need to quickly look up orders by ID and also maintain price-time priority. What data structures would you combine and why?**

7. **Explain Kadane's algorithm. Can it be modified to also track the start and end indices of the maximum subarray? What about handling all-negative arrays?**

8. **Compare the Rabin-Karp and KMP string matching algorithms. When would you prefer one over the other?**

9. **A hash table has a load factor of 0.9. Why is this problematic for open addressing but less so for separate chaining?**

10. **Explain the "subarray sum equals K" problem approach using prefix sums and a hash map. Why is this more efficient than checking all O(n^2) subarrays?**

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** What is the amortized time complexity of `append()` on a dynamic array that doubles its capacity when full?
- (A) O(n)
- (B) O(log n)
- (C) O(1)
- (D) O(n log n)

**Q2.** In a hash table with open addressing and linear probing, what happens when the load factor approaches 1.0?
- (A) Operations remain O(1)
- (B) Probe sequences become very long, approaching O(n)
- (C) The table automatically resizes
- (D) Collisions are eliminated

**Q3.** The two-pointer technique on a sorted array finds a pair summing to a target in:
- (A) O(n^2)
- (B) O(n log n)
- (C) O(n)
- (D) O(log n)

**Q4.** Kadane's algorithm solves which problem?
- (A) Finding two elements that sum to a target
- (B) Finding the maximum sum contiguous subarray
- (C) Sorting an array in O(n) time
- (D) Finding the longest increasing subsequence

**Q5.** What is the space complexity of a prefix sum array for an input of size n?
- (A) O(1)
- (B) O(log n)
- (C) O(n)
- (D) O(n^2)

**Q6.** In separate chaining, what is the worst-case lookup time if all n keys hash to the same bucket?
- (A) O(1)
- (B) O(log n)
- (C) O(n)
- (D) O(n^2)

**Q7.** The sliding window technique reduces the brute-force complexity for substring problems from O(n^2) to:
- (A) O(n log n)
- (B) O(n)
- (C) O(log n)
- (D) O(1)

**Q8.** Which approach correctly solves "Subarray Sum Equals K"?
- (A) Sort the array and use binary search
- (B) Use prefix sums with a hash map of prefix sum frequencies
- (C) Use two pointers from both ends
- (D) Use Kadane's algorithm

**Q9.** Python string concatenation in a loop (`s += char`) is O(n^2) total because:
- (A) Python strings are mutable but slow
- (B) Each concatenation creates a new string object, copying all existing characters
- (C) The GIL prevents efficient string operations
- (D) Python doesn't support string concatenation

**Q10.** What is the expected number of probes for a successful lookup in a hash table with open addressing and load factor alpha?
- (A) 1 / (1 - alpha)
- (B) -ln(1 - alpha) / alpha
- (C) alpha
- (D) 1 + alpha

### Short Answer

**Q11.** You have an array `[2, 7, 11, 15]` and target 9. Walk through how the hash table approach for Two Sum works step by step.

**Q12.** Explain why the sliding window for "longest substring without repeating characters" is O(n) and not O(n^2), even though it has a nested loop (the left pointer advancement inside the main loop).

**Q13.** Given the array `[-2, 1, -3, 4, -1, 2, 1, -5, 4]`, trace through Kadane's algorithm showing `max_ending_here` and `max_so_far` at each step.

**Q14.** Why does a hash table with open addressing typically resize at a lower load factor (0.5-0.7) compared to separate chaining (0.75)?

**Q15.** Describe how to use a fixed-size array (instead of a hash map) to check if two strings are anagrams. When is this approach better than using a Counter?

**Q16.** What is the difference between Rabin-Karp's rolling hash and simply hashing every substring? What is the complexity improvement?

**Q17.** You need to find the maximum sum of any subarray of exactly size K. Describe the optimal approach and its complexity.

---

## Quiz Answer Key

**Q1: (C)** Amortized O(1). The doubling strategy means that after n insertions, the total cost of all copies is 1 + 2 + 4 + ... + n = 2n - 1, giving O(2n/n) = O(1) amortized per insertion.

**Q2: (B)** With linear probing, as load factor approaches 1.0, almost every slot is occupied. The average probe length for unsuccessful search is approximately 1/2 * (1 + (1/(1-alpha))^2), which grows dramatically as alpha approaches 1. This is why open addressing tables resize well before they're full.

**Q3: (C)** O(n). The two pointers start at opposite ends and each moves at most n steps total. This assumes the array is already sorted; if not, sorting adds O(n log n).

**Q4: (B)** Kadane's algorithm finds the contiguous subarray with the maximum sum in O(n) time and O(1) space.

**Q5: (C)** The prefix sum array has n+1 elements (including the 0-prefix), so O(n) space.

**Q6: (C)** If all n keys hash to the same bucket, the linked list at that bucket has length n. Searching through it is O(n).

**Q7: (B)** O(n). Each element is visited at most twice — once when the right pointer passes it, once when the left pointer passes it. Total work is 2n = O(n).

**Q8: (B)** Use prefix sums and a hash map. For each index i, compute `prefix_sum[i]` and check if `prefix_sum[i] - K` exists in the map (meaning some earlier prefix sum created a subarray summing to K). This is O(n) time, O(n) space.

**Q9: (B)** Python strings are immutable. `s += char` creates a new string of length len(s) + 1, copying all characters from the old string. Over n iterations: 1 + 2 + 3 + ... + n = O(n^2).

**Q10: (B)** For uniform hashing, the expected number of probes for a successful search is `(-ln(1-alpha))/alpha`. For unsuccessful search, it's `1/(1-alpha)`. Option (A) is the expected probes for an unsuccessful search.

**Q11:** Iterate through the array with a hash map `complement -> index`:
- i=0: num=2, need 9-2=7, map is empty, store {2:0}
- i=1: num=7, need 9-7=2, map has 2 at index 0. Return [0, 1].

**Q12:** The left pointer only moves forward — it never resets to the beginning. Across all iterations of the outer loop, the left pointer advances at most n times total. So the total work of the inner loop across all iterations is O(n). Combined with the outer loop's O(n), the total is O(n) + O(n) = O(n). This is the "amortized" argument — each element enters and leaves the window at most once.

**Q13:**
| Index | num | max_ending_here | max_so_far |
|---|---|---|---|
| 0 | -2 | -2 | -2 |
| 1 | 1 | 1 (start new) | 1 |
| 2 | -3 | -2 (extend) | 1 |
| 3 | 4 | 4 (start new) | 4 |
| 4 | -1 | 3 (extend) | 4 |
| 5 | 2 | 5 (extend) | 5 |
| 6 | 1 | 6 (extend) | 6 |
| 7 | -5 | 1 (extend) | 6 |
| 8 | 4 | 5 (extend) | 6 |
Answer: 6 (subarray [4, -1, 2, 1])

**Q14:** In open addressing, every collision forces a probe through occupied slots. High load means long probe chains, and probes access the shared backing array (contention with other operations). In separate chaining, a high load factor means longer linked lists per bucket, but each chain is independent. Open addressing also suffers from "clustering" where occupied runs grow and merge, making the degradation super-linear.

**Q15:** Allocate an array of size 26 (for lowercase English letters). Increment `freq[ord(c) - ord('a')]` for each character in string 1, decrement for string 2. If all values are 0, they're anagrams. This is O(n) time, O(1) space (fixed 26 slots). It's better than Counter when: (a) the alphabet is small and known, (b) you want to avoid hash table overhead, (c) you need maximum speed (array access is faster than dict lookup).

**Q16:** Hashing every substring of length m independently costs O(m) per hash, and there are O(n) substrings, giving O(nm) total. Rabin-Karp's rolling hash updates the hash in O(1) by subtracting the contribution of the outgoing character and adding the incoming one. Total: O(n + m) average case (O(nm) worst case with many hash collisions).

**Q17:** Use a fixed-size sliding window of size K. Initialize the window sum with the first K elements. Then slide right, adding the new element and subtracting the leftmost element. Track the maximum sum seen. Time: O(n). Space: O(1).

---

## Coding Practice (Outside 2-hour budget)

These LeetCode problems reinforce the patterns covered above. Practice them separately during spare time.

### Problem List

1. **Two Sum** (LC #1) — Hash table pattern
   - Key insight: For each number, check if its complement exists in the map
   - Time: O(n), Space: O(n)

2. **Best Time to Buy and Sell Stock** (LC #121) — Kadane's variant / greedy
   - Key insight: Track the minimum price seen so far, compute profit at each step
   - Time: O(n), Space: O(1)

3. **Longest Substring Without Repeating Characters** (LC #3) — Sliding window
   - Key insight: Expand right pointer; when a duplicate is found, advance left pointer past the previous occurrence
   - Time: O(n), Space: O(min(n, alphabet_size))

4. **Group Anagrams** (LC #49) — Hash table + string hashing
   - Key insight: Use sorted string (or character frequency tuple) as the hash key
   - Time: O(n * k log k) where k is max string length, or O(n * k) with frequency counting

5. **Subarray Sum Equals K** (LC #560) — Prefix sum + hash map
   - Key insight: Store prefix sum frequencies. At each index, check if `current_prefix - K` exists in the map
   - Time: O(n), Space: O(n)

### Practice Tips for Jump
- Always state the brute-force approach first, then optimize
- Discuss time AND space complexity for every solution
- Consider edge cases: empty array, single element, all negatives, duplicates
- Write clean, production-quality code — variable names matter
- Be prepared to discuss alternatives: "I chose X over Y because..."
