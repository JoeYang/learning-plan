# Learning Plan: C++ for Financial Trading Systems

**Start date:** 2026-02-09
**Target completion:** 2026-03-22
**Schedule:** Daily, 1 hour each
**Status:** in-progress

---

## Phase 1: Architecture & Why C++ (Days 1-4)

### Day 1: The Trading System Stack
**Objective:** Map the components of a trading system and understand what each does
- [ ] Read Stacy Gaudreau blog Part 1 (intro to HFT system components)
- [ ] Study a full-stack architecture diagram: market data → strategy → OMS → execution → risk
- [ ] Notes: sketch the stack, label what each component does and its latency budget
**Key concepts:** Trading system components, latency budgets, data flow
**Resources:** Stacy Gaudreau HFT blog series (Part 1)

### Day 2: Why C++ Dominates Trading (CppCon 2024 Keynote)
**Objective:** Understand the architectural principles behind low-latency system design
- [ ] Watch David Gross "When Nanoseconds Matter" (first 30 min)
- [ ] Notes: list the architectural principles — why low latency must be designed in, not bolted on
**Key concepts:** Latency as architecture, deterministic execution, C++ advantages for trading
**Resources:** CppCon 2024 — David Gross keynote

### Day 3: The Critical Path (CppCon 2017)
**Objective:** Distinguish hot path from cold path and what C++ choices matter on each
- [ ] Watch Carl Cook "When a Microsecond Is an Eternity"
- [ ] Notes: define "hot path" vs "cold path", list the specific C++ choices that matter on each
**Key concepts:** Hot path vs cold path, critical path optimization, latency measurement
**Resources:** CppCon 2017 — Carl Cook

### Day 4: Trading System Design Decisions
**Objective:** Synthesize architectural perspectives and identify common themes
- [ ] Finish David Gross 2024 keynote (remaining ~30 min)
- [ ] Read Ghosh "Building Low Latency Applications with C++" — Chapter 1 (architecture overview) via GitHub companion repo
- [ ] Notes: compare Gross's and Cook's approaches, identify common themes
**Key concepts:** Architecture patterns, design principles, common themes across practitioners
**Resources:** CppCon 2024 keynote (remainder), Ghosh Ch1

---

## Phase 2: Memory & Data Layout (Days 5-8)

### Day 5: Cache-Friendly Design
**Objective:** Understand why data layout matters more than algorithmic complexity at small N
- [ ] Watch Chandler Carruth "Efficiency with Algorithms, Performance with Data Structures" (CppCon 2014, first 30 min)
- [ ] Notes: why cache locality beats algorithmic complexity for small N, implications for order book design
**Key concepts:** Cache lines, spatial/temporal locality, data-oriented design, struct-of-arrays vs array-of-structs
**Resources:** CppCon 2014 — Chandler Carruth

### Day 6: Memory Allocation in Trading
**Objective:** Catalog allocation strategies and understand why malloc is forbidden on the hot path
- [ ] Read "Memory Management in HFT" (cppforquants.com)
- [ ] Study pool allocators and arena allocators — why malloc is forbidden on the hot path
- [ ] Notes: catalog allocation strategies and when each is used
**Key concepts:** Pool allocators, arena allocators, slab allocation, pre-allocation, malloc latency spikes
**Resources:** cppforquants.com

### Day 7: Data-Oriented Design for Order Books
**Objective:** Compare order book data structure approaches and their tradeoffs
- [ ] Finish Carruth 2014 talk + skim Carruth 2016 "Hybrid Data Structures"
- [ ] Compare your CmeOrderBook (flat arrays + memmove) to alternatives: map-based, vector-based, hybrid
- [ ] Notes: tradeoff table for each order book data structure approach
**Key concepts:** Order book data structures, flat arrays vs maps vs hybrids, insertion/deletion tradeoffs
**Resources:** CppCon 2014/2016 — Chandler Carruth

### Day 8: The Standard Library Minefield
**Objective:** Know which std:: features are safe on the hot path and which are not
- [ ] Watch Timur Doumler "Real-time Programming with the C++ Standard Library" (CppCon 2021)
- [ ] Notes: list which std:: features are safe on the hot path, which are not, and why
**Key concepts:** Allocation-free std:: containers, std::string SSO, std::function overhead, exceptions
**Resources:** CppCon 2021 — Timur Doumler

