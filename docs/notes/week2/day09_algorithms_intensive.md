# Day 9 (Fri Apr 17) -- Algorithms Intensive & Timed Practice

## Overview (5 min)

Today splits into two parts: (1) a 2-hour study session on algorithm problem-solving strategy, pattern recognition, and complexity analysis -- the meta-skills that make you faster and more accurate under pressure, and (2) a separate timed mock assessment outside your study budget. The study portion focuses on HOW to think about problems rather than grinding more LeetCode. At Jump Trading, coding interviews test whether you can write clean, correct, efficient code under time pressure -- the same skill that matters when implementing latency-sensitive systems in production.

---

## Reading Materials (60-90 min)

### 1. Problem-Solving Framework

When you see an unfamiliar problem in an interview, panic is the enemy. Having a repeatable framework turns uncertainty into a systematic process.

**The 5-Step Approach**

**Step 1: Understand (2-3 minutes)**
Read the problem twice. Identify:
- What are the inputs? What are the outputs?
- What are the constraints? (size of input, range of values, time/space limits)
- Are there edge cases mentioned or implied?

Restate the problem in your own words to the interviewer. This catches misunderstandings early and buys thinking time.

**Step 2: Examples (2-3 minutes)**
Work through 2-3 examples by hand:
- A small "happy path" example
- An edge case (empty input, single element, all duplicates, etc.)
- A larger example if the pattern is not yet clear

Write these down. They become your test cases later.

**Step 3: Approach (5-7 minutes)**
This is where pattern recognition kicks in. Ask yourself:
- Have I seen a similar problem? What technique did it use?
- What data structure would make the key operation fast?
- Can I simplify the problem (solve a smaller version first)?
- What is the brute force? Can I do better?

State your approach to the interviewer before coding. Get a nod or a redirect.

**Step 4: Code (15-20 minutes)**
Write clean code. Use meaningful variable names. Narrate as you go. If you get stuck on a detail, stub it out with a comment and come back.

**Step 5: Verify (3-5 minutes)**
Trace through your code with one of your examples. Check edge cases. Analyze time and space complexity. Fix bugs.

### 2. Pattern Recognition

Most interview problems fall into a small set of patterns. Recognizing the pattern quickly is the single biggest time-saver.

**Pattern 1: Sliding Window**

*When to use*: Problems involving contiguous subarrays/substrings with some constraint (max sum, contains all characters, etc.)

*Signal words*: "subarray", "substring", "contiguous", "window", "maximum/minimum length"

*Template*:
```python
def sliding_window(arr, condition):
    left = 0
    best = initial_value
    state = {}  # window state

    for right in range(len(arr)):
        # Expand window: add arr[right] to state
        update_state(state, arr[right])

        # Shrink window while condition is violated
        while not valid(state, condition):
            remove_state(state, arr[left])
            left += 1

        # Update answer
        best = optimize(best, right - left + 1)

    return best
```

*Common mistakes*: Off-by-one on window boundaries; forgetting to shrink the window; not handling the empty window case.

**Pattern 2: Two Pointers**

*When to use*: Sorted arrays, palindromes, pair-sum problems, merging sorted sequences.

*Signal words*: "sorted", "pair", "two sum", "palindrome", "merge"

*Variants*:
- Opposite ends (converging): start at both ends, move inward
- Same direction (fast/slow): linked list cycle detection, removing duplicates
- Two arrays: merge sorted arrays

*Common mistakes*: Not handling duplicates; incorrect termination condition (< vs <=).

**Pattern 3: Hash Map / Set**

*When to use*: When you need O(1) lookup to avoid O(n) inner loop. Turns O(n^2) brute force into O(n).

*Signal words*: "find pair", "count occurrences", "first duplicate", "group by"

*Common mistakes*: Not considering hash collisions in analysis; using a map when a set suffices.

**Pattern 4: Stack**

*When to use*: Matching pairs (parentheses), nearest greater/smaller element, expression evaluation.

