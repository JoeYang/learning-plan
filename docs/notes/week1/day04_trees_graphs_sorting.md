# Day 4 (Sun Apr 12) — DS&A II: Trees, Graphs, Sorting

## Overview (5 min)

Trees and graphs model hierarchical and relational data that appears everywhere in trading systems — order book levels form a balanced BST for price lookup, instrument dependency chains are DAGs, exchange connectivity is a graph, and priority queues (heaps) power order scheduling and event-driven simulations. Sorting algorithms underpin order book maintenance, trade matching, and time-series processing. Understanding the internal mechanics and trade-offs of these structures is essential for both interviews and building high-performance systems.

---

## Reading Materials (60-90 min)

### 1. Binary Trees and BSTs

A **binary tree** is a rooted tree where each node has at most two children (left and right). A **binary search tree (BST)** adds the invariant: for every node, all keys in the left subtree are smaller, and all keys in the right subtree are larger.

#### Traversals

Four fundamental ways to visit every node:

**In-order (Left, Root, Right):** Visits BST nodes in sorted order.
```python
def inorder(node):
    if node is None:
        return
    inorder(node.left)
    process(node.val)  # Visit in sorted position
    inorder(node.right)
```

**Pre-order (Root, Left, Right):** Useful for serialization/copying a tree.
```python
def preorder(node):
    if node is None:
        return
    process(node.val)
    preorder(node.left)
    preorder(node.right)
```

**Post-order (Left, Right, Root):** Useful for deletion, evaluating expression trees.
```python
def postorder(node):
    if node is None:
        return
    postorder(node.left)
    postorder(node.right)
    process(node.val)
```

**Level-order (BFS):** Visit nodes level by level using a queue.
```python
from collections import deque

def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

**Iterative in-order (important for interviews — avoids stack overflow on deep trees):**
```python
def inorder_iterative(root):
    stack = []
    current = root
    result = []
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right
    return result
```

#### BST Operations

| Operation | Average | Worst (unbalanced) |
|---|---|---|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Find min/max | O(log n) | O(n) |

The worst case occurs when the BST degenerates into a linked list (e.g., inserting sorted data).

#### Balancing: AVL and Red-Black Trees

**AVL trees** maintain the invariant that for every node, the heights of left and right subtrees differ by at most 1. After insertion/deletion, rotations (single or double) restore balance. Strictly balanced — guaranteed O(log n) height.

**Red-Black trees** (used in `std::map`, Java `TreeMap`) use a coloring scheme with 5 invariants to ensure the tree height is at most 2 * log(n+1). Less strictly balanced than AVL — fewer rotations on insert/delete but slightly worse search.

**Trade-off:** AVL trees have faster lookups (shorter height) but slower insertions/deletions (more rotations). Red-Black trees are faster for insert-heavy workloads.

**Trading context:** An order book organized by price level uses a balanced BST (or skiplist) to support O(log n) price level insertion, deletion, and lookup. Finding the best bid/ask is finding the max/min in O(log n). Red-Black trees are common in production order books because insert/delete happens on every order update.

#### BST Validation

A BST is valid if every node satisfies the BST property. A common mistake is only checking immediate children — you must check that the entire left subtree is less than the node and the entire right subtree is greater.

```python
def is_valid_bst(node, lo=float('-inf'), hi=float('inf')):
    if node is None:
        return True
    if node.val <= lo or node.val >= hi:
        return False
    return (is_valid_bst(node.left, lo, node.val) and
            is_valid_bst(node.right, node.val, hi))
```

### 2. Graphs

A graph G = (V, E) consists of vertices V and edges E. Edges can be directed or undirected, weighted or unweighted.

**Representations:**
- **Adjacency list:** `graph[u] = [(v1, w1), (v2, w2), ...]` — space efficient for sparse graphs (O(V + E))
- **Adjacency matrix:** `matrix[u][v] = weight` — O(V^2) space, O(1) edge lookup, good for dense graphs

#### BFS (Breadth-First Search)

Explores vertices level by level using a queue. Finds shortest path in unweighted graphs.

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    distances = {start: 0}

    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if v not in visited:
                visited.add(v)
                distances[v] = distances[u] + 1
                queue.append(v)
    return distances
```