---

## Phase 3: Lock-Free & Concurrency (Days 9-12)

### Day 9: Lock-Free Fundamentals
**Objective:** Understand lock-free queues, false sharing, and cache line padding
- [ ] Read Erik Rigtorp's ring buffer optimization blog post
- [ ] Study SPSCQueue source code (rigtorp/SPSCQueue) — it's ~200 lines
- [ ] Notes: why lock-free matters, how false sharing works, cache line padding
**Key concepts:** Lock-free programming, SPSC queues, false sharing, cache line padding, memory ordering
**Resources:** Erik Rigtorp blog + rigtorp/SPSCQueue

### Day 10: Producer-Consumer Patterns
**Objective:** Compare SPSC and MPMC patterns and understand when each applies
- [ ] Study MPMCQueue source (rigtorp/MPMCQueue)
- [ ] Read the Disruptor pattern section from Bilokon & Gunduz paper (Section 3)
- [ ] Notes: SPSC vs MPMC tradeoffs, when each is appropriate in a trading system
**Key concepts:** MPMC queues, Disruptor pattern, producer-consumer topologies, backpressure
**Resources:** rigtorp/MPMCQueue, Bilokon & Gunduz paper (Section 3)

### Day 11: Threading Models in Trading
**Objective:** Compare threading architectures used in trading systems
- [ ] Read Ghosh book Chapter on threading (via GitHub repo) or Gaudreau blog Part 2 (building blocks)
- [ ] Study thread-per-component vs event-loop vs thread-pool architectures
- [ ] Notes: diagram which threads handle which components in a typical trading system
**Key concepts:** Thread-per-component, event loops, thread pools, thread affinity, CPU pinning
**Resources:** Ghosh threading chapter or Gaudreau Part 2

### Day 12: Concurrency Tradeoffs Review
**Objective:** Apply concurrency concepts to your own feed handler design
- [ ] Read the Bilokon & Gunduz paper Sections 1-2 (benchmarked patterns, cache warming, constexpr)
- [ ] Revisit your single-threaded feed handler — where would you add threads? What would you keep single-threaded?
- [ ] Notes: write a "redesign proposal" for your feed handler with concurrency
**Key concepts:** Concurrency design decisions, single-threaded vs multi-threaded tradeoffs, cache warming
**Resources:** Bilokon & Gunduz paper (Sections 1-2)

---

## Phase 4: Networking & I/O (Days 13-16)

### Day 13: Kernel Bypass — Why and How
**Objective:** Understand kernel bypass techniques and their tradeoffs
- [ ] Read Databento "What is kernel bypass?" guide
- [ ] Read "Kernel Bypass Techniques in Linux for HFT" (lambdafunc blog)
- [ ] Notes: compare DPDK vs OpenOnload vs raw sockets, tradeoff table
**Key concepts:** Kernel bypass, DPDK, OpenOnload, Solarflare, AF_XDP, raw sockets
**Resources:** Databento guide, lambdafunc blog

### Day 14: Zero-Copy and io_uring
**Objective:** Understand io_uring and how it compares to kernel bypass approaches
- [ ] Read io_uring zero-copy networking kernel docs + LWN article
- [ ] Notes: how io_uring compares to DPDK, when each is appropriate, what you give up
**Key concepts:** io_uring, zero-copy networking, submission/completion queues, syscall batching
**Resources:** Kernel docs, LWN articles on io_uring

### Day 15: FPGA vs Software
**Objective:** Understand when FPGAs beat software and when they don't
- [ ] Read "The Microsecond Wars" (Bangotra article on FPGA vs C++ tradeoffs)
- [ ] Notes: FPGA latency floor (~300ns) vs software floor (~10μs), development velocity tradeoff, when each makes sense
**Key concepts:** FPGA latency, hardware vs software tradeoffs, development velocity, flexibility
**Resources:** Bangotra "The Microsecond Wars"

