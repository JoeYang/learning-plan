# Topic: C++ for Financial Trading Systems

## Why I Want to Learn This
Understand how production trading systems are designed in C++, the architectural tradeoffs, and when/why specific patterns are used.

## Current Knowledge Level
Beginner-to-intermediate. I've built a CME MDP 3.0 feed handler with binary protocol parsing, order books, recovery state machines, and performance-conscious patterns (flat arrays, dirty bitmasks, preallocated buffers). But my code is single-threaded with no templates, lock-free structures, or custom allocators.

## Goal
Be able to reason about trading system architecture decisions — why components are built certain ways, what the tradeoffs are, and what the limitations of each approach are. Broad survey across low-latency architecture, the full trading stack, and C++ patterns used in trading. Understanding system design, tradeoffs, and limitations — not battling the compiler.

## Resources
Curated mix of talks, papers, blog posts, and open-source repos (see learning plan for full list):
- CppCon talks: David Gross, Carl Cook, Chandler Carruth, Timur Doumler, Fedor Pikus
- ACCU talk: Jason McGuiness on templated meta-state machines
- Blog posts: Stacy Gaudreau HFT series, cppforquants.com, Erik Rigtorp, Databento, lambdafunc
- Papers: Bilokon & Gunduz (benchmarked lock-free patterns)
- Books: Ghosh "Building Low Latency Applications with C++", Johnson "Algorithmic Trading and DMA"
- Open-source repos: rigtorp/SPSCQueue, rigtorp/MPMCQueue, Liquibook, CppTrader, NUMA-aware matching engine

## Time Estimate
24 days at 1 hour/day (~4-5 weeks)

## Priority
high