**Time:** O(V + E). **Space:** O(V).

#### DFS (Depth-First Search)

Explores as deep as possible before backtracking. Uses a stack (explicit or call stack).

```python
def dfs(graph, start):
    visited = set()

    def explore(u):
        visited.add(u)
        for v in graph[u]:
            if v not in visited:
                explore(v)

    explore(start)
    return visited
```

**Applications:** Connected components, cycle detection, topological sort, pathfinding in mazes.

#### Cycle Detection

**Undirected graph:** During DFS, if you encounter a visited vertex that isn't the parent of the current vertex, there's a cycle.

**Directed graph:** Use three states — WHITE (unvisited), GRAY (in current DFS path), BLACK (fully processed). If you encounter a GRAY vertex, you've found a back edge (cycle).

```python
def has_cycle_directed(graph, n):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(u):
        color[u] = GRAY
        for v in graph[u]:
            if color[v] == GRAY:  # Back edge = cycle
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    return any(dfs(u) for u in range(n) if color[u] == WHITE)
```

#### Topological Sort

A linear ordering of vertices in a DAG (Directed Acyclic Graph) such that for every edge u -> v, u appears before v.

**Kahn's algorithm (BFS-based):**
```python
from collections import deque

def topological_sort(graph, n):
    in_degree = [0] * n
    for u in range(n):
        for v in graph[u]:
            in_degree[v] += 1

    queue = deque(u for u in range(n) if in_degree[u] == 0)
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    return order if len(order) == n else []  # Empty = cycle exists
```

**Trading context:** Task dependency resolution — "calculate Greek sensitivities before portfolio risk, which requires market data" forms a DAG. Topological sort determines execution order.

#### Dijkstra's Algorithm

Finds shortest paths from a source to all vertices in a weighted graph with non-negative edges.

```python
import heapq

def dijkstra(graph, source):
    dist = {source: 0}
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float('inf')):
            continue  # Stale entry

        for v, weight in graph[u]:
            new_dist = d + weight
            if new_dist < dist.get(v, float('inf')):
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist
```

**Time:** O((V + E) log V) with a binary heap. **Space:** O(V).

**Key insight:** Dijkstra is a greedy algorithm — it always processes the nearest unvisited vertex. This works because edge weights are non-negative, so the shortest path to a vertex is finalized once it's dequeued.

**Trading context:** Network routing optimization — finding the lowest-latency path between data centers or exchanges.

### 3. Sorting Algorithms

#### Quicksort

**Strategy:** Pick a pivot, partition the array into elements less than and greater than the pivot, recurse on both halves.

```python
def quicksort(arr, lo, hi):
    if lo < hi:
        pivot_idx = partition(arr, lo, hi)
        quicksort(arr, lo, pivot_idx - 1)
        quicksort(arr, pivot_idx + 1, hi)

def partition(arr, lo, hi):
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] <= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    return i
```

| Property | Value |
|---|---|
| Average time | O(n log n) |
| Worst time | O(n^2) — when pivot is always min or max |
| Space | O(log n) stack depth average, O(n) worst |
| Stable | No |
| In-place | Yes |

**Avoiding worst case:** Randomized pivot selection or median-of-three pivot.

**Why quicksort is fast in practice:** Excellent cache locality (operates on contiguous memory), small constant factors, and in-place operation. Despite O(n^2) worst case, randomized quicksort is nearly always O(n log n).

#### Mergesort

**Strategy:** Divide array in half, recursively sort each half, merge the sorted halves.

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

| Property | Value |
|---|---|
| Time | O(n log n) always |
| Space | O(n) |
| Stable | Yes |
| In-place | No |

**Mergesort guarantees O(n log n)** regardless of input — no pathological cases. The trade-off is O(n) extra space.

#### Heapsort

**Strategy:** Build a max-heap from the array, then repeatedly extract the maximum and place it at the end.

| Property | Value |
|---|---|
| Time | O(n log n) always |
| Space | O(1) |
| Stable | No |
| In-place | Yes |