### Day 16: Networking Architecture Review
**Objective:** Map your feed handler against the kernel bypass spectrum and identify improvements
- [ ] Revisit your feed handler's multicast receiver — map it against the kernel bypass spectrum
- [ ] Study the NUMA-aware matching engine repo's UDP busy polling approach
- [ ] Notes: where does your current design sit? What would you change for 10x lower latency?
**Key concepts:** Network architecture decisions, busy polling, NUMA awareness, latency spectrum
**Resources:** NUMA-aware matching engine repo

---

## Phase 5: Trading Components Deep Dives (Days 17-21)

### Day 17: Matching Engine Architecture
**Objective:** Understand matching engine design and how it differs from feed handler order books
- [ ] Study Liquibook source — focus on the order book data structure and matching algorithm
- [ ] Notes: how it differs from your CmeOrderBook, why a matching engine's book has different requirements than a feed handler's book
**Key concepts:** Price-time priority, matching algorithms, order types, execution reports
**Resources:** Liquibook source code

### Day 18: Matching Engine Optimization
**Objective:** Compare matching engine implementations and their optimization strategies
- [ ] Study CppTrader matching engine — compare its design choices to Liquibook
- [ ] Read the NUMA-aware matching engine repo's README and key source files
- [ ] Notes: what does each project optimize for? Which tradeoffs does each make?
**Key concepts:** NUMA-aware design, cache optimization, matching engine benchmarks
**Resources:** CppTrader, NUMA-aware matching engine repo

### Day 19: Order Management & Execution
**Objective:** Understand OMS design, order lifecycle, and venue routing
- [ ] Read Johnson "Algorithmic Trading and DMA" summary/key chapters (or detailed review)
- [ ] Study OMS design: order lifecycle, state machines, risk checks, venue routing
- [ ] Notes: sketch an OMS state machine, list where C++ performance matters vs where it doesn't
**Key concepts:** Order lifecycle, OMS state machines, venue routing, smart order routing
**Resources:** Johnson "Algorithmic Trading and DMA"

### Day 20: Risk Systems & Guardrails
**Objective:** Understand pre-trade risk checks and what happens without them
- [ ] Study pre-trade risk check patterns: position limits, order rate limits, fat-finger checks
- [ ] Read about the Knight Capital incident as a case study in what happens without guardrails
- [ ] Notes: which risk checks must be on the hot path? Which can be async?
**Key concepts:** Pre-trade risk, position limits, rate limits, fat-finger checks, Knight Capital
**Resources:** Knight Capital post-mortems, risk system design articles

### Day 21: Market Data Architecture
**Objective:** Design a multi-venue market data system and identify key architectural decisions
- [ ] Study CppTrader's ITCH handler — compare parsing patterns to your CME handler
- [ ] Read about conflation, sequencing, and normalization across venues
- [ ] Notes: design a multi-venue market data system on paper — what are the key decisions?
**Key concepts:** ITCH protocol, conflation, sequencing, venue normalization, market data fan-out
**Resources:** CppTrader ITCH handler

---

## Phase 6: Advanced Patterns & Synthesis (Days 22-24)

### Day 22: Template Metaprogramming for Trading
**Objective:** Understand when template metaprogramming is worth the complexity in trading
- [ ] Watch/read Jason McGuiness "Templated Meta-State Machines in HFT" (ACCU 2023)
- [ ] Notes: when does template metaprogramming pay off in trading? When is it over-engineering?
**Key concepts:** CRTP, policy-based design, compile-time dispatch, template state machines
**Resources:** ACCU 2023 — Jason McGuiness

### Day 23: Branchless Programming & Hot Path Optimization
**Objective:** Catalog branchless techniques and identify where they apply
- [ ] Watch Fedor Pikus "Branchless Programming in C++" (CppCon 2021)
- [ ] Notes: catalog branchless techniques, identify where they'd apply in your feed handler
**Key concepts:** Branch prediction, branchless techniques, CMOV, lookup tables, bit manipulation
**Resources:** CppCon 2021 — Fedor Pikus

### Day 24: Capstone — Architecture Your Own System
**Objective:** Synthesize everything into a complete system design
- [ ] Design a complete trading system on paper: market data → strategy → OMS → execution
- [ ] For each component, document: data structures, threading model, allocation strategy, networking approach
- [ ] Write a 1-page "architecture decision record" explaining your choices and their tradeoffs
**Key concepts:** System design synthesis, architecture decision records, tradeoff documentation
**Resources:** All previous materials