*Signal words*: "matching", "nested", "parentheses", "next greater", "evaluate"

*Template for matching*:
```python
def is_valid(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return len(stack) == 0
```

**Pattern 5: Binary Search**

*When to use*: Sorted data, or when you can binary search on the answer space.

*Signal words*: "sorted", "find position", "minimum that satisfies", "search in rotated"

*Key insight*: Binary search is not just for "find element in sorted array." You can binary search on the answer whenever the problem has monotonic structure (if X works, then X+1 also works).

*Common mistakes*: Off-by-one errors in bounds; infinite loops with incorrect mid calculation; not handling the "not found" case. Use `left < right` vs `left <= right` consistently and know which one your template uses.

```python
# Find leftmost position where condition is true
def binary_search(lo, hi, condition):
    while lo < hi:
        mid = lo + (hi - lo) // 2  # avoid overflow
        if condition(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Pattern 6: BFS/DFS (Graph/Tree Traversal)**

*When to use*: Trees, graphs, grids, state-space search.

*Signal words*: "shortest path" (BFS), "all paths" (DFS), "connected components", "island", "level order"

*Key decision*: BFS for shortest path in unweighted graphs. DFS for exhaustive search, backtracking, topological sort.

**Pattern 7: Dynamic Programming**

*When to use*: Optimal substructure + overlapping subproblems. The problem can be broken into smaller problems whose solutions combine to form the answer.

*Signal words*: "minimum cost", "number of ways", "longest/shortest", "can you reach", "partition"

*Approach*:
1. Define the state: what information do you need to make a decision?
2. Define the recurrence: how does the answer to a larger problem depend on smaller problems?
3. Define the base case.
4. Determine the iteration order (bottom-up) or use memoization (top-down).

*Common mistakes*: Wrong state definition (missing a dimension); not identifying overlapping subproblems (leading to exponential time); off-by-one in base cases.

**Pattern 8: Interval Problems**

*When to use*: Problems involving ranges, schedules, meetings, merging overlapping segments.

*Signal words*: "intervals", "overlap", "merge", "schedule", "meeting rooms"

*Key technique*: Sort by start time, then sweep through:
```python
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:  # overlaps
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
```

**Pattern 9: Design / Data Structure**

*When to use*: "Design a data structure that supports X in O(1)."

*Signal words*: "design", "implement", "support operations"

*Key insight*: Combine multiple data structures. LRU Cache = hash map + doubly-linked list. Median finder = two heaps. Stack with getMin = two stacks.

### 3. Common Pitfalls by Problem Type

**Array/String Problems**
- Empty array/string input
- Single element input
- All elements identical
- Integer overflow when summing
- Off-by-one at array boundaries

**Linked List Problems**
- Null head
- Single node
- Cycle detection (always check before dereferencing .next.next)
- Losing reference to the head when modifying

**Tree Problems**
- Null root
- Single node tree (leaf is also root)
- Skewed tree (essentially a linked list -- worst case for unbalanced trees)
- Confusing BST property: left subtree ALL less than root, not just left child

**Graph Problems**
- Disconnected components
- Self-loops
- Directed vs undirected (adjacency list has edges in both directions for undirected)
- Visited tracking to avoid infinite loops

**DP Problems**
- Base case errors
- Forgetting to handle the 0-index vs 1-index mismatch
- Using O(n^2) space when O(n) suffices (only need previous row)

### 4. Complexity Analysis Review

You must be able to state time and space complexity for any solution you write. Interviewers at trading firms particularly value this because they care about performance.

**Time Complexity Hierarchy**

```
O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n) < O(n!)
```

**Common Operations**

| Operation | Time Complexity |
|-----------|----------------|
| Array access by index | O(1) |
| Hash map get/set | O(1) average |
| Binary search | O(log n) |
| Sorting (comparison-based) | O(n log n) |
| BFS/DFS on graph | O(V + E) |
| Two nested loops over n | O(n^2) |
| All subsets of n elements | O(2^n) |
| All permutations of n elements | O(n!) |

**Amortized Analysis**

Some operations are O(1) amortized even though individual calls may be O(n). Examples:
- Dynamic array append: occasionally doubles capacity (O(n) copy) but amortized O(1) per append.
- Hash map operations: occasional rehash is O(n) but amortized O(1).

**Space Complexity**

Do not forget space. Common sources:
- Recursion stack depth (DFS on a tree: O(h) where h is height)
- Auxiliary data structures (hash map: O(n))
- Output array (does it count? clarify with interviewer)

**Trading Relevance**

At Jump, you will be asked "what is the time complexity?" and "can we do better?" frequently. For latency-critical code, even the constant factors matter -- O(n) with cache-friendly access patterns beats O(n) with random memory access. But in an interview, focus on big-O first and mention constant-factor optimizations as a bonus.

### 5. Time Management During Assessments

For a typical 4-problem online assessment (60-90 minutes):
- **Easy (5-10 min)**: Read, code, test, move on. Do not over-think.
- **Medium 1 (15-20 min)**: Identify the pattern, code the standard approach. Test with edge cases.
- **Medium 2 (15-20 min)**: May require combining two patterns or a less obvious insight.
- **Hard (20-30 min)**: Spend 5 minutes thinking before coding. A brute force that passes some test cases is better than a blank submission.

**Rules**:
- Do the easy problem first. Get it done and move on. Confidence booster.
- If stuck on a problem for more than 5 minutes without progress, move to the next one and come back.
- Partial solutions earn partial credit on many platforms. A brute-force O(n^2) solution that passes 60% of test cases is better than nothing.
- Always handle edge cases explicitly at the top of your function (empty input, single element).

### 6. Interview-Specific Tips for Trading Firms

Trading firm interviews differ from Big Tech in several ways:

**They value efficiency obsessively.** An O(n log n) solution when O(n) exists will get pushback. They will ask "can we do better?" more aggressively.

**They expect low-level awareness.** Mentioning cache locality, branch prediction, or memory allocation patterns earns points even in a coding interview.

**They prefer C++ and sometimes care about language choice.** If you are comfortable in C++, use it. If using Python, acknowledge the performance trade-offs.

**They test mathematical thinking.** You may encounter problems involving probability, expected value, or bit manipulation more than at typical software companies.

**They value clean, correct code over clever code.** A simple, correct solution beats an elegant but buggy one. Trading systems cannot afford bugs.

---

## Practice Questions (20-30 min)

Think through these questions and write brief answers:

1. **You are given an array of stock prices over time. Find the maximum profit from a single buy and sell.** What pattern does this use? What is the optimal time complexity? What edge case is most important?

2. **Explain how you would identify which algorithm pattern to use for a problem you have never seen before.** Walk through your mental checklist.

3. **You have an O(n^2) solution to a problem and the input size is n = 10^6. Is this acceptable? How do you estimate whether it will pass within time limits?**

4. **Describe the LRU Cache data structure.** What operations does it support? What are the time complexities? What two underlying data structures does it combine and why?

5. **What is the difference between top-down (memoization) and bottom-up (tabulation) dynamic programming?** When would you prefer one over the other?

6. **You are merging k sorted lists into one sorted output.** What data structure gives you the optimal time complexity? What is that complexity?

7. **In a binary search, you write `mid = (left + right) / 2`. What is the bug?** How do you fix it? Why does this matter more in C++ than Python?

8. **You are asked to design a data structure that supports insert, delete, and getRandom all in O(1).** Sketch your approach. What data structures do you combine?

---

## Coding Practice (SEPARATE from 2-hour study budget)

### Timed Mock Assessment

Set a 75-minute timer. Solve all four problems in order. Do not look at hints. Track your time per problem.

**Problem 1: Valid Parentheses (Easy) -- Target: 8 minutes**
- LeetCode #20
- Pattern: Stack
- Key insight: Each closing bracket must match the most recent unmatched opening bracket.
- Edge cases: empty string, single character, only opening brackets, only closing brackets.

**Problem 2: Merge Intervals (Medium) -- Target: 15 minutes**
- LeetCode #56
- Pattern: Sort + Sweep
- Key insight: Sort by start time, then merge overlapping intervals greedily.
- Edge cases: single interval, all intervals overlap, no intervals overlap, intervals contained within others.

**Problem 3: LRU Cache (Medium) -- Target: 20 minutes**
- LeetCode #146
- Pattern: Hash Map + Doubly Linked List
- Key insight: Hash map for O(1) key lookup. Doubly linked list for O(1) move-to-front and eviction of least recently used.
- Edge cases: capacity 1, get on missing key, put that updates existing key.

**Problem 4: Median of Two Sorted Arrays (Hard) -- Target: 30 minutes**
- LeetCode #4
- Pattern: Binary Search
- Key insight: Binary search on the partition point of the smaller array. At the correct partition, max(left sides) <= min(right sides).
- Edge cases: one array empty, arrays of very different sizes, all elements of one array smaller than all elements of the other.

### After the Mock

For each problem, record:
- Time taken
- Did you get it right on the first attempt?
- What was the tricky part?
- What would you do differently next time?

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** What algorithm pattern is most appropriate for "find the longest substring without repeating characters"?
- A) Two pointers (converging)
- B) Sliding window with hash set
- C) Dynamic programming
- D) Binary search

**Q2.** You have a sorted array and need to find if a target exists. Which approach is optimal?
- A) Linear scan: O(n)
- B) Binary search: O(log n)
- C) Hash the array first, then lookup: O(n) preprocessing + O(1) lookup
- D) Sort and search: O(n log n)

**Q3.** What is the time complexity of BFS on a graph with V vertices and E edges?
- A) O(V)
- B) O(E)
- C) O(V + E)
- D) O(V * E)

**Q4.** Which data structure combination gives O(1) for all LRU Cache operations (get, put)?
- A) Array + binary search tree
- B) Hash map + doubly-linked list
- C) Hash map + stack
- D) Two arrays

**Q5.** In a merge intervals problem, what is the critical first step?
- A) Check for overlaps between all pairs
- B) Sort intervals by end time
- C) Sort intervals by start time
- D) Remove duplicate intervals

**Q6.** What is the space complexity of a recursive DFS on a balanced binary tree with n nodes?
- A) O(1)
- B) O(log n)
- C) O(n)
- D) O(n log n)

**Q7.** You have an O(n log n) algorithm and n = 10^6. Approximately how many operations is that?
- A) 10^6
- B) 2 * 10^7
- C) 10^12
- D) 6 * 10^6

**Q8.** Which problem type is dynamic programming NOT typically used for?
- A) Finding shortest paths in weighted graphs
- B) Counting the number of ways to reach a target
- C) Finding connected components in a graph
- D) Computing the longest common subsequence

### Short Answer

**Q9.** You write `mid = (left + right) / 2` in C++ where left and right are 32-bit integers. What can go wrong? How do you fix it?

**Q10.** Explain why an O(n) algorithm with poor cache locality can be slower than an O(n log n) algorithm with good cache locality for practical input sizes.

**Q11.** What is amortized O(1)? Give an example of a data structure operation that is amortized O(1) but occasionally O(n).

**Q12.** You are in a coding interview and have been stuck for 5 minutes on a medium problem with no progress. What do you do?

**Q13.** Describe the "binary search on the answer" technique. When is it applicable?

**Q14.** What is the difference between a stable and unstable sort? When does stability matter?

**Q15.** In an interview for a trading firm, you solve a problem in O(n log n). The interviewer asks "can you do better?" What questions do you ask before attempting O(n)?

**Q16.** What are the two conditions for a problem to be solvable with dynamic programming?

---

## Quiz Answer Key

**Q1.** B) Sliding window with hash set. The window tracks the current substring. The hash set tracks characters in the window. When a duplicate is found, shrink the window from the left.

**Q2.** B) Binary search: O(log n). The array is already sorted, so binary search is directly applicable. Option C works but wastes O(n) space and time on preprocessing when the data is already sorted.

**Q3.** C) O(V + E). BFS visits each vertex once (O(V)) and explores each edge once (O(E)).

**Q4.** B) Hash map + doubly-linked list. The hash map provides O(1) lookup by key. The doubly-linked list provides O(1) insertion at front, O(1) removal from any position (given a pointer), and O(1) eviction from the back.

**Q5.** C) Sort intervals by start time. Once sorted by start time, you can sweep left to right and merge overlapping intervals in a single pass.

**Q6.** B) O(log n). The recursion stack depth equals the tree height, which is O(log n) for a balanced tree. For a skewed tree, it would be O(n).

**Q7.** B) Approximately 2 * 10^7. log2(10^6) is about 20, so 10^6 * 20 = 2 * 10^7. This is well within time limits (typically 10^8-10^9 operations per second).

**Q8.** C) Finding connected components in a graph. This is typically solved with BFS/DFS or Union-Find, not DP. The others all have optimal substructure and overlapping subproblems.

**Q9.** Integer overflow. If left and right are both large (e.g., close to 2^31 - 1), their sum overflows a 32-bit integer, producing a negative number. Fix: `mid = left + (right - left) / 2`. In Python, integers have arbitrary precision, so overflow is not an issue, but writing it the safe way is good habit.

**Q10.** Modern CPUs rely heavily on caches. An O(n) algorithm that jumps randomly through memory (e.g., linked list traversal) incurs cache misses on nearly every access. Each miss costs ~100 nanoseconds (main memory access). An O(n log n) algorithm that accesses memory sequentially (e.g., merge sort on an array) benefits from prefetching and cache line reuse. For n = 10^6, the constant factor difference from cache misses can outweigh the log n factor. This is why array-based data structures are preferred in latency-sensitive trading systems.

**Q11.** Amortized O(1) means that while a single operation may occasionally take O(n) time, the average cost over a sequence of n operations is O(1) per operation. Example: appending to a dynamic array (e.g., Python list, C++ vector). Most appends are O(1), but occasionally the array must be resized (doubling capacity), which copies all n elements in O(n). Over n appends, total work is O(n), so amortized cost per append is O(1).

**Q12.** Communicate with the interviewer. Say what you have tried and where you are stuck. Ask clarifying questions. Propose a brute-force approach and ask if you should code it. Interviewers want to see your problem-solving process and communication, not just the final answer. Silently staring at the screen for 5 minutes is the worst outcome.

**Q13.** Binary search on the answer works when: (1) the answer is a number in some range [lo, hi], and (2) there is a monotonic predicate -- if answer X is feasible, then all answers >= X (or <= X) are also feasible. You binary search for the boundary where the predicate flips. Example: "find the minimum capacity such that all shipments can be completed in D days." You binary search on capacity and for each candidate, check if it works in O(n).

**Q14.** A stable sort preserves the relative order of elements with equal keys. An unstable sort does not. Stability matters when sorting by multiple criteria in sequence (e.g., sort by price, then by time -- if the second sort is stable, the time ordering within equal prices is preserved). Merge sort is stable; quicksort and heapsort are not.

**Q15.** Ask: "What is the input format -- is the data sorted or have any special structure?" "Are there constraints on the value range that would allow counting sort or radix sort?" "Is there a known lower bound for this problem?" Understanding the problem's structure is necessary before attempting to improve; otherwise you may waste time trying to beat an information-theoretic lower bound.

**Q16.** (1) **Optimal substructure**: An optimal solution to the problem contains optimal solutions to subproblems. (2) **Overlapping subproblems**: The same subproblems are solved multiple times in a naive recursive approach. If both hold, DP avoids redundant computation by storing results.