**Trade-off:** O(n log n) guaranteed with O(1) space (better than mergesort on space, better than quicksort on worst case). But poor cache performance — the heap property causes non-sequential memory access patterns, making it slower in practice than quicksort despite the same asymptotic complexity.

#### Comparison

| Algorithm | Best | Average | Worst | Space | Stable |
|---|---|---|---|---|---|
| Quicksort | O(n log n) | O(n log n) | O(n^2) | O(log n) | No |
| Mergesort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Heapsort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |

**When to choose which:**
- **Quicksort:** Default for general-purpose sorting (best cache behavior)
- **Mergesort:** When stability is required, or for linked lists (no random access needed), or for external sorting (merge passes over files)
- **Heapsort:** When O(1) space is critical and worst-case guarantee is needed

**Python's sort:** Timsort — a hybrid of mergesort and insertion sort. O(n log n) worst case, stable, and optimized for partially sorted data (common in practice). It detects "runs" (pre-sorted subsequences) and merges them efficiently.

### 4. Heaps and Priority Queues

A **heap** is a complete binary tree stored in an array where the parent is always greater (max-heap) or smaller (min-heap) than its children.

**Array representation:**
- Parent of node i: `(i - 1) // 2`
- Left child of node i: `2 * i + 1`
- Right child of node i: `2 * i + 2`

**Operations:**
| Operation | Time |
|---|---|
| Insert (push) | O(log n) |
| Extract min/max (pop) | O(log n) |
| Peek min/max | O(1) |
| Build heap from array | O(n) |

**Build heap in O(n):** Start from the last non-leaf node and sift down. The key insight is that most nodes are near the bottom and need minimal sifting. The sum 0 * n/2 + 1 * n/4 + 2 * n/8 + ... converges to O(n).

```python
import heapq

# Python's heapq is a min-heap
orders = []
heapq.heappush(orders, (timestamp, order))  # Priority = timestamp
earliest = heapq.heappop(orders)             # Get oldest order

# For max-heap, negate the priority
heapq.heappush(orders, (-priority, order))
```

**Trading context:** Event-driven simulation uses a priority queue (min-heap) keyed by timestamp. The "Merge K Sorted Lists" pattern appears when merging market data streams from multiple exchanges — each stream is sorted by timestamp, and a heap efficiently selects the next event across all streams.

**Kth largest element:** Use a min-heap of size k. After processing all elements, the heap root is the kth largest. Time: O(n log k). Space: O(k). Alternatively, quickselect achieves O(n) average time.

---

## Practice Questions (20-30 min)

1. **Explain the difference between pre-order, in-order, and post-order traversals. When would you use each? What does in-order traversal of a BST produce?**

2. **How does BST validation work? Why is it wrong to only check that each node's value is between its immediate children? Write the correct approach.**

3. **Compare BFS and DFS for graph traversal. When would you choose one over the other? Give a trading-related example for each.**

4. **Explain topological sort. Can it be performed on a graph with cycles? How do you detect if a topological ordering exists?**

5. **Walk through Dijkstra's algorithm on a small weighted graph. Why doesn't it work with negative edge weights?**

6. **Compare quicksort, mergesort, and heapsort. You're sorting a nearly-sorted array of 10 million trade records by timestamp. Which algorithm would you choose and why?**

7. **Explain how a heap is stored in an array. Why is `build_heap` O(n) instead of O(n log n)?**

8. **You're merging real-time market data from 20 exchanges, each providing a sorted stream. Describe an efficient algorithm. What is its time complexity?**

9. **Explain cycle detection in a directed graph using DFS with three-color marking. Why are three states needed instead of two?**

10. **Design a data structure that supports insert, delete, and find-median in O(log n). How would two heaps help?**

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** In-order traversal of a BST visits nodes in:
- (A) Random order
- (B) Level order
- (C) Sorted ascending order
- (D) Sorted descending order

**Q2.** The worst-case time complexity of searching in an unbalanced BST is:
- (A) O(1)
- (B) O(log n)
- (C) O(n)
- (D) O(n log n)

**Q3.** BFS on a graph uses which data structure?
- (A) Stack
- (B) Queue
- (C) Heap
- (D) Hash table

**Q4.** Topological sort requires the graph to be:
- (A) Undirected and acyclic
- (B) Directed and acyclic (DAG)
- (C) Directed and cyclic
- (D) Connected

**Q5.** Dijkstra's algorithm fails with:
- (A) Sparse graphs
- (B) Dense graphs
- (C) Negative edge weights
- (D) Disconnected graphs

**Q6.** Quicksort's worst-case time complexity is:
- (A) O(n)
- (B) O(n log n)
- (C) O(n^2)
- (D) O(2^n)

**Q7.** Which sorting algorithm is stable?
- (A) Quicksort
- (B) Heapsort
- (C) Mergesort
- (D) Selection sort

**Q8.** The time to build a heap from an unsorted array of n elements is:
- (A) O(n^2)
- (B) O(n log n)
- (C) O(n)
- (D) O(log n)

**Q9.** In the three-color DFS cycle detection for directed graphs, a back edge is detected when we encounter a vertex colored:
- (A) WHITE
- (B) GRAY
- (C) BLACK
- (D) Any color

**Q10.** The "Merge K Sorted Lists" problem is optimally solved in:
- (A) O(N * K) where N is total elements
- (B) O(N log K)
- (C) O(N log N)
- (D) O(K^2)

### Short Answer

**Q11.** Explain why quicksort typically outperforms mergesort in practice despite both being O(n log n) average.

**Q12.** Given a binary tree, how would you determine its height? What is the time and space complexity?

**Q13.** Describe Kahn's algorithm for topological sort. What happens if the graph has a cycle?

**Q14.** Why does Dijkstra fail with negative edges? Give a small example.

**Q15.** Explain the quickselect algorithm for finding the kth largest element. What is its average and worst-case complexity?

**Q16.** How would you detect if an undirected graph is connected? What about a directed graph (strongly connected)?

**Q17.** You have a stream of numbers and need to maintain the running median efficiently. Describe the two-heap approach.

---

## Quiz Answer Key

**Q1: (C)** In-order traversal visits left subtree, root, right subtree. For a BST, this visits nodes in ascending sorted order because all left descendants are smaller and all right descendants are larger.

**Q2: (C)** An unbalanced BST can degenerate into a linked list (e.g., inserting 1, 2, 3, 4, 5 in order). Search becomes O(n). Balanced BSTs (AVL, Red-Black) guarantee O(log n).

**Q3: (B)** BFS uses a queue (FIFO) to explore vertices level by level. DFS uses a stack (LIFO) or recursion.

**Q4: (B)** Topological sort is defined only for Directed Acyclic Graphs (DAGs). A cycle means no valid ordering exists (vertex A before B, B before C, C before A is impossible).

**Q5: (C)** Dijkstra's greedy approach assumes that once a vertex is finalized (dequeued), no shorter path exists. Negative edges violate this: a longer path through a negative edge might be shorter overall. Use Bellman-Ford for graphs with negative edges.

**Q6: (C)** Worst case is O(n^2) when the pivot selection is poor (always the smallest or largest element), causing maximally unbalanced partitions of sizes 0 and n-1. Randomized pivot makes this extremely unlikely.

**Q7: (C)** Mergesort preserves the relative order of equal elements. The merge step always takes from the left array first when elements are equal. Quicksort and heapsort can swap equal elements past each other.

**Q8: (C)** Build-heap is O(n) using the sift-down approach. Starting from the bottom, most nodes (n/2 leaves) need 0 work. Nodes at height h need O(h) work. The sum: sum(h * n/(2^(h+1))) for h = 0 to log(n) = O(n).

**Q9: (B)** GRAY means the vertex is currently on the DFS stack (part of the active path). Encountering a GRAY vertex means we've found a cycle (a back edge from a descendant to an ancestor). WHITE means unvisited, BLACK means fully processed (all descendants explored).

**Q10: (B)** Use a min-heap of size K, initially containing the first element from each list. Extract the minimum (O(log K)), then push the next element from that list. Repeat until all N elements are processed. Total: O(N log K).

**Q11:** Cache locality. Quicksort partitions in-place on a contiguous array — sequential memory access fills cache lines efficiently. Mergesort copies data to temporary arrays, causing cache misses. The constant factor in quicksort's O(n log n) is smaller due to this hardware-level advantage. Additionally, quicksort does fewer total comparisons on average.

**Q12:** Recursively compute: `height = 1 + max(height(left), height(right))`, with base case: empty tree has height -1 (or 0, depending on convention). Time: O(n) — visit every node once. Space: O(h) where h is the height — the recursion depth. Worst case O(n) for a skewed tree, O(log n) for a balanced tree.

**Q13:** Kahn's algorithm: 1) Compute in-degree for all vertices. 2) Add all vertices with in-degree 0 to a queue. 3) Dequeue a vertex, add to result, decrement in-degree of all neighbors. 4) If any neighbor's in-degree reaches 0, enqueue it. 5) If the result has fewer vertices than the graph, a cycle exists (some vertices never reached in-degree 0).

**Q14:** Consider: A -> B (weight 1), A -> C (weight 5), B -> C (weight -10). Dijkstra finalizes B at distance 1, then C at distance 5 (via A->C). But the path A->B->C has distance 1 + (-10) = -9, which is shorter. Dijkstra never reconsiders C because it was already finalized. Negative edges break the greedy invariant.

**Q15:** Quickselect uses the partition step from quicksort. After partitioning, the pivot is in its final sorted position p. If p == k, return it. If k < p, recurse on the left. If k > p, recurse on the right. Only recurse on ONE side, giving O(n) average (n + n/2 + n/4 + ... = 2n). Worst case O(n^2) with bad pivots, but randomized pivot makes this extremely unlikely.

**Q16:** Undirected: Run BFS/DFS from any vertex. If all vertices are visited, the graph is connected. O(V + E). Directed (strongly connected): Use Tarjan's or Kosaraju's algorithm. Kosaraju: (1) Run DFS and record finish order. (2) Reverse all edges. (3) Run DFS in reverse finish order. If all vertices are in one SCC, the graph is strongly connected.

**Q17:** Maintain a max-heap (left half, storing smaller values) and a min-heap (right half, storing larger values). Invariant: max-heap size equals min-heap size or is one larger. Insert: add to max-heap, rebalance by moving tops between heaps. Median: if sizes equal, average of both tops. If max-heap is larger, its top is the median. Insert: O(log n). Find median: O(1).

---

## Coding Practice (Outside 2-hour budget)

### Problem List

1. **Validate Binary Search Tree** (LC #98) — BST property with range checking
   - Key insight: Pass valid range (low, high) down the tree. Each node must be within range.
   - Time: O(n), Space: O(h)

2. **Number of Islands** (LC #200) — BFS/DFS on a grid
   - Key insight: Treat the grid as a graph. Each land cell is a vertex. Run DFS/BFS from each unvisited land cell, marking all reachable land as visited.
   - Time: O(m*n), Space: O(m*n)

3. **Course Schedule** (LC #207) — Cycle detection in directed graph / topological sort
   - Key insight: Build a dependency graph. If a cycle exists, the schedule is impossible. Use Kahn's algorithm or DFS with three-color marking.
   - Time: O(V + E), Space: O(V + E)

4. **Kth Largest Element in an Array** (LC #215) — Quickselect or heap
   - Key insight: Quickselect gives O(n) average. Alternatively, min-heap of size k gives O(n log k).
   - Time: O(n) average with quickselect

5. **Merge K Sorted Lists** (LC #23) — Heap-based merge
   - Key insight: Use a min-heap of size K. Always extract the smallest head, push the next element from that list.
   - Time: O(N log K)

6. **Binary Tree Level Order Traversal** (LC #102) — BFS
   - Key insight: Use a queue. Process level by level — track level size before processing.
   - Time: O(n), Space: O(n)

### Practice Tips
- For tree problems, always consider: What information do I need from the subtrees? (Thinking recursively)
- For graph problems, always ask: Is it directed or undirected? Weighted or unweighted? Can it have cycles?
- Know when to use BFS (shortest path in unweighted, level-order) vs DFS (cycle detection, topological sort, exhaustive search)
- Practice both recursive and iterative tree traversals
